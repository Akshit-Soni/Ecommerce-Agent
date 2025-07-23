"""SQL translation service for the E-commerce AI Agent.

This module handles the conversion of natural language questions to SQL queries
using various LLM providers (Groq, Gemini, Ollama) with fallback support.
"""

import json
import logging
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from llm.groq_client import GroqClient
from llm.ollama_client import OllamaClient
from llm.gemini_client import GeminiClient
from db.loader import loader

logger = logging.getLogger(__name__)

groq_client = GroqClient()
ollama_client = OllamaClient()
gemini_client = GeminiClient()

class ModelProvider(str, Enum):
    """Supported LLM providers."""
    GROQ = "groq"
    OLLAMA = "ollama"
    GEMINI = "gemini"

def _get_table_schemas() -> Dict[str, Any]:
    """Get schema information for all tables.
    
    Returns:
        Dict[str, Any]: Schema information for all tables
    """
    schemas = {}
    for table in loader.list_tables():
        schemas[table] = loader.get_table_info(table)
    return schemas

def _validate_sql(sql: str) -> bool:
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
    
async def translate_to_sql(
    question: str, 
    provider: ModelProvider = ModelProvider.GROQ
) -> Tuple[Optional[str], Dict[str, Any]]:
    """Convert natural language question to SQL query.
    
    Args:
        question: User's natural language question
        provider: Optional specific provider to use
        
    Returns:
        Tuple[Optional[str], Dict[str, Any]]: SQL query and metadata
    """
    schemas = _get_table_schemas()
    
    try:
        if provider == ModelProvider.GROQ:
            sql = await groq_client.generate_sql(question, schemas)
        elif provider == ModelProvider.OLLAMA:
            sql = await ollama_client.generate_sql(question, schemas)
        elif provider == ModelProvider.GEMINI:
            sql = await gemini_client.generate_sql(question, schemas)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if not sql:
            raise Exception("Failed to generate SQL query")
        
        # Validate generated SQL
        if not _validate_sql(sql):
            raise ValueError("Generated SQL failed validation")
        
        return sql, {
            "provider": provider,
            "schema_used": schemas,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"SQL translation failed with {provider}: {e}")
        
        # Fallback is disabled for now to isolate the issue.
        
        return None, {
            "provider": provider,
            "error": str(e),
            "success": False
        }
    
async def analyze_visualization(
    question: str,
    sql_result: Any,
    provider: ModelProvider = ModelProvider.GROQ
) -> str:
    """Determine if and how to visualize query results.
    
    Args:
        question: Original user question
        sql_result: SQL query execution result
        provider: The provider to use for analysis
        
    Returns:
        str: Visualization configuration as a JSON string
    """
    try:
        if provider == ModelProvider.GROQ:
            return await groq_client.analyze_visualization_need(question, sql_result)
        elif provider == ModelProvider.GEMINI:
            return await gemini_client.analyze_visualization_need(question, sql_result)
        
        # Ollama does not currently support visualization analysis
        return json.dumps({"needs_visualization": False})
        
    except Exception as e:
        logger.error(f"Visualization analysis failed: {e}")
        return json.dumps({"needs_visualization": False})