"""
Configuration management for PhishGuard AI.
Loads settings from environment variables with validation and type safety.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from exceptions import ConfigurationError


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # API Configuration
    groq_api_key: str = Field(
        default="",
        description="Groq API key for LLM access"
    )
    
    # Model Configuration
    embedding_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model name"
    )
    
    llm_model_name: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq LLM model name"
    )
    
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM temperature for response randomness"
    )
    
    # Vector Database Configuration
    vector_db_path: str = Field(
        default="sirket_vektor_db",
        description="Path to FAISS vector database"
    )
    
    # RAG Configuration
    rag_top_k: int = Field(
        default=2,
        ge=1,
        description="Number of top similar documents to retrieve"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    log_dir: str = Field(
        default="logs",
        description="Directory for log files"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper
    
    def validate_api_key(self) -> None:
        """Validate that API key is set and not a placeholder."""
        if not self.groq_api_key or self.groq_api_key == "your_groq_api_key_here":
            raise ConfigurationError(
                "Groq API key not configured",
                "Please set GROQ_API_KEY in your .env file or environment variables"
            )
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
    def get_vector_db_full_path(self) -> Path:
        """Get the full path to the vector database."""
        return Path(self.vector_db_path).absolute()


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
        _config.ensure_directories()
    return _config


def set_api_key(api_key: str) -> None:
    """Set the API key at runtime (useful for Streamlit app)."""
    global _config
    if _config is None:
        _config = Config()
    _config.groq_api_key = api_key
    os.environ["GROQ_API_KEY"] = api_key
