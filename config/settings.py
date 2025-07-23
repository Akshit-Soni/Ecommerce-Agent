"""Configuration management for the E-commerce AI Agent.

This module handles all configuration settings and environment variables for the application.
It uses pydantic for validation and python-dotenv for environment variable management.
"""

from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directory of the project
BASE_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    """Application settings and configuration.
    
    Attributes:
        groq_api_key: API key for Groq LLM service
        gemini_api_key: API key for Google's Gemini LLM service
        db_path: SQLite database path
        api_host: Host address for the FastAPI server
        api_port: Port number for the FastAPI server
        debug_mode: Enable debug mode
        rate_limit_calls: Number of allowed calls per period
        rate_limit_period: Time period for rate limiting in seconds
        enable_visualization: Toggle for visualization features
        enable_streaming: Toggle for response streaming
        default_model: Default LLM model to use
        model_timeout: Timeout for model API calls in seconds
        log_level: Logging level
        log_file: Log file path
    """
    
    # LLM API Keys
    groq_api_key: str = Field(..., description="Groq API key")
    gemini_api_key: str = Field(None, description="Gemini API key")
    
    # Database
    db_path: str = Field("sqlite:///ecom_data.db", description="SQLite database path")
    
    # API Settings
    api_host: str = Field("0.0.0.0", description="API host address")
    api_port: int = Field(8000, description="API port number")
    debug_mode: bool = Field(False, description="Debug mode toggle")
    
    # Rate Limiting
    rate_limit_calls: int = Field(5, description="Rate limit calls per period")
    rate_limit_period: int = Field(60, description="Rate limit period in seconds")
    
    # Features
    enable_visualization: bool = Field(True, description="Enable visualization features")
    enable_streaming: bool = Field(False, description="Enable response streaming")
    
    # Model Configuration
    default_model: Literal["groq", "gemini", "ollama"] = Field(
        "groq", description="Default LLM model")
    model_timeout: int = Field(30, description="Model API timeout in seconds")
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", description="Logging level")
    log_file: str = Field("app.log", description="Log file path")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Create global settings instance
settings = Settings()

# Computed paths
DB_FILE_PATH = BASE_DIR / "ecom_data.db"
LOG_FILE_PATH = BASE_DIR / settings.log_file