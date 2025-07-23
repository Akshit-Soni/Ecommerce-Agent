"""Groq API client implementation for the E-commerce AI Agent.

This module provides a wrapper for the Groq API to handle LLM interactions.
"""

import logging
from typing import Optional, Dict, Any
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)

class GroqClient:
    """Groq API client for LLM interactions.
    
    Handles API calls to Groq's LLM service for SQL query generation
    and natural language processing tasks.
    """
    
    def __init__(self):
        """Initialize Groq client with API configuration."""
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = settings.model_timeout
        
        # Default headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(self, 
                           endpoint: str, 
                           payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make async HTTP request to Groq API.
        
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
                url = f"{self.base_url}/{endpoint}"
                logger.info(f"Making request to: {url}")
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Groq API request failed: {e}")
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
        # Construct prompt for SQL generation
        prompt = f"""You are a SQLite expert. Given the following table schemas:

{table_schema}

Write a single, valid SQLite query to answer the question: "{question}"

- Use only the provided table and column names.
- Do not add any comments or explanations.

Query:"""

        try:
            response = await self._make_request(
                "chat/completions",
                {
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": "You are a SQLite expert. Given a question and a database schema, generate a valid SQLite query to answer the question."},

                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": 500,
                    "n": 1,
                    "stream": False
                }
            )
            
            # Extract SQL from response
            if response and 'choices' in response:
                sql = response['choices'][0]['message']['content'].strip()
                logger.info(f"Generated SQL query: {sql}")
                return sql
            return None
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return None
    
    async def analyze_visualization_need(self, 
                                       question: str,
                                       sql_result: str) -> str:
        """Analyze if the query result needs visualization.
        
        Args:
            question: Original user question
            sql_result: SQL query result as a string
            
        Returns:
            str: Visualization configuration as a JSON string
        """
        prompt = f"""Analyze this question and its SQL result to determine if visualization would be helpful:

Question: {question}
Result: {sql_result}

If visualization would help, specify:
1. Chart type (bar, line, pie, etc.)
2. X and Y axis columns
3. Any additional styling

Respond in JSON format only."""

        try:
            response = await self._make_request(
                "chat/completions",
                {
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": "You are a data visualization expert. Analyze data and suggest appropriate visualizations."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 250,
                    "n": 1,
                    "stream": False,
                    "response_format": {"type": "json_object"}
                }
            )
            
            if response and 'choices' in response:
                return response['choices'][0]['message']['content']
            return '{"needs_visualization": false}'
            
        except Exception as e:
            logger.error(f"Visualization analysis failed: {e}")
            return '{"needs_visualization": false}'

# Create global Groq client instance
groq_client = GroqClient()