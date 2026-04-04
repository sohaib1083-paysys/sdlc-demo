# app/utils.py
import logging

def setup_logging():
    """
    Sets up logging.
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("Logging setup complete")
