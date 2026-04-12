import sys
from loguru import logger
from app.config import logging_config

# Remove default handler and configure application logging
logger.remove()
logger.add(sys.stderr, level=logging_config.log_level)
logger.add(logging_config.log_file, level=logging_config.log_level, rotation="10 MB")


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
