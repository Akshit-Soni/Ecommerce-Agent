"""Gemini API client implementation for the E-commerce AI Agent.

This module provides a wrapper for the Google Gemini API to handle LLM interactions.
"""

import logging
from typing import Optional, Dict, Any
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini API client for LLM interactions.
    
    Handles API calls to Google's Gemini LLM service for SQL query generation.
    """
    
    def __init__(self):
        """Initialize Gemini client with API configuration."""
        self.api_key = settings.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        self.timeout = settings.model_timeout
        
        self.headers = {
            "Content-Type": "application/json",
        }
    
    async def _make_request(self, 
                           payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make async HTTP request to Gemini API.
        
        Args:
            payload: Request payload
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = f"{self.base_url}?key={self.api_key}"
                logger.info(f"Making request to: {url}")
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Gemini API request failed: {e}")
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
                {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": 500
                    }
                }
            )
            
            if response and 'candidates' in response:
                sql = response['candidates'][0]['content']['parts'][0]['text'].strip()
                logger.info(f"Generated SQL query: {sql}")
                # Helper to remove markdown and extract pure SQL
                if '```' in sql:
                    sql = sql.split('```')[1]
                    if sql.startswith('sqlite'):
                        sql = sql[len('sqlite'):].strip()
                return sql.strip()
            return None
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return None

gemini_client = GeminiClient()