import sys
import os
sys.path.insert(0, '.')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from backend.utils.logging_config import setup_logging
setup_logging()
import logging
logger = logging.getLogger(__name__)
logger.info('Test Chinese log recording')
logger.warning('Warning message with Chinese')
logger.error('Error message with Chinese')
