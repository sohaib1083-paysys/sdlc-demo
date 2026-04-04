# app/config.py
import os

class Config:
    """
    Configuration class.
    """
    DEBUG = os.environ.get("DEBUG", False)
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = os.environ.get("PORT", 8000)
