"""Configuration settings for Clinical Question Copilot."""

import os
from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""
    
    # API Configuration
    openai_api_key: Optional[str] = None
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_persist_directory: str = "./chroma_db"
    log_level: str = "INFO"
    
    
    # Clinical Knowledge Base
    mimic_data_path: str = "./data/mimic_demo"
    max_context_length: int = 4000
    similarity_threshold: float = 0.15
    top_k_results: int = 10
    top_k_context: int = 6
    
    
    # Guardrails
    clinical_keywords: list = [
        "icu", "intensive care", "hospital", "clinical", "medical", "patient",
        "diagnosis", "treatment", "therapy", "medication", "drug", "surgery",
        "ventilator", "respiratory", "cardiac", "neurological", "sepsis",
        "acidosis", "ards", "blood gas", "vital signs", "monitoring",
        "protocol", "guideline", "standard", "criteria", "threshold",
        "vasopressor", "vasopressors", "pressor", "pressors", "vasopressin",
        "inotrope", "inotropes", "dobutamine", "norepinephrine",
        "shock", "cardiogenic shock", "titrate", "wean"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
