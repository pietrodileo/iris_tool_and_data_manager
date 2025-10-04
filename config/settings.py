# config/settings.py
"""
Application Configuration
Loads environment variables and provides configuration settings
"""

import dotenv
import os

dotenv.load_dotenv()

class AppConfig:
    """Application configuration from environment variables"""
    
    def __init__(self):
        self.IRIS_HOST = self._get_env("IRIS_HOST")
        self.IRIS_PORT = self._get_env("IRIS_PORT")
        self.IRIS_NAMESPACE = self._get_env("IRIS_NAMESPACE")
        self.IRIS_USER = self._get_env("IRIS_USER")
        self.IRIS_PASSWORD = self._get_env("IRIS_PASSWORD")        
        self.OLLAMA_API_URL = self._get_env("OLLAMA_API_URL")
    
    def _get_env(self, key: str) -> str:
        """Get environment variable from .env file"""
        value = dotenv.get_key(".env", key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value