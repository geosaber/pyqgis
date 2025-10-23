# -*- coding: utf-8 -*-

"""
Script to generate trend surface from point data
"""

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterExtent,
                       QgsProcessingUtils,
                       QgsFields, QgsField, QgsFeature,
                       QgsGeometry, QgsPointXY,
                       QgsRasterLayer, QgsCoordinateReferenceSystem,
                       QgsProcessingException)
import numpy as np
from osgeo import gdal, osr
import tempfile
import os


class TrendSurfaceAlgorithm(QgsProcessingAlgorithm):
    """
    Algorithm to generate polynomial trend surface
    """

    # Input parameters
    INPUT = 'INPUT'
    Z_FIELD = 'Z_FIELD'
    POLYNOMIAL = 'POLYNOMIAL'
    CELL_SIZE = 'CELL_SIZE'
    EXTENT = 'EXTENT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        # Input point layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input point layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Z value field
        self.addParameter(
            QgsProcessingParameterField(
                self.Z_FIELD,
                self.tr('Z value field'),
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT,
                allowMultiple=False
            )
        )

        # Polynomial degree
        self.addParameter(
            QgsProcessingParameterNumber(
                self.POLYNOMIAL,
                self.tr('Polynomial degree'),
                type=QgsProcessingParameterNumber.Integer,
                minValue=1,
                maxValue=5,
                defaultValue=1
            )
        )

        # Cell size
        self.addParameter(
            QgsProcessingParameterNumber(
                self.CELL_SIZE,
                self.tr('Cell size'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.1,
                defaultValue=100.0
            )
        )

        # Extent
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Output extent'),
                optional=True
            )
        )

        # Output raster
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Trend surface raster')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Get parameters
        source = self.parameterAsSource(parameters, self.INPUT, context)
        z_field = self.parameterAsString(parameters, self.Z_FIELD, context)
        polynomial_degree = self.parameterAsInt(parameters, self.POLYNOMIAL, context)
        cell_size = self.parameterAsDouble(parameters, self.CELL_SIZE, context)
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Collect points and values
        points = []
        z_values = []
        total_features = source.featureCount()
        
        feedback.pushInfo(f"Collecting {total_features} points...")

        for i, feature in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break
                
            if i % 100 == 0:
                feedback.setProgress(int(i / total_features * 50))
                
            geometry = feature.geometry()
            if geometry.isMultipart():
                points.extend([p for p in geometry.asMultiPoint()])
                z_values.extend([feature[z_field]] * len(geometry.asMultiPoint()))
            else:
                point = geometry.asPoint()
                points.append((point.x(), point.y()))
                z_values.append(feature[z_field])

        if len(points) < 3:
            raise QgsProcessingException("Insufficient points to generate trend surface")

        # Convert to numpy arrays
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        z = np.array(z_values)

        feedback.pushInfo(f"Points collected: {len(points)}")
        feedback.pushInfo(f"Fitting polynomial of degree {polynomial_degree}...")

        # Fit polynomial trend surface using least squares
        try:
            coefficients = self.fit_polynomial_surface(x, y, z, polynomial_degree, feedback)
        except Exception as e:
            raise QgsProcessingException(f"Error in polynomial fitting: {str(e)}")

        # Define extent and resolution
        if extent.isNull():
            xmin, xmax = np.min(x), np.max(x)
            ymin, ymax = np.min(y), np.max(y)
        else:
            xmin, xmax = extent.xMinimum(), extent.xMaximum()
            ymin, ymax = extent.yMinimum(), extent.yMaximum()

        # Calculate raster dimensions
        cols = int((xmax - xmin) / cell_size) + 1
        rows = int((ymax - ymin) / cell_size) + 1

        feedback.pushInfo(f"Raster dimensions: {cols} x {rows}")
        feedback.pushInfo(f"Extent: X({xmin:.2f}, {xmax:.2f}) Y({ymin:.2f}, {ymax:.2f})")

        # Create raster
        driver = gdal.GetDriverByName('GTiff')
        out_raster = driver.Create(output_path, cols, rows, 1, gdal.GDT_Float32)
        
        # Set geotransform
        geotransform = (xmin, cell_size, 0, ymax, 0, -cell_size)
        out_raster.SetGeoTransform(geotransform)

        # Set CRS
        crs = source.sourceCrs()
        if crs.isValid():
            srs = osr.SpatialReference()
            srs.ImportFromWkt(crs.toWkt())
            out_raster.SetProjection(srs.ExportToWkt())

        # Fill raster with trend surface values
        band = out_raster.GetRasterBand(1)
        band.SetNoDataValue(-9999)

        feedback.setProgress(60)
        feedback.pushInfo("Generating trend surface raster...")

        # Calculate values for each cell
        raster_data = np.zeros((rows, cols), dtype=np.float32)
        
        for row in range(rows):
            if feedback.isCanceled():
                break
                
            if row % 100 == 0:
                feedback.setProgress(60 + int(row / rows * 35))
                
            y_val = ymax - row * cell_size
            for col in range(cols):
                x_val = xmin + col * cell_size
                raster_data[row, col] = self.evaluate_polynomial(x_val, y_val, coefficients, polynomial_degree)

        band.WriteArray(raster_data)
        band.FlushCache()
        
        out_raster = None  # Close file

        feedback.setProgress(100)
        feedback.pushInfo("Trend surface generated successfully!")

        return {self.OUTPUT: output_path}

    def fit_polynomial_surface(self, x, y, z, degree, feedback):
        """Fit polynomial surface to points using least squares regression"""
        # Create design matrix
        A = []
        for i in range(len(x)):
            row = []
            for d in range(degree + 1):
                for j in range(d + 1):
                    row.append(x[i] ** (d - j) * y[i] ** j)
            A.append(row)
        
        A = np.array(A)
        
        # Solve linear system using least squares
        coefficients, residuals, rank, s = np.linalg.lstsq(A, z, rcond=None)
        
        feedback.pushInfo(f"Fit residuals: {residuals[0]:.4f}" if len(residuals) > 0 else "Fit completed")
        
        return coefficients

    def evaluate_polynomial(self, x, y, coefficients, degree):
        """Evaluate polynomial at x, y coordinates"""
        value = 0
        idx = 0
        for d in range(degree + 1):
            for j in range(d + 1):
                value += coefficients[idx] * (x ** (d - j)) * (y ** j)
                idx += 1
        return value

    def name(self):
        return 'trendsurface'

    def displayName(self):
        return self.tr('Trend Surface')

    def group(self):
        return self.tr('Surface Analysis')

    def groupId(self):
        return 'surfaceanalysis'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TrendSurfaceAlgorithm()


def classFactory(iface):
    return TrendSurfaceAlgorithm()
