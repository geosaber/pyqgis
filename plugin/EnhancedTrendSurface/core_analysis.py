# -*- coding: utf-8 -*-
"""
Core trend surface analysis functionality
"""

import numpy as np
from qgis.core import (QgsVectorLayer, QgsRasterLayer, QgsProject, 
                       QgsCoordinateReferenceSystem, QgsFields, QgsField, 
                       QgsFeature, QgsGeometry, QgsPointXY)
from osgeo import gdal, osr
import tempfile
import os
from qgis.PyQt.QtCore import QVariant


class TrendSurfaceAnalyzer:
    """Core trend surface analysis engine"""
    
    def __init__(self, feedback_callback=None):
        self.feedback = feedback_callback
    
    def log(self, message):
        """Log message through feedback or print"""
        if self.feedback:
            self.feedback(message)
        else:
            print(message)
    
    def analyze(self, input_layer, z_field, polynomial_degree=2, cell_size=100):
        """Perform trend surface analysis"""
        try:
            self.log("Starting trend surface analysis...")
            
            # Collect data
            points, z_values = self.collect_point_data(input_layer, z_field)
            
            if len(points) < 3:
                raise Exception("Insufficient points for analysis")
            
            # Convert to arrays
            x = np.array([p[0] for p in points])
            y = np.array([p[1] for p in points])
            z = np.array(z_values)
            
            self.log(f"Processing {len(points)} points...")
            
            # Create design matrix
            A = self.create_design_matrix(x, y, polynomial_degree)
            
            # Perform regression
            coefficients, residuals = self.polynomial_regression(A, z)
            
            # Calculate statistics
            z_pred = A @ coefficients
            r2 = self.calculate_r2(z, z_pred)
            
            self.log(f"Analysis complete - R²: {r2:.4f}")
            
            return {
                'coefficients': coefficients,
                'residuals': residuals,
                'points': points,
                'z_original': z,
                'z_predicted': z_pred,
                'r2': r2,
                'degree': polynomial_degree
            }
            
        except Exception as e:
            self.log(f"Analysis error: {str(e)}")
            raise
    
    def collect_point_data(self, layer, z_field):
        """Collect point coordinates and Z values"""
        points = []
        z_values = []
        
        for feature in layer.getFeatures():
            geometry = feature.geometry()
            z_value = feature[z_field]
            
            if geometry.isMultipart():
                for point in geometry.asMultiPoint():
                    points.append((point.x(), point.y()))
                    z_values.append(z_value)
            else:
                point = geometry.asPoint()
                points.append((point.x(), point.y()))
                z_values.append(z_value)
        
        return points, z_values
    
    def create_design_matrix(self, x, y, degree):
        """Create polynomial design matrix"""
        n_points = len(x)
        n_terms = (degree + 1) * (degree + 2) // 2
        
        A = np.ones((n_points, n_terms))
        
        col_index = 0
        for d in range(degree + 1):
            for j in range(d + 1):
                if col_index < n_terms:
                    A[:, col_index] = (x ** (d - j)) * (y ** j)
                    col_index += 1
        
        return A
    
    def polynomial_regression(self, A, z):
        """Perform polynomial regression using least squares"""
        try:
            # Solve using normal equations: (A^T A)^-1 A^T z
            ATA = A.T @ A
            ATz = A.T @ z
            coefficients = np.linalg.solve(ATA, ATz)
            
            # Calculate residuals
            residuals = z - (A @ coefficients)
            
            return coefficients, residuals
            
        except np.linalg.LinAlgError:
            # Fallback to pseudo-inverse if matrix is singular
            coefficients = np.linalg.pinv(A) @ z
            residuals = z - (A @ coefficients)
            return coefficients, residuals
    
    def calculate_r2(self, z_obs, z_pred):
        """Calculate R-squared value"""
        ss_res = np.sum((z_obs - z_pred) ** 2)
        ss_tot = np.sum((z_obs - np.mean(z_obs)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    def create_trend_surface(self, analysis_result, extent, cell_size, crs, output_path):
        """Create trend surface raster"""
        try:
            self.log("Creating trend surface raster...")
            
            # Determine extent from points if not provided
            if extent is None:
                points = analysis_result['points']
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                xmin, xmax = min(x_coords), max(x_coords)
                ymin, ymax = min(y_coords), max(y_coords)
                # Add 10% buffer
                x_buffer = (xmax - xmin) * 0.1
                y_buffer = (ymax - ymin) * 0.1
                xmin -= x_buffer
                xmax += x_buffer
                ymin -= y_buffer
                ymax += y_buffer
            else:
                xmin, xmax = extent.xMinimum(), extent.xMaximum()
                ymin, ymax = extent.yMinimum(), extent.yMaximum()
            
            # Calculate dimensions
            cols = max(1, int((xmax - xmin) / cell_size) + 1)
            rows = max(1, int((ymax - ymin) / cell_size) + 1)
            
            self.log(f"Raster dimensions: {cols} x {rows}")
            
            # Create raster data
            trend_data = np.zeros((rows, cols), dtype=np.float32)
            coefficients = analysis_result['coefficients']
            degree = analysis_result['degree']
            
            for row in range(rows):
                if row % 100 == 0:
                    self.log(f"Processing row {row}/{rows}")
                
                y_val = ymax - row * cell_size
                for col in range(cols):
                    x_val = xmin + col * cell_size
                    trend_data[row, col] = self.evaluate_polynomial(x_val, y_val, coefficients, degree)
            
            # Save raster
            self.save_raster(output_path, trend_data, xmin, ymax, cell_size, crs)
            self.log(f"Trend surface saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            self.log(f"Error creating trend surface: {str(e)}")
            raise
    
    def evaluate_polynomial(self, x, y, coefficients, degree):
        """Evaluate polynomial at given coordinates"""
        value = 0
        idx = 0
        for d in range(degree + 1):
            for j in range(d + 1):
                if idx < len(coefficients):
                    value += coefficients[idx] * (x ** (d - j)) * (y ** j)
                    idx += 1
        return value
    
    def save_raster(self, path, data, xmin, ymax, cell_size, crs):
        """Save data to raster file"""
        driver = gdal.GetDriverByName('GTiff')
        rows, cols = data.shape
        
        out_raster = driver.Create(path, cols, rows, 1, gdal.GDT_Float32)
        out_raster.SetGeoTransform((xmin, cell_size, 0, ymax, 0, -cell_size))
        
        if crs.isValid():
            srs = osr.SpatialReference()
            srs.ImportFromWkt(crs.toWkt())
            out_raster.SetProjection(srs.ExportToWkt())
        
        band = out_raster.GetRasterBand(1)
        band.WriteArray(data)
        band.SetNoDataValue(-9999)
        band.FlushCache()
        out_raster = None
    
    def create_residual_layer(self, input_layer, residuals, z_field):
        """Create a point layer with residuals"""
        residual_layer = QgsVectorLayer("Point?crs=" + input_layer.sourceCrs().authid(), 
                                      "Residual Points", "memory")
        provider = residual_layer.dataProvider()
        
        # Add fields
        fields = input_layer.fields()
        fields.append(QgsField("residual", QVariant.Double))
        fields.append(QgsField("predicted", QVariant.Double))
        provider.addAttributes(fields)
        residual_layer.updateFields()
        
        # Add features with residuals
        features = []
        for i, (feature, residual) in enumerate(zip(input_layer.getFeatures(), residuals)):
            if i >= len(residuals):
                break
                
            new_feature = QgsFeature(residual_layer.fields())
            new_feature.setGeometry(feature.geometry())
            
            # Copy attributes
            attributes = feature.attributes()
            for j in range(min(len(attributes), input_layer.fields().count())):
                new_feature.setAttribute(j, attributes[j])
            
            # Add residual and predicted values
            z_value = feature[z_field] if feature[z_field] is not None else 0
            new_feature.setAttribute(input_layer.fields().count(), float(residual))
            new_feature.setAttribute(input_layer.fields().count() + 1, float(z_value - residual))
            
            features.append(new_feature)
        
        provider.addFeatures(features)
        residual_layer.updateExtents()
        
        return residual_layer