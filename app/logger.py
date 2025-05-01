import logging
import os

from colorlog import ColoredFormatter

if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger('flask_app')

flask_env = os.getenv('FLASK_ENV', 'production')
if flask_env == 'development':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Create colored formatter
formatter = ColoredFormatter(
    "%(asctime)s [%(log_color)s%(levelname)s%(reset)s] %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logger.level)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
