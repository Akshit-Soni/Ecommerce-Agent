"""CSV data loader and database schema management for the E-commerce AI Agent.

This module handles loading CSV files into SQLite tables with dynamic schema creation.
"""

import pandas as pd
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .connection import db

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading CSV data into SQLite database with dynamic schema creation.
    
    Features:
    - Automatic schema detection from CSV headers
    - Data type inference
    - Table creation and data insertion
    - Schema validation and column mapping
    """
    
    def __init__(self):
        """Initialize the data loader."""
        self.table_schemas: Dict[str, Dict] = {}
    
    def _infer_sql_type(self, dtype: str) -> str:
        """Convert pandas dtype to SQLite type.
        
        Args:
            dtype: Pandas data type string
            
        Returns:
            str: Corresponding SQLite type
        """
        if 'int' in dtype:
            return 'INTEGER'
        elif 'float' in dtype:
            return 'REAL'
        elif 'bool' in dtype:
            return 'BOOLEAN'
        elif 'datetime' in dtype:
            return 'TIMESTAMP'
        else:
            return 'TEXT'
    
    def _create_table_schema(self, df: pd.DataFrame, table_name: str) -> str:
        """Generate SQL create table statement from DataFrame.
        
        Args:
            df: Pandas DataFrame
            table_name: Name for the new table
            
        Returns:
            str: SQL create table statement
        """
        columns = []
        for col, dtype in df.dtypes.items():
            sql_type = self._infer_sql_type(str(dtype))
            # Clean column name and make it SQL-safe
            clean_col = col.strip().replace(' ', '_').lower()
            columns.append(f'"{clean_col}" {sql_type}')
        
        # Store schema for future reference
        self.table_schemas[table_name] = {
            'columns': df.columns.tolist(),
            'types': df.dtypes.to_dict()
        }
        
        # Create the SQL statement without using backslashes in f-string
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        return create_table_sql
    
    def load_csv(self, 
                 file_path: Path, 
                 table_name: str,
                 column_mapping: Optional[Dict[str, str]] = None) -> bool:
        """Load CSV file into SQLite database.
        
        Args:
            file_path: Path to CSV file
            table_name: Name for the database table
            column_mapping: Optional mapping of CSV columns to table columns
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            pd.errors.EmptyDataError: If CSV file is empty
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Apply column mapping if provided
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # Clean column names
            df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
            
            # Create table
            create_table_sql = self._create_table_schema(df, table_name)
            
            with db.get_cursor() as cursor:
                # Create table
                cursor.execute(create_table_sql)
                
                # Insert data
                df.to_sql(
                    name=table_name,
                    con=cursor.connection,
                    if_exists='replace',
                    index=False
                )
            
            logger.info(f"Successfully loaded {len(df)} rows into table {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV {file_path} into table {table_name}: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict:
        """Get table schema information.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dict: Table schema information
        """
        with db.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            return {
                'name': table_name,
                'columns': [dict(col) for col in columns]
            }
    
    def list_tables(self) -> List[str]:
        """Get list of all tables in database.
        
        Returns:
            List[str]: List of table names
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            return [row[0] for row in cursor.fetchall()]

# Create global data loader instance
loader = DataLoader()