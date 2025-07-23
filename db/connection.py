"""Database connection management for the E-commerce AI Agent.

This module provides a connection pool and context manager for SQLite database operations.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator
import logging
from config.settings import DB_FILE_PATH

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages SQLite database connections and operations.
    
    Provides connection pooling and context management for database operations.
    Ensures proper connection handling and resource cleanup.
    """
    
    def __init__(self, db_path: str = str(DB_FILE_PATH)):
        """Initialize database connection manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Create and yield a database connection.
        
        Yields:
            sqlite3.Connection: Active database connection
            
        Raises:
            sqlite3.Error: If connection fails
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable foreign key support
            conn.execute("PRAGMA foreign_keys = ON")
            # Return dictionary-like rows
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Create and yield a database cursor.
        
        Yields:
            sqlite3.Cursor: Active database cursor
            
        Raises:
            sqlite3.Error: If cursor creation fails
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database operation error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            list[sqlite3.Row]: Query results
            
        Raises:
            sqlite3.Error: If query execution fails
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_many(self, query: str, params: list[tuple]) -> None:
        """Execute a SQL query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params: List of parameter tuples
            
        Raises:
            sqlite3.Error: If query execution fails
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params)

# Create global database connection instance
db = DatabaseConnection()