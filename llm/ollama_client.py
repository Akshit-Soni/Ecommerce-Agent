"""Ollama API client implementation for the E-commerce AI Agent.

This module provides a wrapper for a local Ollama instance to handle LLM interactions.
"""

import logging
from typing import Optional, Dict, Any
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    """Ollama API client for LLM interactions.
    
    Handles API calls to a local Ollama instance for SQL query generation.
    """
    
    def __init__(self):
        """Initialize Ollama client with API configuration."""
        self.base_url = settings.ollama_base_url
        self.timeout = settings.model_timeout
        
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(self, 
                           endpoint: str, 
                           payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make async HTTP request to Ollama API.
        
        Args:
            endpoint: API endpoint path
            payload: Request payload
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"{self.base_url}{endpoint}"
                logger.info(f"Making request to: {url}")
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Ollama API request failed: {e}")
                try:
                    logger.error(f"Response content: {response.text}")
                except NameError:
                    pass
                raise
    
    async def generate_sql(self, 
                          question: str,
                          table_schema: Dict[str, Any],
                          temperature: float = 0.1) -> Optional[str]:
        """Generate SQL query from natural language question.
        
        Args:
            question: User's natural language question
            table_schema: Database schema information
            temperature: Model temperature (0.0 to 1.0)
            
        Returns:
            Optional[str]: Generated SQL query or None if generation fails
        """
        prompt = f"""You are a SQLite expert. Given the following table schemas:

{table_schema}

Write a single, valid SQLite query to answer the question: "{question}"

- Use only the provided table and column names.
- Do not add any comments or explanations.

Query:"""

        try:
            response = await self._make_request(
                "/api/generate",
                {
                    "model": "gemma:2b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                }
            )
            
            if response and 'response' in response:
                sql_query = response['response'].strip()
                # The response from ollama might include the prompt, so we clean it
                if 'Query:' in sql_query:
                    sql_query = sql_query.split('Query:')[1].strip()
                return sql_query
            return None
        except Exception as e:
            logger.error(f"Failed to generate SQL with Ollama: {e}")
            return None

ollama_client = OllamaClient()