"""Data visualization module for the E-commerce AI Agent.

This module handles the creation of dynamic plots based on SQL query results
using matplotlib or plotly, with automatic chart type selection.
"""

import base64
from io import BytesIO
import json
import logging
from typing import Dict, Any, Optional

import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)

class Plotter:
    """Handles dynamic visualization of query results.
    
    Features:
    - Automatic chart type selection
    - Dynamic axis mapping
    - Base64 image encoding
    - Multiple chart types support
    """
    
    def __init__(self):
        """Initialize plotter with default style settings."""
        # Set default style
        plt.style.use('seaborn-v0_8')
        self.default_figsize = (10, 6)
        self.default_dpi = 100
    
    def _create_bar_chart(self, 
                         df: pd.DataFrame,
                         x_col: str,
                         y_col: str,
                         title: str = "") -> None:
        """Create a bar chart.
        
        Args:
            df: Pandas DataFrame with the data
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
        """
        plt.figure(figsize=self.default_figsize)
        plt.bar(df[x_col], df[y_col])
        plt.title(title)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    def _create_line_chart(self,
                          df: pd.DataFrame,
                          x_col: str,
                          y_col: str,
                          title: str = "") -> None:
        """Create a line chart.
        
        Args:
            df: Pandas DataFrame with the data
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
        """
        plt.figure(figsize=self.default_figsize)
        plt.plot(df[x_col], df[y_col], marker='o')
        plt.title(title)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    def _create_pie_chart(self,
                         df: pd.DataFrame,
                         value_col: str,
                         label_col: str,
                         title: str = "") -> None:
        """Create a pie chart.
        
        Args:
            df: Pandas DataFrame with the data
            value_col: Column for values
            label_col: Column for labels
            title: Chart title
        """
        plt.figure(figsize=self.default_figsize)
        plt.pie(df[value_col], labels=df[label_col], autopct='%1.1f%%')
        plt.title(title)
        plt.axis('equal')
    
    def _convert_to_base64(self) -> str:
        """Convert the current plot to base64 string.
        
        Returns:
            str: Base64 encoded image string
        """
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=self.default_dpi)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        return img_base64
    
    def create_plot(self,
                    data: Dict[str, Any],
                    viz_config: Dict[str, Any]) -> Optional[str]:
        """Create a visualization based on data and configuration.
        
        Args:
            data: Query result data
            viz_config: Visualization configuration from LLM
            
        Returns:
            Optional[str]: Base64 encoded image string if successful
        """
        try:
            # Convert data to DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Extract visualization parameters
            chart_type = viz_config.get('chart_type', '').lower()
            x_axis = viz_config.get('x_axis')
            y_axis = viz_config.get('y_axis')
            title = viz_config.get('title', '')
            
            if not all([chart_type, x_axis, y_axis]):
                logger.error("Missing required visualization parameters")
                return None
            
            # Create appropriate chart
            if chart_type == 'bar':
                self._create_bar_chart(df, x_axis, y_axis, title)
            elif chart_type == 'line':
                self._create_line_chart(df, x_axis, y_axis, title)
            elif chart_type == 'pie':
                self._create_pie_chart(df, y_axis, x_axis, title)
            else:
                logger.error(f"Unsupported chart type: {chart_type}")
                return None
            
            # Convert to base64
            return self._convert_to_base64()
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return None

# Create global plotter instance
plotter = Plotter()