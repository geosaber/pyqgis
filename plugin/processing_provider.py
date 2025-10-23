# -*- coding: utf-8 -*-

"""
Processing algorithm provider for Enhanced Trend Surface Analysis
"""

import os
from qgis.core import (QgsProcessingProvider,
                       QgsMessageLog,
                       Qgis)
from .enhanced_trend_surface_algorithm import EnhancedTrendSurfaceAlgorithm

class EnhancedTrendSurfaceProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()

    def getAlgs(self):
        algs = [
            EnhancedTrendSurfaceAlgorithm()
        ]
        return algs

    def id(self):
        return 'enhancedtrendsurface'

    def name(self):
        return 'Enhanced Trend Surface'

    def icon(self):
        return None

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def load(self):
        self.loadAlgorithms()
        return True
