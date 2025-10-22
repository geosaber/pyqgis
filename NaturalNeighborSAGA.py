"""
Script de interpolação por Vizinhos Naturais usando SAGA
"""

from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterExtent)
import processing


class NaturalNeighborSAGA(QgsProcessingAlgorithm):
    """
    Interpolação por Vizinhos Naturais usando SAGA
    """

    INPUT = 'INPUT'
    Z_FIELD = 'Z_FIELD'
    OUTPUT = 'OUTPUT'
    PIXEL_SIZE = 'PIXEL_SIZE'
    EXTENT = 'EXTENT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Camada de pontos',
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.Z_FIELD,
                'Campo Z',
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.PIXEL_SIZE,
                'Tamanho do pixel',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=100.0
            )
        )

        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                'Extensão'
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                'Raster de saída'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        z_field = self.parameterAsString(parameters, self.Z_FIELD, context)
        pixel_size = self.parameterAsDouble(parameters, self.PIXEL_SIZE, context)
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        # Usar algoritmo SAGA para Natural Neighbor
        alg_params = {
            'SHAPES': parameters[self.INPUT],
            'FIELD': z_field,
            'TARGET_USER_SIZE': pixel_size,
            'TARGET_USER_XMIN': extent.xMinimum(),
            'TARGET_USER_XMAX': extent.xMaximum(),
            'TARGET_USER_YMIN': extent.yMinimum(),
            'TARGET_USER_YMAX': extent.yMaximum(),
            'TARGET_OUT_GRID': output
        }

        result = processing.run("saga:naturalneighbour", 
                              alg_params, 
                              context=context, 
                              feedback=feedback)

        return {self.OUTPUT: result['TARGET_OUT_GRID']}

    def name(self):
        return 'naturalneighborsaga'

    def displayName(self):
        return 'Interpolação Vizinhos Naturais (SAGA)'

    def createInstance(self):
        return NaturalNeighborSAGA()


def classFactory(interface):
    return NaturalNeighborSAGA()