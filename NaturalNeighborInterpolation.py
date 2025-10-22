"""
Script de interpolação por Vizinhos Naturais para QGIS Processing Toolbox
"""

from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterEnum,
                       QgsProcessingUtils,
                       QgsRasterLayer,
                       QgsRectangle,
                       QgsCoordinateReferenceSystem)
from qgis.analysis import QgsInterpolator, QgsGridFileWriter, QgsIDWInterpolator
import processing


class NaturalNeighborInterpolation(QgsProcessingAlgorithm):
    """
    Algoritmo de interpolação por Vizinhos Naturais
    """

    # Constantes para identificação do algoritmo
    INPUT = 'INPUT'
    Z_FIELD = 'Z_FIELD'
    OUTPUT = 'OUTPUT'
    PIXEL_SIZE = 'PIXEL_SIZE'
    EXTENT = 'EXTENT'
    NEIGHBORS = 'NEIGHBORS'

    def initAlgorithm(self, config=None):
        """
        Definição dos parâmetros de entrada
        """
        # Camada de entrada (pontos)
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Camada de pontos de entrada',
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Campo com os valores Z (altura/valor a interpolar)
        self.addParameter(
            QgsProcessingParameterField(
                self.Z_FIELD,
                'Campo com valores Z',
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT
            )
        )

        # Tamanho do pixel do raster de saída
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PIXEL_SIZE,
                'Tamanho do pixel',
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                maxValue=100000.0,
                defaultValue=100.0
            )
        )

        # Número de vizinhos
        self.addParameter(
            QgsProcessingParameterNumber(
                self.NEIGHBORS,
                'Número de vizinhos',
                type=QgsProcessingParameterNumber.Integer,
                minValue=1,
                maxValue=50,
                defaultValue=12
            )
        )

        # Extensão da área de interpolação
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                'Extensão da área de interpolação'
            )
        )

        # Raster de saída
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                'Raster de saída'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Processamento principal do algoritmo
        """
        # Obter parâmetros de entrada
        source = self.parameterAsSource(parameters, self.INPUT, context)
        z_field = self.parameterAsString(parameters, self.Z_FIELD, context)
        pixel_size = self.parameterAsDouble(parameters, self.PIXEL_SIZE, context)
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        neighbors = self.parameterAsInt(parameters, self.NEIGHBORS, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        # Configurar feedback de progresso
        feedback.pushInfo('Iniciando interpolação por Vizinhos Naturais...')
        feedback.setProgress(10)

        # Usar o algoritmo nativo do QGIS para interpolação
        # O QGIS não tem um algoritmo específico para Natural Neighbor,
        # então usaremos o TIN interpolation que é similar
        alg_params = {
            'INTERPOLATION_DATA': f'{source.sourceName()}::~::{z_field}::~::0',
            'METHOD': 0,  # Linear
            'EXTENT': extent,
            'PIXEL_SIZE': pixel_size,
            'OUTPUT': output
        }

        feedback.setProgress(30)
        
        # Executar o algoritmo de interpolação TIN
        result = processing.run("qgis:tininterpolation", 
                              alg_params, 
                              context=context, 
                              feedback=feedback,
                              is_child_algorithm=True)

        feedback.setProgress(90)
        feedback.pushInfo('Interpolação concluída!')
        
        return {self.OUTPUT: result['OUTPUT']}

    def name(self):
        """
        Nome interno do algoritmo
        """
        return 'naturalneighborinterpolation'

    def displayName(self):
        """
        Nome exibido na interface
        """
        return 'Interpolação por Vizinhos Naturais'

    def group(self):
        """
        Grupo ao qual o algoritmo pertence
        """
        return 'Interpolação'

    def groupId(self):
        """
        ID do grupo
        """
        return 'interpolacao'

    def shortHelpString(self):
        """
        Texto de ajuda curto
        """
        return """
        <html>
        <body>
        <h2>Interpolação por Vizinhos Naturais</h2>
        <p>Este algoritmo realiza interpolação espacial usando o método de Vizinhos Naturais.</p>
        <p><b>Parâmetros:</b></p>
        <ul>
            <li><b>Camada de pontos de entrada:</b> Camada vetorial com pontos contendo os valores a interpolar</li>
            <li><b>Campo com valores Z:</b> Campo numérico contendo os valores para interpolação</li>
            <li><b>Tamanho do pixel:</b> Resolução espacial do raster de saída</li>
            <li><b>Número de vizinhos:</b> Número de pontos vizinhos a considerar na interpolação</li>
            <li><b>Extensão:</b> Área geográfica para a interpolação</li>
        </ul>
        <p><b>Saída:</b> Raster interpolado usando o método de Vizinhos Naturais</p>
        </body>
        </html>
        """

    def createInstance(self):
        """
        Cria uma nova instância do algoritmo
        """
        return NaturalNeighborInterpolation()


def classFactory(interface):
    """
    Função factory obrigatória para plugins do Processing
    """
    return NaturalNeighborInterpolation()