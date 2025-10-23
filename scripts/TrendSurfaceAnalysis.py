# -*- coding: utf-8 -*-

"""
Enhanced Polynomial Trend Surface Analysis with Least Squares Regression
Fixed version with proper matrix dimension handling
"""

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterEnum,
                       QgsProcessingUtils,
                       QgsFields, QgsField, QgsFeature,
                       QgsGeometry, QgsPointXY,
                       QgsRasterLayer, QgsCoordinateReferenceSystem,
                       QgsProcessingException,
                       QgsVectorLayer,
                       QgsProject)
import numpy as np
from osgeo import gdal, osr
import tempfile
import os
import scipy.stats as stats
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


class EnhancedTrendSurfaceAlgorithm(QgsProcessingAlgorithm):
    """
    Enhanced algorithm for polynomial trend surface analysis with comprehensive diagnostics
    """

    # Input parameters
    INPUT = 'INPUT'
    Z_FIELD = 'Z_FIELD'
    POLYNOMIAL = 'POLYNOMIAL'
    CELL_SIZE = 'CELL_SIZE'
    EXTENT = 'EXTENT'
    CONFIDENCE_LEVEL = 'CONFIDENCE_LEVEL'
    CROSS_VALIDATION = 'CROSS_VALIDATION'
    OUTPUT_TREND = 'OUTPUT_TREND'
    OUTPUT_RESIDUALS = 'OUTPUT_RESIDUALS'
    OUTPUT_CONFIDENCE = 'OUTPUT_CONFIDENCE'
    OUTPUT_STATS = 'OUTPUT_STATS'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    ROBUST_REGRESSION = 'ROBUST_REGRESSION'
    WEIGHT_FIELD = 'WEIGHT_FIELD'

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

        # Weight field (optional)
        self.addParameter(
            QgsProcessingParameterField(
                self.WEIGHT_FIELD,
                self.tr('Weight field (optional)'),
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT,
                optional=True
            )
        )

        # Polynomial degree with more options
        self.addParameter(
            QgsProcessingParameterNumber(
                self.POLYNOMIAL,
                self.tr('Polynomial degree'),
                type=QgsProcessingParameterNumber.Integer,
                minValue=1,
                maxValue=8,
                defaultValue=2
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

        # Confidence level
        self.addParameter(
            QgsProcessingParameterNumber(
                self.CONFIDENCE_LEVEL,
                self.tr('Confidence level (%)'),
                type=QgsProcessingParameterNumber.Double,
                minValue=80,
                maxValue=99.9,
                defaultValue=95.0
            )
        )

        # Cross-validation
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CROSS_VALIDATION,
                self.tr('Perform cross-validation'),
                defaultValue=False
            )
        )

        # Robust regression
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ROBUST_REGRESSION,
                self.tr('Use robust regression (outlier resistant)'),
                defaultValue=False
            )
        )

        # Output trend surface
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_TREND,
                self.tr('Trend surface raster')
            )
        )

        # Output residuals raster
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RESIDUALS,
                self.tr('Residuals raster'),
                optional=True
            )
        )

        # Output confidence intervals
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_CONFIDENCE,
                self.tr('Confidence intervals raster'),
                optional=True
            )
        )

        # Output statistics
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Output folder for statistics and charts'),
                optional=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Get parameters
        source = self.parameterAsSource(parameters, self.INPUT, context)
        z_field = self.parameterAsString(parameters, self.Z_FIELD, context)
        weight_field = self.parameterAsString(parameters, self.WEIGHT_FIELD, context)
        polynomial_degree = self.parameterAsInt(parameters, self.POLYNOMIAL, context)
        cell_size = self.parameterAsDouble(parameters, self.CELL_SIZE, context)
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        confidence_level = self.parameterAsDouble(parameters, self.CONFIDENCE_LEVEL, context) / 100.0
        cross_validation = self.parameterAsBool(parameters, self.CROSS_VALIDATION, context)
        robust_regression = self.parameterAsBool(parameters, self.ROBUST_REGRESSION, context)
        output_trend = self.parameterAsOutputLayer(parameters, self.OUTPUT_TREND, context)
        output_residuals = self.parameterAsOutputLayer(parameters, self.OUTPUT_RESIDUALS, context)
        output_confidence = self.parameterAsOutputLayer(parameters, self.OUTPUT_CONFIDENCE, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Collect points and values
        feedback.pushInfo("Collecting data points...")
        points, z_values, weights = self.collect_data(source, z_field, weight_field, feedback)

        if len(points) < 3:
            raise QgsProcessingException("Insufficient points to generate trend surface")

        # Convert to arrays
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        z = np.array(z_values)
        w = np.array(weights) if weights else None

        feedback.pushInfo(f"Data collected: {len(x)} points")
        feedback.pushInfo(f"Z value range: {np.min(z):.2f} to {np.max(z):.2f}")

        # Perform trend surface analysis
        results = self.trend_surface_analysis(
            x, y, z, w, polynomial_degree, confidence_level, 
            cross_validation, robust_regression, feedback
        )

        # Generate rasters
        self.generate_rasters(
            x, y, results, extent, cell_size, source.sourceCrs(),
            output_trend, output_residuals, output_confidence,
            feedback
        )

        # Generate statistics and charts
        if output_folder:
            self.generate_statistics(output_folder, results, feedback)

        # Add residual points to project
        residual_layer = self.create_residual_points_layer(source, results['residuals'], z_field, context)
        QgsProject.instance().addMapLayer(residual_layer)

        feedback.pushInfo("Enhanced trend surface analysis completed successfully!")
        
        return {
            self.OUTPUT_TREND: output_trend,
            self.OUTPUT_RESIDUALS: output_residuals if output_residuals else None,
            self.OUTPUT_CONFIDENCE: output_confidence if output_confidence else None,
            'RESIDUAL_POINTS': residual_layer
        }

    def collect_data(self, source, z_field, weight_field, feedback):
        """Collect points, Z values, and weights"""
        points = []
        z_values = []
        weights = []
        
        total_features = source.featureCount()
        
        for i, feature in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break
                
            if i % 100 == 0:
                feedback.setProgress(int(i / total_features * 20))
                
            geometry = feature.geometry()
            z_value = feature[z_field]
            
            if z_value is None or np.isnan(z_value):
                continue  # Skip null values
                
            if geometry.isMultipart():
                multi_points = geometry.asMultiPoint()
                for point in multi_points:
                    points.append((point.x(), point.y()))
                    z_values.append(z_value)
                    if weight_field and feature[weight_field] is not None:
                        weights.append(feature[weight_field])
            else:
                point = geometry.asPoint()
                points.append((point.x(), point.y()))
                z_values.append(z_value)
                if weight_field and feature[weight_field] is not None:
                    weights.append(feature[weight_field])
        
        # If weights were requested but not all features have them, set to None
        if weight_field and len(weights) != len(points):
            feedback.pushWarning("Weight field not available for all points. Using unweighted regression.")
            weights = None
        
        feedback.pushInfo(f"Successfully collected {len(points)} valid points")
        return points, z_values, weights

    def trend_surface_analysis(self, x, y, z, w, degree, confidence_level, 
                             cross_validation, robust_regression, feedback):
        """Perform comprehensive trend surface analysis"""
        
        # Create design matrix
        A = self.create_design_matrix(x, y, degree)
        feedback.pushInfo(f"Design matrix shape: {A.shape}")
        
        # Check for sufficient data
        n_samples, n_features = A.shape
        if n_samples < n_features:
            raise QgsProcessingException(
                f"Insufficient data points ({n_samples}) for polynomial degree {degree} "
                f"(requires at least {n_features} points)"
            )

        # Fit model
        if robust_regression:
            coefficients, residuals, model_stats = self.robust_regression_fit(A, z, w, feedback)
        else:
            coefficients, residuals, model_stats = self.least_squares_fit(A, z, w, feedback)
        
        # Calculate predictions
        z_pred = np.dot(A, coefficients)
        
        # Cross-validation
        cv_results = None
        if cross_validation and len(z) > 10:
            cv_results = self.cross_validation(x, y, z, w, degree, feedback)
        
        # Confidence intervals
        confidence_intervals = self.calculate_confidence_intervals(
            A, coefficients, residuals, confidence_level, model_stats, len(z)
        )
        
        # Comprehensive statistics
        statistics = self.calculate_statistics(z, z_pred, residuals, degree, cv_results)
        
        feedback.pushInfo(f"Model R²: {statistics['r2']:.4f}")
        feedback.pushInfo(f"RMSE: {statistics['rmse']:.4f}")
        
        return {
            'coefficients': coefficients,
            'predictions': z_pred,
            'residuals': residuals,
            'design_matrix': A,
            'model_stats': model_stats,
            'confidence_intervals': confidence_intervals,
            'statistics': statistics,
            'cv_results': cv_results,
            'degree': degree
        }

    def create_design_matrix(self, x, y, degree):
        """Create polynomial design matrix with proper dimension handling"""
        n_points = len(x)
        n_terms = (degree + 1) * (degree + 2) // 2
        
        A = np.ones((n_points, n_terms))
        
        col_index = 0
        for d in range(degree + 1):
            for j in range(d + 1):
                if col_index < n_terms:  # Safety check
                    A[:, col_index] = (x ** (d - j)) * (y ** j)
                    col_index += 1
        
        return A

    def least_squares_fit(self, A, z, w, feedback):
        """Ordinary least squares fit with proper error handling"""
        try:
            if w is not None and len(w) == len(z):
                # Weighted least squares
                W_sqrt = np.sqrt(w)
                A_weighted = A * W_sqrt[:, np.newaxis]
                z_weighted = z * W_sqrt
                coefficients, residuals, rank, s = np.linalg.lstsq(A_weighted, z_weighted, rcond=None)
                feedback.pushInfo("Used weighted least squares")
            else:
                # Ordinary least squares
                coefficients, residuals, rank, s = np.linalg.lstsq(A, z, rcond=None)
                feedback.pushInfo("Used ordinary least squares")
            
            # Calculate residuals properly
            z_pred = np.dot(A, coefficients)
            residuals = z - z_pred
            
            model_stats = {
                'rank': rank,
                'singular_values': s,
                'effective_parameters': rank
            }
            
            return coefficients, residuals, model_stats
            
        except np.linalg.LinAlgError as e:
            raise QgsProcessingException(f"Matrix solving failed: {str(e)}. Try reducing polynomial degree.")
        except Exception as e:
            raise QgsProcessingException(f"Regression failed: {str(e)}")

    def robust_regression_fit(self, A, z, w, feedback, max_iter=20, tol=1e-6):
        """Iteratively reweighted least squares for robust regression"""
        feedback.pushInfo("Starting robust regression...")
        
        # Initial OLS fit
        coefficients, residuals, model_stats = self.least_squares_fit(A, z, w, feedback)
        
        for iteration in range(max_iter):
            # Calculate robust weights using Huber function
            abs_residuals = np.abs(residuals)
            mad = np.median(abs_residuals)
            
            if mad < 1e-10:  # Avoid division by zero
                break
                
            # Huber weighting function
            k = 1.345 * mad  # Tuning constant
            robust_weights = np.where(abs_residuals <= k, 1.0, k / abs_residuals)
            
            # Update weights considering original weights if provided
            if w is not None:
                robust_weights = robust_weights * w
            
            # Weighted least squares iteration
            W_sqrt = np.sqrt(robust_weights)
            A_weighted = A * W_sqrt[:, np.newaxis]
            z_weighted = z * W_sqrt
            
            try:
                new_coefficients, _, _, _ = np.linalg.lstsq(A_weighted, z_weighted, rcond=None)
            except:
                break
            
            # Check convergence
            coefficient_change = np.max(np.abs(new_coefficients - coefficients))
            if coefficient_change < tol:
                feedback.pushInfo(f"Robust regression converged after {iteration + 1} iterations")
                break
                
            coefficients = new_coefficients
            residuals = z - np.dot(A, coefficients)
        
        model_stats['robust_iterations'] = iteration + 1
        return coefficients, residuals, model_stats

    def cross_validation(self, x, y, z, w, degree, feedback, k=5):
        """k-fold cross-validation with proper dimension handling"""
        n = len(z)
        if n < 10:
            feedback.pushWarning("Too few points for cross-validation")
            return None
            
        indices = np.arange(n)
        np.random.shuffle(indices)
        
        fold_size = n // k
        mse_scores = []
        r2_scores = []
        
        for fold in range(min(k, n)):  # Ensure we don't have more folds than points
            if feedback.isCanceled():
                break
                
            # Split data
            test_start = fold * fold_size
            test_end = min(test_start + fold_size, n)
            
            if test_start >= n:
                break
                
            test_idx = indices[test_start:test_end]
            train_idx = np.concatenate([indices[:test_start], indices[test_end:]])
            
            if len(train_idx) == 0 or len(test_idx) == 0:
                continue
            
            # Train model
            try:
                A_train = self.create_design_matrix(x[train_idx], y[train_idx], degree)
                if len(train_idx) < A_train.shape[1]:
                    continue  # Skip if not enough training data
                    
                w_train = w[train_idx] if w is not None else None
                coefficients, _, _ = self.least_squares_fit(A_train, z[train_idx], w_train, feedback)
                
                # Test model
                A_test = self.create_design_matrix(x[test_idx], y[test_idx], degree)
                z_pred_test = np.dot(A_test, coefficients)
                
                # Calculate scores
                mse = mean_squared_error(z[test_idx], z_pred_test)
                r2 = r2_score(z[test_idx], z_pred_test)
                
                mse_scores.append(mse)
                r2_scores.append(r2)
            except Exception as e:
                feedback.pushWarning(f"Cross-validation fold {fold} failed: {str(e)}")
                continue
        
        if not mse_scores:
            return None
            
        return {
            'mse_mean': np.mean(mse_scores),
            'mse_std': np.std(mse_scores),
            'r2_mean': np.mean(r2_scores),
            'r2_std': np.std(r2_scores),
            'folds_completed': len(mse_scores)
        }

    def calculate_confidence_intervals(self, A, coefficients, residuals, confidence_level, model_stats, n_samples):
        """Calculate confidence intervals for predictions"""
        n = n_samples
        p = len(coefficients)
        
        if n <= p:
            return {
                'rse': 0,
                'std_errors': np.zeros_like(coefficients),
                't_value': 0,
                'confidence_level': confidence_level
            }
        
        # Residual standard error
        ss_res = np.sum(residuals**2)
        rse = np.sqrt(ss_res / (n - p))
        
        # Covariance matrix
        try:
            cov_matrix = np.linalg.inv(A.T @ A) * (rse**2)
            std_errors = np.sqrt(np.diag(cov_matrix))
        except:
            std_errors = np.ones_like(coefficients) * rse
        
        # t-value for confidence interval
        try:
            t_value = stats.t.ppf(1 - (1 - confidence_level) / 2, n - p)
        except:
            t_value = 1.96  # Fallback to normal distribution
        
        return {
            'rse': rse,
            'std_errors': std_errors,
            't_value': t_value,
            'confidence_level': confidence_level
        }

    def calculate_statistics(self, z_obs, z_pred, residuals, degree, cv_results):
        """Calculate comprehensive model statistics"""
        n = len(z_obs)
        p = (degree + 1) * (degree + 2) // 2  # Number of parameters
        
        if n <= p:
            return {
                'n_observations': n,
                'n_parameters': p,
                'r2': 0,
                'r2_adjusted': 0,
                'rmse': 0,
                'mae': 0,
                'aic': 0,
                'bic': 0,
                'normality_p': 0,
                'residual_mean': 0,
                'residual_std': 0
            }
        
        # Basic statistics
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((z_obs - np.mean(z_obs))**2)
        
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        r2_adj = 1 - (1 - r2) * (n - 1) / (n - p - 1) if (n - p - 1) > 0 else r2
        rmse = np.sqrt(ss_res / n)
        mae = np.mean(np.abs(residuals))
        
        # AIC and BIC
        aic = n * np.log(ss_res / n) + 2 * p if ss_res > 0 else 0
        bic = n * np.log(ss_res / n) + p * np.log(n) if ss_res > 0 else 0
        
        # Normality test
        try:
            _, normality_p = stats.normaltest(residuals)
        except:
            normality_p = 0
        
        statistics = {
            'n_observations': n,
            'n_parameters': p,
            'r2': r2,
            'r2_adjusted': r2_adj,
            'rmse': rmse,
            'mae': mae,
            'aic': aic,
            'bic': bic,
            'normality_p': normality_p,
            'residual_mean': np.mean(residuals),
            'residual_std': np.std(residuals)
        }
        
        if cv_results:
            statistics.update({
                'cv_mse': cv_results['mse_mean'],
                'cv_r2': cv_results['r2_mean'],
                'cv_folds': cv_results['folds_completed']
            })
        
        return statistics

    def generate_rasters(self, x, y, results, extent, cell_size, crs,
                        output_trend, output_residuals, output_confidence, feedback):
        """Generate output rasters"""
        
        # Determine extent
        if extent.isNull():
            xmin, xmax = np.min(x), np.max(x)
            ymin, ymax = np.min(y), np.max(y)
            # Add 10% buffer
            x_range = xmax - xmin
            y_range = ymax - ymin
            xmin -= x_range * 0.1
            xmax += x_range * 0.1
            ymin -= y_range * 0.1
            ymax += y_range * 0.1
        else:
            xmin, xmax = extent.xMinimum(), extent.xMaximum()
            ymin, ymax = extent.yMinimum(), extent.yMaximum()

        # Calculate dimensions
        cols = max(1, int((xmax - xmin) / cell_size) + 1)
        rows = max(1, int((ymax - ymin) / cell_size) + 1)

        feedback.pushInfo(f"Generating rasters with dimensions: {cols} x {rows}")

        # Create trend surface raster
        trend_data = np.zeros((rows, cols), dtype=np.float32)
        confidence_data = np.zeros((rows, cols), dtype=np.float32)

        coefficients = results['coefficients']
        degree = results['degree']
        confidence_info = results['confidence_intervals']

        for row in range(rows):
            if feedback.isCanceled():
                break
                
            if row % 100 == 0:
                feedback.setProgress(50 + int(row / rows * 40))
                
            y_val = ymax - row * cell_size
            for col in range(cols):
                x_val = xmin + col * cell_size
                trend_val = self.evaluate_polynomial(x_val, y_val, coefficients, degree)
                trend_data[row, col] = trend_val
                confidence_data[row, col] = confidence_info['rse']  # Standard error

        # Save rasters
        self.save_raster(output_trend, trend_data, xmin, ymax, cell_size, crs, "Trend Surface")
        
        if output_residuals:
            # For residual raster, we would need to interpolate point residuals
            # For now, create a placeholder
            residual_data = np.zeros((rows, cols), dtype=np.float32)
            self.save_raster(output_residuals, residual_data, xmin, ymax, cell_size, crs, "Residuals")
            
        if output_confidence:
            self.save_raster(output_confidence, confidence_data, xmin, ymax, cell_size, crs, "Confidence")

    def save_raster(self, path, data, xmin, ymax, cell_size, crs, description):
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
        band.SetDescription(description)
        band.FlushCache()
        out_raster = None

    def evaluate_polynomial(self, x, y, coefficients, degree):
        """Evaluate polynomial at given coordinates"""
        value = 0
        idx = 0
        for d in range(degree + 1):
            for j in range(d + 1):
                if idx < len(coefficients):  # Safety check
                    value += coefficients[idx] * (x ** (d - j)) * (y ** j)
                    idx += 1
        return value

    def create_residual_points_layer(self, source, residuals, z_field, context):
        """Create a point layer with residuals"""
        # Create temporary layer
        residual_layer = QgsVectorLayer("Point?crs=" + source.sourceCrs().authid(), "Residual Points", "memory")
        provider = residual_layer.dataProvider()
        
        # Add fields
        fields = source.fields()
        fields.append(QgsField("residual", QVariant.Double))
        fields.append(QgsField("predicted", QVariant.Double))
        provider.addAttributes(fields)
        residual_layer.updateFields()
        
        # Add features with residuals
        features = []
        source_features = list(source.getFeatures())
        
        for i, (feature, residual) in enumerate(zip(source_features, residuals)):
            if i >= len(residuals):
                break
                
            new_feature = QgsFeature(residual_layer.fields())
            new_feature.setGeometry(feature.geometry())
            
            # Copy attributes
            for j in range(source.fields().count()):
                if j < len(feature.attributes()):
                    new_feature.setAttribute(j, feature.attributes()[j])
            
            # Add residual and predicted values
            z_value = feature[z_field] if feature[z_field] is not None else 0
            new_feature.setAttribute(source.fields().count(), float(residual))
            new_feature.setAttribute(source.fields().count() + 1, float(z_value - residual))
            
            features.append(new_feature)
        
        provider.addFeatures(features)
        residual_layer.updateExtents()
        
        return residual_layer

    def generate_statistics(self, output_folder, results, feedback):
        """Generate statistical reports and charts"""
        try:
            stats = results['statistics']
            
            # Create report
            report_path = os.path.join(output_folder, f"trend_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(report_path, 'w') as f:
                f.write("ENHANCED POLYNOMIAL TREND SURFACE ANALYSIS REPORT\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Polynomial Degree: {results['degree']}\n")
                f.write(f"Number of Observations: {stats['n_observations']}\n")
                f.write(f"Number of Parameters: {stats['n_parameters']}\n\n")
                
                f.write("GOODNESS OF FIT STATISTICS:\n")
                f.write(f"R²: {stats['r2']:.4f}\n")
                f.write(f"Adjusted R²: {stats['r2_adjusted']:.4f}\n")
                f.write(f"RMSE: {stats['rmse']:.4f}\n")
                f.write(f"MAE: {stats['mae']:.4f}\n\n")
                
                f.write("MODEL SELECTION CRITERIA:\n")
                f.write(f"AIC: {stats['aic']:.4f}\n")
                f.write(f"BIC: {stats['bic']:.4f}\n\n")
                
                f.write("RESIDUAL ANALYSIS:\n")
                f.write(f"Residual Mean: {stats['residual_mean']:.6f}\n")
                f.write(f"Residual Std: {stats['residual_std']:.4f}\n")
                f.write(f"Normality Test p-value: {stats['normality_p']:.4f}\n")
                
                if 'cv_r2' in stats:
                    f.write("\nCROSS-VALIDATION RESULTS:\n")
                    f.write(f"CV R²: {stats['cv_r2']:.4f}\n")
                    f.write(f"CV MSE: {stats['cv_mse']:.4f}\n")
                    f.write(f"Folds Completed: {stats['cv_folds']}\n")
            
            feedback.pushInfo(f"Statistics report saved: {report_path}")
            
        except Exception as e:
            feedback.pushWarning(f"Could not generate statistics report: {str(e)}")

    def name(self):
        return 'enhancedtrendsurface'

    def displayName(self):
        return self.tr('Enhanced Trend Surface Analysis')

    def group(self):
        return self.tr('Surface Analysis')

    def groupId(self):
        return 'surfaceanalysis'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return EnhancedTrendSurfaceAlgorithm()


def classFactory(iface):
    return EnhancedTrendSurfaceAlgorithm()