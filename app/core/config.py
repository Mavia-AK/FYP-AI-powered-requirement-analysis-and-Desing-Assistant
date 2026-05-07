"""
Configuration settings for AI-RADA application
"""
import os
from typing import Optional

# ── API Keys ──────────────────────────────────────────────────────────────────

# Gemini API Configuration
GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')

# ── Model Settings ────────────────────────────────────────────────────────────

# Ambiguity Classification Model
AMBIGUITY_MODEL_PATH = "models/ambiguity/"
CLASSIFICATION_MODEL_PATH = "models/classification_final/"

# ── Data Paths ────────────────────────────────────────────────────────────────

DATA_DIR = "data/"
RAW_DATA_PATH = "data/raw/ambiguity_dataset.csv"
PROCESSED_DATA_DIR = "data/processed/"

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_DIR = "logs/"
LOG_LEVEL = "INFO"

# ── UI Settings ───────────────────────────────────────────────────────────────

MAX_FILE_SIZE_MB = 10
SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.xlsx']

# ── Validation ────────────────────────────────────────────────────────────────

def validate_config():
    """Validate configuration settings."""
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. PlantUML generation will use fallback method.")

    return True