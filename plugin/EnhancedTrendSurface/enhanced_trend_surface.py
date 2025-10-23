# -*- coding: utf-8 -*-
"""
Enhanced Trend Surface Analysis Plugin
"""

import os
from qgis.PyQt.QtCore import QCoreApplication, QTranslator, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QProgressDialog
from qgis.core import (QgsProject, QgsVectorLayer, QgsRasterLayer, 
                       QgsMessageLog, Qgis, QgsMapLayerProxyModel)
from qgis.gui import QgsMapLayerComboBox, QgsFileWidget
import processing

# Use programmatic dialog instead of .ui file
from .trend_surface_dialog import TrendSurfaceDialog

class EnhancedTrendSurfacePlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr('Enhanced Trend Surface')
        
        # Check if plugin was started the first time in current QGIS session
        self.first_start = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API."""
        return QCoreApplication.translate('EnhancedTrendSurface', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, 'icons', 'icon.png')
        
        self.add_action(
            icon_path,
            text=self.tr('Enhanced Trend Surface Analysis'),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr('Enhanced Trend Surface'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        if self.first_start == True:
            self.first_start = False
            self.dlg = TrendSurfaceDialog()
            
            # Connect signals
            self.dlg.runButton.clicked.connect(self.execute_analysis)
            self.dlg.closeButton.clicked.connect(self.dlg.close)
            self.dlg.inputLayerCombo.layerChanged.connect(self.update_field_combos)
        
        # Populate layer combos
        self.dlg.inputLayerCombo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.update_field_combos()
        
        # Show the dialog
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

    def update_field_combos(self):
        """Update field comboboxes based on selected layer"""
        layer = self.dlg.inputLayerCombo.currentLayer()
        
        if layer:
            fields = layer.fields()
            numeric_fields = [field.name() for field in fields if field.isNumeric()]
            
            # Clear and populate Z field combo
            self.dlg.zFieldCombo.clear()
            self.dlg.zFieldCombo.addItems(numeric_fields)
            
            # Clear and populate weight field combo
            self.dlg.weightFieldCombo.clear()
            self.dlg.weightFieldCombo.addItem("")  # Empty for no weight
            self.dlg.weightFieldCombo.addItems(numeric_fields)
            
            # Auto-select common field names
            for field_name in ['elevation', 'z', 'height', 'altitude', 'value']:
                if field_name in numeric_fields:
                    index = self.dlg.zFieldCombo.findText(field_name)
                    if index >= 0:
                        self.dlg.zFieldCombo.setCurrentIndex(index)
                        break

    def execute_analysis(self):
        """Execute the trend surface analysis"""
        try:
            # Get parameters from dialog
            input_layer = self.dlg.inputLayerCombo.currentLayer()
            z_field = self.dlg.zFieldCombo.currentText()
            polynomial_degree = self.dlg.polynomialSpin.value()
            cell_size = self.dlg.cellSizeSpin.value()
            
            # Validate inputs
            if not input_layer:
                QMessageBox.warning(self.dlg, "Input Error", "Please select an input point layer.")
                return
                
            if not z_field:
                QMessageBox.warning(self.dlg, "Input Error", "Please select a Z value field.")
                return

            # Get output path
            output_trend = self.dlg.trendOutputWidget.filePath()
            if not output_trend:
                QMessageBox.warning(self.dlg, "Output Error", "Please specify output trend surface file.")
                return

            # Initialize analyzer
            from .core_analysis import TrendSurfaceAnalyzer
            
            def progress_callback(message):
                QgsMessageLog.logMessage(message, "TrendSurface", Qgis.Info)
            
            analyzer = TrendSurfaceAnalyzer(progress_callback)
            
            # Perform analysis
            analysis_result = analyzer.analyze(
                input_layer, z_field, polynomial_degree, cell_size
            )
            
            # Create trend surface
            trend_path = analyzer.create_trend_surface(
                analysis_result, 
                input_layer.extent(), 
                cell_size, 
                input_layer.sourceCrs(),
                output_trend
            )
            
            # Create residual layer
            residual_layer = analyzer.create_residual_layer(
                input_layer, analysis_result['residuals'], z_field
            )
            QgsProject.instance().addMapLayer(residual_layer)
            
            # Load trend surface
            trend_layer = QgsRasterLayer(trend_path, "Trend Surface")
            if trend_layer.isValid():
                QgsProject.instance().addMapLayer(trend_layer)
                self.iface.mapCanvas().setExtent(trend_layer.extent())
                self.iface.mapCanvas().refresh()
            
            QMessageBox.information(self.dlg, "Analysis Complete", 
                                  f"Trend surface analysis completed successfully!\n\n"
                                  f"R²: {analysis_result['r2']:.4f}\n"
                                  f"Output: {trend_path}")
            
        except Exception as e:
            QMessageBox.critical(self.dlg, "Analysis Error", 
                               f"An error occurred during analysis:\n{str(e)}")
            QgsMessageLog.logMessage(f"Trend Surface Error: {str(e)}", "EnhancedTrendSurface", Qgis.Critical)   

    def load_results(self, result):
        """Load analysis results into QGIS project"""
        try:
            # Load trend surface raster
            if os.path.exists(result['OUTPUT_TREND']):
                trend_layer = QgsRasterLayer(result['OUTPUT_TREND'], "Trend Surface")
                if trend_layer.isValid():
                    QgsProject.instance().addMapLayer(trend_layer)
                    # Apply default style
                    self.apply_trend_style(trend_layer)
                else:
                    QgsMessageLog.logMessage("Failed to load trend surface raster", "EnhancedTrendSurface", Qgis.Warning)

            # Load residuals raster if available
            if result.get('OUTPUT_RESIDUALS') and os.path.exists(result['OUTPUT_RESIDUALS']):
                residuals_layer = QgsRasterLayer(result['OUTPUT_RESIDUALS'], "Residuals Surface")
                if residuals_layer.isValid():
                    QgsProject.instance().addMapLayer(residuals_layer)
                    self.apply_residuals_style(residuals_layer)

            # Load confidence raster if available
            if result.get('OUTPUT_CONFIDENCE') and os.path.exists(result['OUTPUT_CONFIDENCE']):
                confidence_layer = QgsRasterLayer(result['OUTPUT_CONFIDENCE'], "Confidence Intervals")
                if confidence_layer.isValid():
                    QgsProject.instance().addMapLayer(confidence_layer)
                    self.apply_confidence_style(confidence_layer)

            # Residual points layer is already added by the algorithm

            # Zoom to trend surface extent
            if trend_layer and trend_layer.isValid():
                self.iface.mapCanvas().setExtent(trend_layer.extent())
                self.iface.mapCanvas().refresh()

        except Exception as e:
            QgsMessageLog.logMessage(f"Error loading results: {str(e)}", "EnhancedTrendSurface", Qgis.Warning)

    def apply_trend_style(self, layer):
        """Apply default style to trend surface layer"""
        try:
            # Create a color ramp for trend surface
            from qgis.core import QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
            from qgis.PyQt.QtGui import QColor
            
            # Get statistics for better classification
            stats = layer.dataProvider().bandStatistics(1)
            
            # Create color ramp
            color_ramp = QgsColorRampShader()
            color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
            
            # Define colors (blue to red)
            items = [
                QgsColorRampShader.ColorRampItem(stats.minimum, QColor(0, 0, 255), "Low"),
                QgsColorRampShader.ColorRampItem((stats.minimum + stats.maximum) / 2, QColor(255, 255, 0), "Medium"),
                QgsColorRampShader.ColorRampItem(stats.maximum, QColor(255, 0, 0), "High")
            ]
            
            color_ramp.setColorRampItemList(items)
            
            # Apply shader
            shader = QgsRasterShader()
            shader.setRasterShaderFunction(color_ramp)
            
            renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
            layer.setRenderer(renderer)
            layer.triggerRepaint()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Could not apply trend style: {str(e)}", "EnhancedTrendSurface", Qgis.Warning)

    def apply_residuals_style(self, layer):
        """Apply style to residuals layer"""
        try:
            from qgis.core import QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
            from qgis.PyQt.QtGui import QColor
            
            # Create diverging color ramp for residuals
            color_ramp = QgsColorRampShader()
            color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
            
            # Blue-white-red diverging scheme
            items = [
                QgsColorRampShader.ColorRampItem(-100, QColor(0, 0, 255), "Negative"),
                QgsColorRampShader.ColorRampItem(0, QColor(255, 255, 255), "Zero"),
                QgsColorRampShader.ColorRampItem(100, QColor(255, 0, 0), "Positive")
            ]
            
            color_ramp.setColorRampItemList(items)
            
            shader = QgsRasterShader()
            shader.setRasterShaderFunction(color_ramp)
            
            renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
            layer.setRenderer(renderer)
            layer.triggerRepaint()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Could not apply residuals style: {str(e)}", "EnhancedTrendSurface", Qgis.Warning)

    def apply_confidence_style(self, layer):
        """Apply style to confidence intervals layer"""
        try:
            from qgis.core import QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
            from qgis.PyQt.QtGui import QColor
            
            # Grayscale for confidence intervals
            color_ramp = QgsColorRampShader()
            color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
            
            items = [
                QgsColorRampShader.ColorRampItem(0, QColor(255, 255, 255), "Low Uncertainty"),
                QgsColorRampShader.ColorRampItem(50, QColor(128, 128, 128), "Medium Uncertainty"),
                QgsColorRampShader.ColorRampItem(100, QColor(0, 0, 0), "High Uncertainty")
            ]
            
            color_ramp.setColorRampItemList(items)
            
            shader = QgsRasterShader()
            shader.setRasterShaderFunction(color_ramp)
            
            renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
            layer.setRenderer(renderer)
            layer.triggerRepaint()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Could not apply confidence style: {str(e)}", "EnhancedTrendSurface", Qgis.Warning)
