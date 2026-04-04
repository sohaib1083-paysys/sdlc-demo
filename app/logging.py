import logging
from loguru import logger
from app.config import logging_config

# Set up logging
logger.remove(0)
logger.add(logging_config.log_file, level=logging_config.log_level)

def log_error(message: str, exception: Exception):
    """
    Log an error message with an exception.
    """
    logger.error(f"{message}: {str(exception)}")

def log_info(message: str):
    """
    Log an info message.
    """
    logger.info(message)
