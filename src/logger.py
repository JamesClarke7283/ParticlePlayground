import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define TRACE level
TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)
logging.Logger.trace = trace

# Set up logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=log_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def get_logger(name):
    logger = logging.getLogger(name)
    if log_level.upper() == 'TRACE':
        logger.setLevel(TRACE_LEVEL_NUM)
    return logger