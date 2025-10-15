# -*- coding: utf-8 -*-

"""
Script para gerar superfície de tendência a partir de pontos
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
    Algoritmo para gerar superfície de tendência
    """

    # Parâmetros de entrada
    INPUT = 'INPUT'
    Z_FIELD = 'Z_FIELD'
    POLYNOMIAL = 'POLYNOMIAL'
    CELL_SIZE = 'CELL_SIZE'
    EXTENT = 'EXTENT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        # Camada de entrada de pontos
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Camada de pontos de entrada'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Campo Z (valor)
        self.addParameter(
            QgsProcessingParameterField(
                self.Z_FIELD,
                self.tr('Campo Z (valor)'),
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT,
                allowMultiple=False
            )
        )

        # Grau do polinômio
        self.addParameter(
            QgsProcessingParameterNumber(
                self.POLYNOMIAL,
                self.tr('Grau do polinômio'),
                type=QgsProcessingParameterNumber.Integer,
                minValue=1,
                maxValue=5,
                defaultValue=1
            )
        )

        # Tamanho da célula
        self.addParameter(
            QgsProcessingParameterNumber(
                self.CELL_SIZE,
                self.tr('Tamanho da célula'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.1,
                defaultValue=100.0
            )
        )

        # Extensão
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Extensão da saída'),
                optional=True
            )
        )

        # Raster de saída
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Raster de superfície de tendência')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Obter parâmetros
        source = self.parameterAsSource(parameters, self.INPUT, context)
        z_field = self.parameterAsString(parameters, self.Z_FIELD, context)
        polynomial_degree = self.parameterAsInt(parameters, self.POLYNOMIAL, context)
        cell_size = self.parameterAsDouble(parameters, self.CELL_SIZE, context)
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Coletar pontos e valores
        points = []
        z_values = []
        total_features = source.featureCount()
        
        feedback.pushInfo(f"Coletando {total_features} pontos...")

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
            raise QgsProcessingException("Número insuficiente de pontos para gerar superfície de tendência")

        # Converter para arrays numpy
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        z = np.array(z_values)

        feedback.pushInfo(f"Pontos coletados: {len(points)}")
        feedback.pushInfo(f"Ajustando polinômio de grau {polynomial_degree}...")

        # Ajustar superfície de tendência polinomial
        try:
            coefficients = self.fit_polynomial_surface(x, y, z, polynomial_degree, feedback)
        except Exception as e:
            raise QgsProcessingException(f"Erro no ajuste polinomial: {str(e)}")

        # Definir extensão e resolução
        if extent.isNull():
            xmin, xmax = np.min(x), np.max(x)
            ymin, ymax = np.min(y), np.max(y)
        else:
            xmin, xmax = extent.xMinimum(), extent.xMaximum()
            ymin, ymax = extent.yMinimum(), extent.yMaximum()

        # Calcular dimensões do raster
        cols = int((xmax - xmin) / cell_size) + 1
        rows = int((ymax - ymin) / cell_size) + 1

        feedback.pushInfo(f"Dimensões do raster: {cols} x {rows}")
        feedback.pushInfo(f"Extensão: X({xmin:.2f}, {xmax:.2f}) Y({ymin:.2f}, {ymax:.2f})")

        # Criar raster
        driver = gdal.GetDriverByName('GTiff')
        out_raster = driver.Create(output_path, cols, rows, 1, gdal.GDT_Float32)
        
        # Definir transformação geográfica
        geotransform = (xmin, cell_size, 0, ymax, 0, -cell_size)
        out_raster.SetGeoTransform(geotransform)

        # Definir SRC
        crs = source.sourceCrs()
        if crs.isValid():
            srs = osr.SpatialReference()
            srs.ImportFromWkt(crs.toWkt())
            out_raster.SetProjection(srs.ExportToWkt())

        # Preencher raster com valores da superfície de tendência
        band = out_raster.GetRasterBand(1)
        band.SetNoDataValue(-9999)

        feedback.setProgress(60)
        feedback.pushInfo("Gerando raster de superfície de tendência...")

        # Calcular valores para cada célula
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
        
        out_raster = None  # Fechar arquivo

        feedback.setProgress(100)
        feedback.pushInfo("Superfície de tendência gerada com sucesso!")

        return {self.OUTPUT: output_path}

    def fit_polynomial_surface(self, x, y, z, degree, feedback):
        """Ajusta uma superfície polinomial aos pontos"""
        # Criar matriz de design
        A = []
        for i in range(len(x)):
            row = []
            for d in range(degree + 1):
                for j in range(d + 1):
                    row.append(x[i] ** (d - j) * y[i] ** j)
            A.append(row)
        
        A = np.array(A)
        
        # Resolver sistema linear usando mínimos quadrados
        coefficients, residuals, rank, s = np.linalg.lstsq(A, z, rcond=None)
        
        feedback.pushInfo(f"Resíduos do ajuste: {residuals[0]:.4f}" if len(residuals) > 0 else "Ajuste concluído")
        
        return coefficients

    def evaluate_polynomial(self, x, y, coefficients, degree):
        """Avalia o polinômio nas coordenadas x, y"""
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
        return self.tr('Superfície de Tendência')

    def group(self):
        return self.tr('Análise de Superfície')

    def groupId(self):
        return 'surfaceanalysis'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TrendSurfaceAlgorithm()


def classFactory(iface):
    return TrendSurfaceAlgorithm()