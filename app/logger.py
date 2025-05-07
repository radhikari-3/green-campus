import logging
import os
from colorlog import ColoredFormatter

# === Ensure 'logs' directory exists ===
if not os.path.exists('logs'):
    os.makedirs('logs')  # Create logs directory if it doesn't exist

# === Create logger instance ===
logger = logging.getLogger('flask_app')  # Named logger for the Flask app

# === Set log level based on environment ===
flask_env = os.getenv('FLASK_ENV', 'production')  # Default to 'production' if not set
if flask_env == 'development':
    logger.setLevel(logging.DEBUG)  # Verbose output during development
else:
    logger.setLevel(logging.INFO)   # Quieter output in production

# === Setup colored formatter for console output ===
formatter = ColoredFormatter(
    "%(asctime)s [%(log_color)s%(levelname)s%(reset)s] %(message)s",  # Log format
    datefmt=None,
    reset=True,
    log_colors={  # Color mapping by log level
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

# === Configure console logging ===
console_handler = logging.StreamHandler()     # Output logs to stdout
console_handler.setLevel(logger.level)        # Match handler level with logger level
console_handler.setFormatter(formatter)       # Use colored formatter

# === Attach handler to logger ===
logger.addHandler(console_handler)
