import logging
import os
from datetime import datetime

def setup_logging(log_level='INFO', log_to_file=True, log_directory='logs'):
    """
    Configure logging for the crawler with flexible options.

    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_to_file: Whether to log to file in addition to console
        log_directory: Directory to store log files
    """

    # Create logs directory if it doesn't exist
    if log_to_file and not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Set up formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = os.path.join(log_directory, f'crawler_{timestamp}.log')

        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)  # Always detailed logging to file
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        # Also create a latest.log symlink for easy access
        latest_log = os.path.join(log_directory, 'latest.log')
        if os.path.exists(latest_log):
            os.remove(latest_log)
        os.symlink(os.path.basename(log_filename), latest_log)

        logger.info(f"Logging to file: {log_filename}")

    return logger

def get_logger(name):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)

# Common log levels for easy reference
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
