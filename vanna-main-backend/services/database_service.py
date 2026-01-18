"""
Database Service - Single Responsibility: Database connection management.
SOLID: Single Responsibility Principle
"""
import sqlite3
from typing import Optional
from contextlib import contextmanager


class DatabaseService:
    """Service for managing database connections."""
    
    def __init__(self, db_path: str):
        """
        Initialize database service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection cleanup.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of row dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT query and return the last row ID.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Last inserted row ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def get_database_schema(self, vn) -> str:
        """
        Get the database schema DDL using Vanna's run_sql.
        
        Args:
            vn: Vanna instance
            
        Returns:
            str: Combined DDL statements for all tables
        """
        # SQLite specific query as requested
        query = "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        
        try:
            df = vn.run_sql(query)
            
            if df is None or df.empty:
                return "-- No schema found or empty database."
                
            ddl_parts = []
            for _, row in df.iterrows():
                if row['sql']:
                    ddl_parts.append(row['sql'] + ";")
                    
            return "\n\n".join(ddl_parts)
        except Exception as e:
            print(f"Error getting schema: {e}")
            return f"-- Error fetching schema: {str(e)}"
