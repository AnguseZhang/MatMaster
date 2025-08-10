"""
Simplified MCP Tool for Data Analysis, following FastMCP server format.

This tool performs:
1. Data Preprocessing: Drop rows with missing values.
2. Feature Engineering: Pearson correlation analysis.
3. Model Training: XGBoost regression with hyperparameter optimization.
4. Model Interpretation: SHAP analysis.
5. Data Visualization: Generate and save plots to output directory.
6. Database Integration: Load data directly from database tables.

Usage:
- User uploads a CSV file or loads data from database.
- The tool processes the data, generates visualizations, and returns results.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import json
import requests
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import tempfile
import os
import base64
from typing import Dict, Any, Optional, List
import argparse
from mcp.server.fastmcp import FastMCP
from datetime import datetime


# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


def parse_args():
    """Parse command line arguments for MCP server."""
    parser = argparse.ArgumentParser(description="Data Analysis MCP Server")
    parser.add_argument('--port', type=int, default=50001, help='Server port (default: 50001)')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    try:
        args = parser.parse_args()
    except SystemExit:
        class Args:
            port = 50001
            host = '0.0.0.0'
            log_level = 'INFO'
        args = Args()
    return args


args = parse_args()
mcp = FastMCP("data_analysis", port=args.port, host=args.host)


# 全局共享数据存储
class DataStorage:
    """全局数据存储类，用于在各个独立工具间共享数据"""
    def __init__(self):
        self.datasets = {}  # 存储多个数据集
        self.models = {}    # 存储多个模型
        self.results = {}   # 存储分析结果
    
    def store_data(self, dataset_id: str, data: pd.DataFrame, metadata: dict = None):
        """存储数据集"""
        self.datasets[dataset_id] = {
            'data': data,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
    
    def get_data(self, dataset_id: str) -> pd.DataFrame:
        """获取数据集"""
        if dataset_id in self.datasets:
            return self.datasets[dataset_id]['data']
        return None
    
    def store_model(self, model_id: str, model, metadata: dict = None):
        """存储模型"""
        self.models[model_id] = {
            'model': model,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
    
    def get_model(self, model_id: str):
        """获取模型"""
        if model_id in self.models:
            return self.models[model_id]['model']
        return None

# 全局数据存储实例
data_storage = DataStorage()

class DataAnalysisBase:
    """数据分析工具基类"""
    
    def __init__(self, output_dir: str = "/personal/sse_brain/agents/solid_electrolyte_brain/output", 
                 database_url: str = "http://localhost:5002"):
        self.output_dir = output_dir
        self.database_url = database_url.rstrip('/')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up matplotlib for headless environment
        plt.switch_backend('Agg')
        
        # Set up session for database requests
        self.session = requests.Session()

    def _save_plot(self, filename: str) -> str:
        """Save current plot to output directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(self.output_dir, full_filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        return filepath

    def load_data_from_database(self, table_name: str, conditions_json: str = "[]", 
                              page_size: int = 1000, dataset_id: str = "default") -> Dict[str, Any]:
        """
        Load data directly from database table.

        Args:
            table_name (str): Name of the database table.
            conditions_json (str): JSON string with query conditions.
            page_size (int): Maximum number of records to fetch.

        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            conditions = json.loads(conditions_json)
            response = self.session.post(
                f"{self.database_url}/tables/{table_name}/query", 
                json={'conditions': conditions, 'limit': page_size}
            )
            response.raise_for_status()
            
            data_rows = response.json()
            if not data_rows:
                return {
                    'success': False,
                    'message': f'No data found in table {table_name} with given conditions'
                }
            
            # Convert to DataFrame
            data = pd.DataFrame(data_rows)
            
            # 存储到全局存储中
            data_storage.store_data(dataset_id, data, {
                'source': 'database',
                'table_name': table_name,
                'conditions': conditions,
                'page_size': page_size
            })
            
            # Generate basic visualization
            if len(data) > 0:
                plt.figure(figsize=(12, 8))
                
                # Create subplots for data overview
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                fig.suptitle(f'Data Overview from Table: {table_name}', fontsize=16)
                
                # Data shape info
                axes[0, 0].text(0.1, 0.5, f'Shape: {data.shape[0]} rows × {data.shape[1]} columns\n'
                               f'Memory usage: {data.memory_usage(deep=True).sum()/1024:.2f} KB\n'
                               f'Data types:\n{data.dtypes.value_counts().to_string()}',
                               fontsize=12, verticalalignment='center')
                axes[0, 0].set_title('Data Information')
                axes[0, 0].axis('off')
                
                # Missing values heatmap
                if data.isnull().sum().sum() > 0:
                    sns.heatmap(data.isnull(), cbar=True, ax=axes[0, 1])
                    axes[0, 1].set_title('Missing Values Heatmap')
                else:
                    axes[0, 1].text(0.5, 0.5, 'No Missing Values', ha='center', va='center')
                    axes[0, 1].set_title('Missing Values')
                    axes[0, 1].axis('off')
                
                # Numeric columns distribution
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    data[numeric_cols].hist(bins=20, ax=axes[1, 0], alpha=0.7)
                    axes[1, 0].set_title('Numeric Columns Distribution')
                else:
                    axes[1, 0].text(0.5, 0.5, 'No Numeric Columns', ha='center', va='center')
                    axes[1, 0].axis('off')
                
                # Data sample
                axes[1, 1].axis('tight')
                axes[1, 1].axis('off')
                sample_data = data.head(5).round(3) if len(data) >= 5 else data.round(3)
                table = axes[1, 1].table(cellText=sample_data.values,
                                       colLabels=sample_data.columns,
                                       cellLoc='center', loc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                axes[1, 1].set_title('Data Sample (First 5 rows)')
                
                plt.tight_layout()
                saved_path = self._save_plot(f'database_load_{table_name}_overview.png')
                
                return {
                    'success': True,
                    'message': f'Successfully loaded {len(data)} records from table {table_name}',
                    'dataset_id': dataset_id,
                    'data_shape': data.shape,
                    'columns': list(data.columns),
                    'visualization_saved': saved_path
                }
            else:
                return {
                    'success': False,
                    'message': f'No data loaded from table {table_name}'
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Database connection error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error loading data from database: {str(e)}'
            }

    def load_csv_data(self, csv_content: str, encoding: str = 'utf-8', dataset_id: str = "default") -> Dict[str, Any]:
        """
        Load CSV data from content (can be base64 encoded or raw string).

        Args:
            csv_content (str): CSV data content.
            encoding (str): Encoding of the CSV data.

        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Try to decode base64
            try:
                csv_data = base64.b64decode(csv_content).decode(encoding)
            except:
                csv_data = csv_content

            # Create a temporary file and read
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                temp_file.write(csv_data)
                temp_file_path = temp_file.name

            # Read CSV
            data = pd.read_csv(temp_file_path)
            os.unlink(temp_file_path)
            
            # 存储到全局存储中
            data_storage.store_data(dataset_id, data, {
                'source': 'csv',
                'encoding': encoding
            })

            # Generate visualization for loaded data
            if len(data) > 0:
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                fig.suptitle('CSV Data Overview', fontsize=16)
                
                # Data info
                axes[0, 0].text(0.1, 0.5, f'Shape: {data.shape[0]} rows × {data.shape[1]} columns\n'
                               f'Memory usage: {data.memory_usage(deep=True).sum()/1024:.2f} KB\n'
                               f'Data types:\n{data.dtypes.value_counts().to_string()}',
                               fontsize=12, verticalalignment='center')
                axes[0, 0].set_title('Data Information')
                axes[0, 0].axis('off')
                
                # Missing values
                if data.isnull().sum().sum() > 0:
                    sns.heatmap(data.isnull(), cbar=True, ax=axes[0, 1])
                    axes[0, 1].set_title('Missing Values Heatmap')
                else:
                    axes[0, 1].text(0.5, 0.5, 'No Missing Values', ha='center', va='center')
                    axes[0, 1].set_title('Missing Values')
                    axes[0, 1].axis('off')
                
                # Numeric distribution
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    data[numeric_cols].hist(bins=20, ax=axes[1, 0], alpha=0.7)
                    axes[1, 0].set_title('Numeric Columns Distribution')
                else:
                    axes[1, 0].text(0.5, 0.5, 'No Numeric Columns', ha='center', va='center')
                    axes[1, 0].axis('off')
                
                # Data sample table
                axes[1, 1].axis('tight')
                axes[1, 1].axis('off')
                sample_data = data.head(5).round(3) if len(data) >= 5 else data.round(3)
                table = axes[1, 1].table(cellText=sample_data.values,
                                       colLabels=sample_data.columns,
                                       cellLoc='center', loc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                axes[1, 1].set_title('Data Sample (First 5 rows)')
                
                plt.tight_layout()
                saved_path = self._save_plot('csv_data_overview.png')
                
                return {
                    'success': True,
                    'message': f'Successfully loaded CSV data with shape {data.shape}',
                    'dataset_id': dataset_id,
                    'data_shape': data.shape,
                    'columns': list(data.columns),
                    'visualization_saved': saved_path
                }
            else:
                return {
                    'success': False,
                    'message': 'No data loaded from CSV'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error loading CSV data: {str(e)}'
            }

    def preprocess_data(self, dataset_id: str = "default", output_dataset_id: str = "") -> Dict[str, Any]:
        """
        Preprocess data by dropping rows with missing values.

        Returns:
            Dict[str, Any]: Result of the operation.
        """
        # 从全局存储获取数据
        data = data_storage.get_data(dataset_id)
        if data is None:
            return {'success': False, 'message': f'No data found with dataset_id: {dataset_id}. Please load data first.'}

        try:
            initial_shape = data.shape
            processed_data = data.dropna()
            final_shape = processed_data.shape
            
            # 存储预处理后的数据
            if output_dataset_id == "" or output_dataset_id is None:
                output_dataset_id = f"{dataset_id}_processed"
            data_storage.store_data(output_dataset_id, processed_data, {
                'source': 'preprocessing',
                'original_dataset': dataset_id,
                'preprocessing_steps': ['dropna']
            })

            # Generate preprocessing visualization
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Data Preprocessing Results', fontsize=16)
            
            # Before/After comparison
            comparison_text = f'Initial shape: {initial_shape[0]} rows × {initial_shape[1]} columns\n'
            comparison_text += f'Final shape: {final_shape[0]} rows × {final_shape[1]} columns\n'
            comparison_text += f'Rows dropped: {initial_shape[0] - final_shape[0]}\n'
            comparison_text += f'Data retention: {final_shape[0]/initial_shape[0]*100:.1f}%'
            
            axes[0, 0].text(0.1, 0.5, comparison_text, fontsize=12, verticalalignment='center')
            axes[0, 0].set_title('Before/After Comparison')
            axes[0, 0].axis('off')
            
            # Missing values before preprocessing
            if self.data.isnull().sum().sum() > 0:
                missing_counts = self.data.isnull().sum()
                missing_counts = missing_counts[missing_counts > 0]
                if len(missing_counts) > 0:
                    missing_counts.plot(kind='bar', ax=axes[0, 1])
                    axes[0, 1].set_title('Missing Values by Column (Before)')
                    axes[0, 1].tick_params(axis='x', rotation=45)
                else:
                    axes[0, 1].text(0.5, 0.5, 'No Missing Values', ha='center', va='center')
                    axes[0, 1].axis('off')
            else:
                axes[0, 1].text(0.5, 0.5, 'No Missing Values', ha='center', va='center')
                axes[0, 1].set_title('Missing Values (Before)')
                axes[0, 1].axis('off')
            
            # Data distribution comparison (if numeric columns exist)
            numeric_cols = self.processed_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                # Plot distribution of first numeric column as example
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    axes[1, 0].hist(data[col].dropna(), alpha=0.5, label='Before', bins=20)
                    axes[1, 0].hist(processed_data[col], alpha=0.5, label='After', bins=20)
                    axes[1, 0].set_title(f'Distribution Comparison: {col}')
                    axes[1, 0].legend()
                
                # Basic statistics comparison
                stats_text = 'Key Statistics (After Preprocessing):\n'
                stats_text += f'Mean: {processed_data[numeric_cols].mean().round(3).to_string()}\n'
                stats_text += f'Std: {processed_data[numeric_cols].std().round(3).to_string()}'
                
                axes[1, 1].text(0.1, 0.5, stats_text, fontsize=10, verticalalignment='center')
                axes[1, 1].set_title('Summary Statistics')
                axes[1, 1].axis('off')
            else:
                axes[1, 0].text(0.5, 0.5, 'No Numeric Columns', ha='center', va='center')
                axes[1, 0].axis('off')
                axes[1, 1].text(0.5, 0.5, 'No Statistics Available', ha='center', va='center')
                axes[1, 1].axis('off')
            
            plt.tight_layout()
            saved_path = self._save_plot('data_preprocessing.png')

            return {
                'success': True,
                'message': 'Data preprocessing completed successfully',
                'input_dataset_id': dataset_id,
                'output_dataset_id': output_dataset_id,
                'initial_shape': initial_shape,
                'final_shape': final_shape,
                'rows_dropped': initial_shape[0] - final_shape[0],
                'visualization_saved': saved_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error in data preprocessing: {str(e)}'
            }

    def feature_engineering(self, target_column: str, dataset_id: str = "default", output_dataset_id: str = "") -> Dict[str, Any]:
        """
        Perform Pearson correlation analysis.

        Args:
            target_column (str): Name of the target column.

        Returns:
            Dict[str, Any]: Result of the operation including correlation matrix.
        """
        # 从全局存储获取数据
        data = data_storage.get_data(dataset_id)
        if data is None:
            return {'success': False, 'message': f'No data found with dataset_id: {dataset_id}. Please load or preprocess data first.'}

        if target_column not in data.columns:
            return {'success': False, 'message': f'Target column "{target_column}" not found in dataset {dataset_id}.'}

        try:
            numeric_df = data.select_dtypes(include=[np.number])
            correlation_matrix = numeric_df.corr()
            
            # 存储特征工程结果
            if output_dataset_id == "" or output_dataset_id is None:
                output_dataset_id = f"{dataset_id}_features"
            data_storage.results[output_dataset_id] = {
                'correlation_matrix': correlation_matrix,
                'target_column': target_column,
                'numeric_columns': list(numeric_df.columns),
                'dataset_id': dataset_id
            }

            # Convert correlation matrix to a serializable format
            corr_dict = correlation_matrix.to_dict()
            target_correlations = correlation_matrix[target_column].abs().sort_values(ascending=False)

            # Generate feature engineering visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Feature Engineering Analysis - Target: {target_column}', fontsize=16)
            
            # Correlation heatmap
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                       square=True, ax=axes[0, 0], fmt='.2f')
            axes[0, 0].set_title('Correlation Matrix Heatmap')
            
            # Target correlation bar plot
            target_corr_filtered = target_correlations[target_correlations.index != target_column]
            if len(target_corr_filtered) > 0:
                target_corr_filtered.plot(kind='bar', ax=axes[0, 1])
                axes[0, 1].set_title(f'Correlations with {target_column}')
                axes[0, 1].tick_params(axis='x', rotation=45)
                axes[0, 1].set_ylabel('Absolute Correlation')
            else:
                axes[0, 1].text(0.5, 0.5, 'No other numeric columns', ha='center', va='center')
                axes[0, 1].axis('off')
            
            # Feature importance ranking
            feature_ranking = target_corr_filtered.head(10) if len(target_corr_filtered) > 10 else target_corr_filtered
            ranking_text = f'Top Features by Correlation with {target_column}:\n\n'
            for i, (feature, corr) in enumerate(feature_ranking.items(), 1):
                ranking_text += f'{i}. {feature}: {corr:.3f}\n'
            
            axes[1, 0].text(0.1, 0.9, ranking_text, fontsize=11, verticalalignment='top')
            axes[1, 0].set_title('Feature Importance Ranking')
            axes[1, 0].axis('off')
            
            # Scatter plot of most correlated feature vs target
            if len(target_corr_filtered) > 0:
                best_feature = target_corr_filtered.index[0]
                axes[1, 1].scatter(data[best_feature], data[target_column], alpha=0.6)
                axes[1, 1].set_xlabel(best_feature)
                axes[1, 1].set_ylabel(target_column)
                axes[1, 1].set_title(f'Scatter: {best_feature} vs {target_column}')
                
                # Add correlation coefficient to plot
                corr_coef = correlation_matrix.loc[best_feature, target_column]
                axes[1, 1].text(0.05, 0.95, f'r = {corr_coef:.3f}', transform=axes[1, 1].transAxes,
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            else:
                axes[1, 1].text(0.5, 0.5, 'No features to plot', ha='center', va='center')
                axes[1, 1].axis('off')
            
            plt.tight_layout()
            saved_path = self._save_plot(f'feature_engineering_{target_column}.png')

            return {
                'success': True,
                'message': 'Feature engineering (correlation analysis) completed successfully',
                'input_dataset_id': dataset_id,
                'output_result_id': output_dataset_id,
                'target_column': target_column,
                'correlation_matrix': corr_dict,
                'target_correlations': {k: float(v) for k, v in target_correlations.to_dict().items()},
                'visualization_saved': saved_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error in feature engineering: {str(e)}'
            }

    def train_model(self, target_column: str, dataset_id: str = "default", model_id: str = "", n_iter: int = 10) -> Dict[str, Any]:
        """
        Train an XGBoost regression model with hyperparameter optimization.

        Args:
            target_column (str): Name of the target column.
            n_iter (int): Number of iterations for RandomizedSearchCV.

        Returns:
            Dict[str, Any]: Result of the operation including model performance.
        """
        # 从全局存储获取数据
        data = data_storage.get_data(dataset_id)
        if data is None:
            return {'success': False, 'message': f'No data found with dataset_id: {dataset_id}. Please load or preprocess data first.'}

        if target_column not in data.columns:
            return {'success': False, 'message': f'Target column "{target_column}" not found in dataset {dataset_id}.'}

        try:
            X = data.drop(columns=[target_column])
            y = data[target_column]

            # Ensure X contains only numeric columns
            X = X.select_dtypes(include=[np.number])

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=RANDOM_SEED
            )

            # Define XGBoost model
            xgb_model = xgb.XGBRegressor(random_state=RANDOM_SEED)

            # Define hyperparameter search space
            param_distributions = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0]
            }

            # Perform hyperparameter optimization
            search = RandomizedSearchCV(
                xgb_model,
                param_distributions,
                n_iter=n_iter,
                cv=5,
                scoring='r2',
                n_jobs=-1,
                random_state=RANDOM_SEED
            )

            search.fit(X_train, y_train)
            model = search.best_estimator_
            
            # 存储模型
            if model_id == "" or model_id is None:
                model_id = f"{dataset_id}_{target_column}_model"
            data_storage.store_model(model_id, model, {
                'target_column': target_column,
                'dataset_id': dataset_id,
                'model_type': 'XGBoost',
                'best_params': search.best_params_,
                'cv_score': search.best_score_
            })

            # Evaluate model
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            train_mse = mean_squared_error(y_train, y_pred_train)
            test_mse = mean_squared_error(y_test, y_pred_test)
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)

            # Generate model training visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Model Training Results - Target: {target_column}', fontsize=16)
            
            # Actual vs Predicted scatter plot
            axes[0, 0].scatter(y_test, y_pred_test, alpha=0.6, label='Test')
            axes[0, 0].scatter(y_train, y_pred_train, alpha=0.4, label='Train')
            axes[0, 0].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
            axes[0, 0].set_xlabel('Actual Values')
            axes[0, 0].set_ylabel('Predicted Values')
            axes[0, 0].set_title('Actual vs Predicted')
            axes[0, 0].legend()
            
            # Model performance metrics
            metrics_text = f'Model Performance:\n\n'
            metrics_text += f'Training R²: {train_r2:.4f}\n'
            metrics_text += f'Test R²: {test_r2:.4f}\n'
            metrics_text += f'Training MSE: {train_mse:.4f}\n'
            metrics_text += f'Test MSE: {test_mse:.4f}\n\n'
            metrics_text += f'Best Parameters:\n'
            for param, value in search.best_params_.items():
                metrics_text += f'{param}: {value}\n'
            
            axes[0, 1].text(0.1, 0.9, metrics_text, fontsize=11, verticalalignment='top')
            axes[0, 1].set_title('Model Performance Metrics')
            axes[0, 1].axis('off')
            
            # Feature importance (if available)
            if hasattr(model, 'feature_importances_'):
                feature_importance = pd.Series(model.feature_importances_, index=X.columns)
                feature_importance = feature_importance.sort_values(ascending=False)
                
                # Plot top 10 features
                top_features = feature_importance.head(10)
                top_features.plot(kind='bar', ax=axes[1, 0])
                axes[1, 0].set_title('Top 10 Feature Importances')
                axes[1, 0].tick_params(axis='x', rotation=45)
                axes[1, 0].set_ylabel('Importance')
            else:
                axes[1, 0].text(0.5, 0.5, 'Feature importance not available', ha='center', va='center')
                axes[1, 0].axis('off')
            
            # Residual plot
            residuals_test = y_test - y_pred_test
            axes[1, 1].scatter(y_pred_test, residuals_test, alpha=0.6)
            axes[1, 1].axhline(y=0, color='r', linestyle='--')
            axes[1, 1].set_xlabel('Predicted Values')
            axes[1, 1].set_ylabel('Residuals')
            axes[1, 1].set_title('Residual Plot')
            
            plt.tight_layout()
            saved_path = self._save_plot(f'model_training_{target_column}.png')

            return {
                'success': True,
                'message': 'Model training completed successfully',
                'dataset_id': dataset_id,
                'model_id': model_id,
                'target_column': target_column,
                'best_params': search.best_params_,
                'train_mse': float(train_mse),
                'test_mse': float(test_mse),
                'train_r2': float(train_r2),
                'test_r2': float(test_r2),
                'train_shape': X_train.shape,
                'test_shape': X_test.shape,
                'visualization_saved': saved_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error in model training: {str(e)}'
            }

    def interpret_model(self, model_id: str, dataset_id: str = "default", sample_size: int = 100) -> Dict[str, Any]:
        """
        Perform SHAP analysis on the trained model.

        Args:
            sample_size (int): Number of samples to use for SHAP analysis.

        Returns:
            Dict[str, Any]: Result of the operation including SHAP values.
        """
        # 从全局存储获取模型和数据
        model = data_storage.get_model(model_id)
        if model is None:
            return {'success': False, 'message': f'No trained model found with model_id: {model_id}. Please train a model first.'}
        
        data = data_storage.get_data(dataset_id)
        if data is None:
            return {'success': False, 'message': f'No data found with dataset_id: {dataset_id}.'}
        
        # 获取模型元数据
        model_metadata = data_storage.models[model_id]['metadata']
        target_column = model_metadata.get('target_column')
        
        if not target_column or target_column not in data.columns:
            return {'success': False, 'message': 'Target column information not available or not found in dataset.'}

        try:
            X = data.drop(columns=[target_column])
            X = X.select_dtypes(include=[np.number])

            # Sample data for SHAP analysis if dataset is large
            if len(X) > sample_size:
                X_sample = X.sample(n=sample_size, random_state=RANDOM_SEED)
            else:
                X_sample = X

            # Create SHAP explainer
            shap_explainer = shap.TreeExplainer(model)
            shap_values = shap_explainer.shap_values(X_sample)

            # Calculate mean absolute SHAP values for feature importance
            mean_shap_values = np.abs(shap_values).mean(0)
            feature_importance = dict(zip(X_sample.columns, mean_shap_values))

            # Generate SHAP visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'SHAP Model Interpretation - Target: {target_column}', fontsize=16)
            
            # SHAP feature importance bar plot
            feature_importance_sorted = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            top_features = dict(list(feature_importance_sorted.items())[:10])
            
            bars = axes[0, 0].bar(range(len(top_features)), list(top_features.values()))
            axes[0, 0].set_xticks(range(len(top_features)))
            axes[0, 0].set_xticklabels(list(top_features.keys()), rotation=45)
            axes[0, 0].set_title('SHAP Feature Importance (Top 10)')
            axes[0, 0].set_ylabel('Mean |SHAP value|')
            
            # Color bars by importance
            max_val = max(top_features.values())
            for bar, val in zip(bars, top_features.values()):
                bar.set_color(plt.cm.viridis(val / max_val))
            
            # SHAP summary text
            summary_text = f'SHAP Analysis Summary:\n\n'
            summary_text += f'Sample size: {len(X_sample)} observations\n'
            summary_text += f'Features analyzed: {len(X_sample.columns)}\n\n'
            summary_text += f'Top 5 Most Important Features:\n'
            for i, (feature, importance) in enumerate(list(feature_importance_sorted.items())[:5], 1):
                summary_text += f'{i}. {feature}: {importance:.4f}\n'
            
            axes[0, 1].text(0.1, 0.9, summary_text, fontsize=11, verticalalignment='top')
            axes[0, 1].set_title('SHAP Analysis Summary')
            axes[0, 1].axis('off')
            
            # SHAP values distribution for most important feature
            if len(feature_importance_sorted) > 0:
                most_important_feature = list(feature_importance_sorted.keys())[0]
                feature_idx = list(X_sample.columns).index(most_important_feature)
                shap_values_feature = shap_values[:, feature_idx]
                
                axes[1, 0].hist(shap_values_feature, bins=20, alpha=0.7, edgecolor='black')
                axes[1, 0].set_xlabel('SHAP Value')
                axes[1, 0].set_ylabel('Frequency')
                axes[1, 0].set_title(f'SHAP Values Distribution: {most_important_feature}')
                axes[1, 0].axvline(x=0, color='red', linestyle='--', alpha=0.7)
            else:
                axes[1, 0].text(0.5, 0.5, 'No features available', ha='center', va='center')
                axes[1, 0].axis('off')
            
            # Feature correlation with SHAP values (for most important feature)
            if len(feature_importance_sorted) > 0:
                most_important_feature = list(feature_importance_sorted.keys())[0]
                feature_idx = list(X_sample.columns).index(most_important_feature)
                feature_values = X_sample[most_important_feature].values
                shap_values_feature = shap_values[:, feature_idx]
                
                scatter = axes[1, 1].scatter(feature_values, shap_values_feature, 
                                           c=feature_values, cmap='viridis', alpha=0.6)
                axes[1, 1].set_xlabel(f'{most_important_feature} (Feature Value)')
                axes[1, 1].set_ylabel('SHAP Value')
                axes[1, 1].set_title(f'Feature Value vs SHAP Value: {most_important_feature}')
                axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
                
                # Add colorbar
                plt.colorbar(scatter, ax=axes[1, 1], label='Feature Value')
            else:
                axes[1, 1].text(0.5, 0.5, 'No features to plot', ha='center', va='center')
                axes[1, 1].axis('off')
            
            plt.tight_layout()
            saved_path = self._save_plot(f'shap_interpretation_{target_column}.png')

            return {
                'success': True,
                'message': 'Model interpretation (SHAP analysis) completed successfully',
                'model_id': model_id,
                'dataset_id': dataset_id,
                'target_column': target_column,
                'feature_importance': {k: float(v) for k, v in feature_importance.items()},
                'sample_size': len(X_sample),
                'visualization_saved': saved_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error in model interpretation: {str(e)}'
            }



# 创建全局实例
data_analysis_tool = DataAnalysisBase()


@mcp.tool()
def load_data_from_database(table_name: str, conditions_json: str = "[]", 
                           page_size: int = 1000, dataset_id: str = "default") -> Dict[str, Any]:
    """
    从数据库加载数据 - 独立工具，不依赖其他步骤

    Args:
        table_name (str): 数据库表名
        conditions_json (str): 查询条件JSON字符串
        page_size (int): 最大记录数
        dataset_id (str): 数据集ID，用于标识和存储数据

    Returns:
        Dict[str, Any]: 加载结果
    """
    return data_analysis_tool.load_data_from_database(table_name, conditions_json, page_size, dataset_id)


@mcp.tool()
def load_data_from_csv(csv_content: str, encoding: str = 'utf-8', dataset_id: str = "default") -> Dict[str, Any]:
    """
    从 CSV 加载数据 - 独立工具，不依赖其他步骤

    Args:
        csv_content (str): CSV数据内容
        encoding (str): 编码格式
        dataset_id (str): 数据集ID

    Returns:
        Dict[str, Any]: 加载结果
    """
    return data_analysis_tool.load_csv_data(csv_content, encoding, dataset_id)


@mcp.tool()
def preprocess_data(dataset_id: str = "default", output_dataset_id: str = "") -> Dict[str, Any]:
    """
    数据预处理 - 独立工具，可指定任意数据集

    Args:
        dataset_id (str): 输入数据集ID
        output_dataset_id (str): 输出数据集ID，默认为{dataset_id}_processed

    Returns:
        Dict[str, Any]: 预处理结果
    """
    return data_analysis_tool.preprocess_data(dataset_id, output_dataset_id)


@mcp.tool()
def feature_engineering(target_column: str, dataset_id: str = "default", output_dataset_id: str = "") -> Dict[str, Any]:
    """
    特征工程 - 独立工具，直接对指定数据集进行分析

    Args:
        target_column (str): 目标列名
        dataset_id (str): 数据集ID
        output_dataset_id (str): 结果存储ID

    Returns:
        Dict[str, Any]: 特征分析结果
    """
    return data_analysis_tool.feature_engineering(target_column, dataset_id, output_dataset_id)


@mcp.tool()
def train_model(target_column: str, dataset_id: str = "default", model_id: str = "", n_iter: int = 10) -> Dict[str, Any]:
    """
    模型训练 - 独立工具，直接在指定数据集上训练模型

    Args:
        target_column (str): 目标列名
        dataset_id (str): 数据集ID
        model_id (str): 模型ID，默认为{dataset_id}_{target_column}_model
        n_iter (int): 超参数优化迭代次数

    Returns:
        Dict[str, Any]: 训练结果
    """
    return data_analysis_tool.train_model(target_column, dataset_id, model_id, n_iter)


@mcp.tool()
def interpret_model(model_id: str, dataset_id: str = "default", sample_size: int = 100) -> Dict[str, Any]:
    """
    模型解释 - 独立工具，对指定模型进行 SHAP 分析

    Args:
        model_id (str): 模型ID
        dataset_id (str): 数据集ID（用于获取特征数据）
        sample_size (int): SHAP分析样本数

    Returns:
        Dict[str, Any]: 模型解释结果
    """
    return data_analysis_tool.interpret_model(model_id, dataset_id, sample_size)


@mcp.tool()
def list_datasets() -> Dict[str, Any]:
    """
    列出所有已加载的数据集

    Returns:
        Dict[str, Any]: 数据集列表和信息
    """
    datasets_info = {}
    for dataset_id, dataset_info in data_storage.datasets.items():
        datasets_info[dataset_id] = {
            'shape': dataset_info['data'].shape,
            'columns': list(dataset_info['data'].columns),
            'metadata': dataset_info['metadata'],
            'timestamp': dataset_info['timestamp']
        }
    
    return {
        'success': True,
        'datasets': datasets_info,
        'count': len(datasets_info)
    }


@mcp.tool()
def list_models() -> Dict[str, Any]:
    """
    列出所有已训练的模型

    Returns:
        Dict[str, Any]: 模型列表和信息
    """
    models_info = {}
    for model_id, model_info in data_storage.models.items():
        models_info[model_id] = {
            'metadata': model_info['metadata'],
            'timestamp': model_info['timestamp']
        }
    
    return {
        'success': True,
        'models': models_info,
        'count': len(models_info)
    }


@mcp.tool()
def get_dataset_info(dataset_id: str) -> Dict[str, Any]:
    """
    获取指定数据集的详细信息

    Args:
        dataset_id (str): 数据集ID

    Returns:
        Dict[str, Any]: 数据集详细信息
    """
    data = data_storage.get_data(dataset_id)
    if data is None:
        return {
            'success': False,
            'message': f'Dataset {dataset_id} not found'
        }
    
    dataset_info = data_storage.datasets[dataset_id]
    
    return {
        'success': True,
        'dataset_id': dataset_id,
        'shape': data.shape,
        'columns': list(data.columns),
        'data_types': data.dtypes.to_dict(),
        'missing_values': data.isnull().sum().to_dict(),
        'metadata': dataset_info['metadata'],
        'timestamp': dataset_info['timestamp'],
        'sample_data': data.head().to_dict('records')
    }


# 保留兼容性接口 - 使用默认参数
def SimplifiedDataAnalysisTool():
    """兼容性函数，返回全局实例"""
    return data_analysis_tool


if __name__ == "__main__":
    mcp.run(transport="sse")