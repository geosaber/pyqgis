# -*- coding: utf-8 -*-
"""
Dialog for Enhanced Trend Surface Analysis - Programmatic Version
"""

from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                                 QFormLayout, QLabel, QComboBox, QSpinBox, 
                                 QDoubleSpinBox, QCheckBox, QTextEdit, 
                                 QPushButton)
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapLayerComboBox, QgsFileWidget
from qgis.core import QgsMapLayerProxyModel

class TrendSurfaceDialog(QDialog):
    def __init__(self):
        super(TrendSurfaceDialog, self).__init__()
        self.setWindowTitle("Enhanced Trend Surface Analysis")
        self.setMinimumSize(600, 700)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Input Parameters Group
        input_group = QGroupBox("Input Parameters")
        input_layout = QFormLayout(input_group)
        
        self.inputLayerCombo = QgsMapLayerComboBox()
        self.inputLayerCombo.setFilters(QgsMapLayerProxyModel.PointLayer)
        input_layout.addRow(QLabel("Input Point Layer:"), self.inputLayerCombo)
        
        self.zFieldCombo = QComboBox()
        input_layout.addRow(QLabel("Z Value Field:"), self.zFieldCombo)
        
        self.weightFieldCombo = QComboBox()
        self.weightFieldCombo.addItem("")  # Empty option for no weight
        input_layout.addRow(QLabel("Weight Field (optional):"), self.weightFieldCombo)
        
        self.polynomialSpin = QSpinBox()
        self.polynomialSpin.setRange(1, 8)
        self.polynomialSpin.setValue(2)
        input_layout.addRow(QLabel("Polynomial Degree:"), self.polynomialSpin)
        
        self.cellSizeSpin = QDoubleSpinBox()
        self.cellSizeSpin.setRange(0.1, 10000.0)
        self.cellSizeSpin.setValue(100.0)
        self.cellSizeSpin.setDecimals(1)
        input_layout.addRow(QLabel("Cell Size:"), self.cellSizeSpin)
        
        self.confidenceSpin = QDoubleSpinBox()
        self.confidenceSpin.setRange(80.0, 99.9)
        self.confidenceSpin.setValue(95.0)
        self.confidenceSpin.setDecimals(1)
        input_layout.addRow(QLabel("Confidence Level (%):"), self.confidenceSpin)
        
        layout.addWidget(input_group)
        
        # Analysis Options Group
        options_group = QGroupBox("Analysis Options")
        options_layout = QVBoxLayout(options_group)
        
        self.crossValidationCheck = QCheckBox("Perform Cross-Validation")
        self.crossValidationCheck.setChecked(False)
        options_layout.addWidget(self.crossValidationCheck)
        
        self.robustRegressionCheck = QCheckBox("Use Robust Regression (outlier resistant)")
        self.robustRegressionCheck.setChecked(False)
        options_layout.addWidget(self.robustRegressionCheck)
        
        layout.addWidget(options_group)
        
        # Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)
        
        self.trendOutputWidget = QgsFileWidget()
        self.trendOutputWidget.setFilter("Tiff files (*.tif *.tiff)")
        self.trendOutputWidget.setStorageMode(QgsFileWidget.SaveFile)
        output_layout.addRow(QLabel("Trend Surface:"), self.trendOutputWidget)
        
        self.residualsOutputWidget = QgsFileWidget()
        self.residualsOutputWidget.setFilter("Tiff files (*.tif *.tiff)")
        self.residualsOutputWidget.setStorageMode(QgsFileWidget.SaveFile)
        output_layout.addRow(QLabel("Residuals Surface (optional):"), self.residualsOutputWidget)
        
        self.confidenceOutputWidget = QgsFileWidget()
        self.confidenceOutputWidget.setFilter("Tiff files (*.tif *.tiff)")
        self.confidenceOutputWidget.setStorageMode(QgsFileWidget.SaveFile)
        output_layout.addRow(QLabel("Confidence Intervals (optional):"), self.confidenceOutputWidget)
        
        self.folderOutputWidget = QgsFileWidget()
        self.folderOutputWidget.setStorageMode(QgsFileWidget.GetDirectory)
        output_layout.addRow(QLabel("Statistics Folder (optional):"), self.folderOutputWidget)
        
        layout.addWidget(output_group)
        
        # Info Text
        self.infoText = QTextEdit()
        self.infoText.setHtml("""
        <p style="font-size:8pt;">Enhanced Trend Surface Analysis uses polynomial regression to model spatial trends. Features include:</p>
        <ul style="font-size:8pt;">
        <li>Multiple polynomial degrees (1-8)</li>
        <li>Robust regression for outlier resistance</li>
        <li>Cross-validation and confidence intervals</li>
        <li>Comprehensive statistical diagnostics</li>
        </ul>
        """)
        self.infoText.setReadOnly(True)
        layout.addWidget(self.infoText)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.runButton = QPushButton("Run Analysis")
        self.closeButton = QPushButton("Close")
        
        button_layout.addWidget(self.runButton)
        button_layout.addStretch()
        button_layout.addWidget(self.closeButton)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.closeButton.clicked.connect(self.close)