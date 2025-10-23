# -*- coding: utf-8 -*-
"""
Dialog for Enhanced Trend Surface Analysis
"""

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
import os

class TrendSurfaceDialog(QDialog):
    def __init__(self):
        super(TrendSurfaceDialog, self).__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'trend_surface_dialog.ui')
        uic.loadUi(ui_path, self)
