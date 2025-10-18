"""
Algorithm: Smooth Contours from Raster
Provider: Custom
"""

from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsRasterLayer,
                       QgsVectorLayer,
                       QgsGeometry,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes)
from qgis.PyQt.QtCore import QVariant
import processing
import numpy as np
from scipy import ndimage
import tempfile
import os

class SmoothContoursFromRaster(QgsProcessingAlgorithm):
    """
    Algoritmo para extrair contornos suaves a partir de raster
    """

    # Constants
    INPUT_RASTER = 'INPUT_RASTER'
    INTERVAL = 'INTERVAL'
    SMOOTH_ITERATIONS = 'SMOOTH_ITERATIONS'
    SMOOTH_METHOD = 'SMOOTH_METHOD'
    SIMPLIFY_TOLERANCE = 'SIMPLIFY_TOLERANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        # Input raster
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                'Raster de entrada'
            )
        )

        # Intervalo de contorno
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INTERVAL,
                'Intervalo entre curvas de nível',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                minValue=0.1
            )
        )

        # Método de suavização
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SMOOTH_METHOD,
                'Método de suavização',
                options=['Gaussian', 'Median', 'Mean'],
                defaultValue=0
            )
        )

        # Iterações de suavização
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SMOOTH_ITERATIONS,
                'Grau de suavização',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=2,
                minValue=1,
                maxValue=10
            )
        )

        # Tolerância de simplificação
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIMPLIFY_TOLERANCE,
                'Tolerância de simplificação',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1.0,
                minValue=0.0,
                optional=True
            )
        )

        # Output
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Contornos suaves'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Get parameters
        raster_layer = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        interval = self.parameterAsDouble(parameters, self.INTERVAL, context)
        smooth_method = self.parameterAsInt(parameters, self.SMOOTH_METHOD, context)
        smooth_iterations = self.parameterAsInt(parameters, self.SMOOTH_ITERATIONS, context)
        simplify_tolerance = self.parameterAsDouble(parameters, self.SIMPLIFY_TOLERANCE, context)

        feedback.pushInfo("Iniciando extração de contornos suaves...")

        # Step 1: Get raster statistics to determine contour range
        band_stats = raster_layer.dataProvider().bandStatistics(1)
        min_val = band_stats.minimumValue
        max_val = band_stats.maximumValue
        
        # Calculate contour levels
        contour_levels = []
        current_level = min_val + (interval - (min_val % interval)) if min_val % interval != 0 else min_val
        while current_level <= max_val:
            contour_levels.append(current_level)
            current_level += interval

        feedback.pushInfo(f"Gerando {len(contour_levels)} níveis de contorno de {min_val} a {max_val}")

        # Step 2: Create temporary smoothed raster
        feedback.pushInfo("Aplicando suavização no raster...")
        
        # Export raster to temporary file for processing
        temp_raster = os.path.join(tempfile.gettempdir(), 'temp_raster.tif')
        processing.run("gdal:translate", {
            'INPUT': raster_layer,
            'TARGET_CRS': raster_layer.crs(),
            'OUTPUT': temp_raster
        }, context=context, feedback=feedback)

        # Step 3: Apply smoothing using GDAL
        smoothed_raster = os.path.join(tempfile.gettempdir(), 'smoothed_raster.tif')
        
        if smooth_method == 0:  # Gaussian
            processing.run("gdal:fillnodata", {
                'INPUT': temp_raster,
                'BAND': 1,
                'DISTANCE': 10,
                'ITERATIONS': smooth_iterations,
                'OUTPUT': smoothed_raster
            }, context=context, feedback=feedback)
        elif smooth_method == 1:  # Median
            processing.run("gdal:sievecallback", {
                'INPUT': temp_raster,
                'BAND': 1,
                'MASK': None,
                'COMPUTE_EDGES': True,
                'LEVEL': smooth_iterations,
                'OUTPUT': smoothed_raster
            }, context=context, feedback=feedback)
        else:  # Mean
            processing.run("gdal:fillnodata", {
                'INPUT': temp_raster,
                'BAND': 1,
                'DISTANCE': 5 * smooth_iterations,
                'ITERATIONS': 1,
                'OUTPUT': smoothed_raster
            }, context=context, feedback=feedback)

        # Step 4: Generate contours from smoothed raster
        feedback.pushInfo("Gerando contornos do raster suavizado...")
        
        temp_contours = os.path.join(tempfile.gettempdir(), 'temp_contours.gpkg')
        
        processing.run("gdal:contour", {
            'INPUT': smoothed_raster,
            'BAND': 1,
            'INTERVAL': interval,
            'FIELD_NAME': 'ELEV',
            'CREATE_3D': False,
            'IGNORE_NODATA': True,
            'NODATA': band_stats.noDataValue if band_stats.noDataValue else -9999,
            'OFFSET': 0,
            'EXTRA': '',
            'OUTPUT': temp_contours
        }, context=context, feedback=feedback)

        # Step 5: Load contours and apply additional smoothing
        contours_layer = QgsVectorLayer(temp_contours, 'temp_contours', 'ogr')
        
        if not contours_layer.isValid():
            feedback.reportError("Erro ao carregar contornos temporários")
            return {}

        # Define output fields
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("elevation", QVariant.Double))
        fields.append(QgsField("original_id", QVariant.Int))

        # Create output sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.LineString,
            raster_layer.crs()
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Process features with smoothing
        total_features = contours_layer.featureCount()
        feedback.pushInfo(f"Aplicando suavização final em {total_features} feições...")

        for current, feature in enumerate(contours_layer.getFeatures()):
            if feedback.isCanceled():
                break

            geometry = feature.geometry()
            if not geometry.isEmpty():
                # Smooth the geometry
                smoothed_geometry = self.smooth_geometry(geometry, smooth_iterations)
                
                # Simplify if tolerance is specified
                if simplify_tolerance > 0:
                    smoothed_geometry = smoothed_geometry.simplify(simplify_tolerance)
                
                # Create new feature
                new_feature = QgsFeature(fields)
                new_feature.setGeometry(smoothed_geometry)
                new_feature.setAttribute("id", current)
                new_feature.setAttribute("elevation", feature.attribute("ELEV"))
                new_feature.setAttribute("original_id", feature.id())
                
                sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total_features))

        # Clean up temporary files
        try:
            os.remove(temp_raster)
            os.remove(smoothed_raster)
            os.remove(temp_contours)
        except:
            pass

        feedback.pushInfo("Processamento concluído!")
        return {self.OUTPUT: dest_id}

    def smooth_geometry(self, geometry, iterations):
        """
        Apply smoothing to a geometry using Chaikin's algorithm
        """
        if geometry.isMultipart():
            parts = geometry.asMultiPolyline()
            smoothed_parts = []
            for part in parts:
                smoothed_part = self.chaikin_smooth(part, iterations)
                smoothed_parts.append(smoothed_part)
            return QgsGeometry.fromMultiPolylineXY(smoothed_parts)
        else:
            line = geometry.asPolyline()
            smoothed_line = self.chaikin_smooth(line, iterations)
            return QgsGeometry.fromPolylineXY(smoothed_line)

    def chaikin_smooth(self, line, iterations):
        """
        Chaikin's smoothing algorithm for lines
        """
        if len(line) < 3:
            return line

        smoothed = line
        for _ in range(iterations):
            new_line = [smoothed[0]]  # Keep first point
            for i in range(len(smoothed) - 1):
                p0 = smoothed[i]
                p1 = smoothed[i + 1]
                
                # Calculate quarter points
                q0 = QgsPointXY(
                    p0.x() * 0.75 + p1.x() * 0.25,
                    p0.y() * 0.75 + p1.y() * 0.25
                )
                q1 = QgsPointXY(
                    p0.x() * 0.25 + p1.x() * 0.75,
                    p0.y() * 0.25 + p1.y() * 0.75
                )
                
                new_line.extend([q0, q1])
            
            new_line.append(smoothed[-1])  # Keep last point
            smoothed = new_line
        
        return smoothed

    def name(self):
        return 'smoothcontoursfromraster'

    def displayName(self):
        return 'Contornos Suaves a partir de Raster'

    def group(self):
        return 'Custom'

    def groupId(self):
        return 'custom'

    def createInstance(self):
        return SmoothContoursFromRaster()