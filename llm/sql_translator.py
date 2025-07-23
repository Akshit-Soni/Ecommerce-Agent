"""SQL translation service for the E-commerce AI Agent.

This module handles the conversion of natural language questions to SQL queries
using various LLM providers (Groq, Gemini, Ollama) with fallback support.
"""

import json
import logging
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from .groq_client import groq_client
from db.loader import loader
from config.settings import settings

logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    """Supported LLM providers."""
    GROQ = "groq"
    GEMINI = "gemini"
    OLLAMA = "ollama"

class SQLTranslator:
    """Translates natural language questions to SQL queries.
    
    Features:
    - Multi-provider support (Groq, Gemini, Ollama)
    - Automatic fallback on failure
    - Query validation and safety checks
    - Result interpretation
    """
    
    def __init__(self):
        """Initialize SQL translator with configured provider."""
        self.default_provider = ModelProvider(settings.default_model)
        self.current_provider = self.default_provider
    
    def _get_table_schemas(self) -> Dict[str, Any]:
        """Get schema information for all tables.
        
        Returns:
            Dict[str, Any]: Schema information for all tables
        """
        schemas = {}
        for table in loader.list_tables():
            schemas[table] = loader.get_table_info(table)
        return schemas
    
    def _validate_sql(self, sql: str) -> bool:
        """Validate SQL query for safety and correctness.
        
        Args:
            sql: SQL query string
            
        Returns:
            bool: True if query is valid
        """
        # Basic safety checks
        dangerous_keywords = [
            "DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT",
            "ALTER", "EXEC", "EXECUTE", "UNION"
        ]
        
        sql_upper = sql.upper()
        if any(keyword in sql_upper for keyword in dangerous_keywords):
            logger.warning(f"Dangerous SQL detected: {sql}")
            return False
        
        # This validation is basic. For a real-world application, a proper
        # SQL parser should be used.
        return True
    
    async def translate_to_sql(self, 
                              question: str,
                              provider: Optional[ModelProvider] = None) -> Tuple[Optional[str], Dict[str, Any]]:
        """Convert natural language question to SQL query.
        
        Args:
            question: User's natural language question
            provider: Optional specific provider to use
            
        Returns:
            Tuple[Optional[str], Dict[str, Any]]: SQL query and metadata
        """
        self.current_provider = provider or self.default_provider
        schemas = self._get_table_schemas()
        
        try:
            if self.current_provider == ModelProvider.GROQ:
                sql = await groq_client.generate_sql(question, schemas)
            # elif self.current_provider == ModelProvider.GEMINI:
            #     sql = await gemini_client.generate_sql(question, schemas)
            # elif self.current_provider == ModelProvider.OLLAMA:
            #     sql = await ollama_client.generate_sql(question, schemas)
            else:
                raise ValueError(f"Unsupported provider: {self.current_provider}")
            
            if not sql:
                raise Exception("Failed to generate SQL query")
            
            # Validate generated SQL
            if not self._validate_sql(sql):
                raise ValueError("Generated SQL failed validation")
            
            return sql, {
                "provider": self.current_provider,
                "schema_used": schemas,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"SQL translation failed with {self.current_provider}: {e}")
            
            # Fallback is disabled for now to isolate the issue.
            
            return None, {
                "provider": self.current_provider,
                "error": str(e),
                "success": False
            }
    
    async def analyze_visualization(self,
                                  question: str,
                                  sql_result: Any) -> str:
        """Determine if and how to visualize query results.
        
        Args:
            question: Original user question
            sql_result: SQL query execution result
            
        Returns:
            str: Visualization configuration as a JSON string
        """
        try:
            if self.current_provider == ModelProvider.GROQ:
                return await groq_client.analyze_visualization_need(
                    question, sql_result)
            
            return json.dumps({"needs_visualization": False})
            
        except Exception as e:
            logger.error(f"Visualization analysis failed: {e}")
            return json.dumps({"needs_visualization": False})

# Create global translator instance
translator = SQLTranslator()