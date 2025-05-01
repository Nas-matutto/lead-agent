"""
Configuration settings for the Lead Agent application.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM API keys and settings
LLM_CONFIG = {
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
        "enabled": bool(os.getenv("ANTHROPIC_ENABLED", "True").lower() == "true"),
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "enabled": bool(os.getenv("OPENAI_ENABLED", "False").lower() == "true"),
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "enabled": bool(os.getenv("DEEPSEEK_ENABLED", "False").lower() == "true"),
    },
}

# Web scraping settings
SCRAPING_CONFIG = {
    "user_agent_rotation": True,
    "request_timeout": 10,  # seconds
    "max_retries": 3,
    "concurrent_requests": 5,
    "request_delay": 2,  # seconds between requests
    "use_proxies": bool(os.getenv("USE_PROXIES", "False").lower() == "true"),
    "proxy_list": os.getenv("PROXY_LIST", "").split(",") if os.getenv("PROXY_LIST") else [],
}

# Data storage configuration
STORAGE_CONFIG = {
    "output_dir": os.getenv("OUTPUT_DIR", "data"),
    "default_format": os.getenv("DEFAULT_FORMAT", "csv"),
    "database_url": os.getenv("DATABASE_URL", "sqlite:///leads.db"),
}

# Application settings
APP_CONFIG = {
    "debug": bool(os.getenv("DEBUG", "False").lower() == "true"),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "leads_per_batch": int(os.getenv("LEADS_PER_BATCH", "10")),
    "cache_ttl": int(os.getenv("CACHE_TTL", "86400")),  # 24 hours in seconds
}

def get_config() -> Dict[str, Any]:
    """Return the complete configuration dictionary."""
    return {
        "llm": LLM_CONFIG,
        "scraping": SCRAPING_CONFIG,
        "storage": STORAGE_CONFIG,
        "app": APP_CONFIG,
    }