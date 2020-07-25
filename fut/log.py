import logging
from datetime import datetime
from click import BadParameter

def setup_logger():
  log_numeric = getattr(logging, log.upper())
  if not isinstance(log_numeric, int):
    error_msg = f'Invalid log level: {log}'
    raise BadParameter(error_msg)

  timestamp = str(datetime.now().strftime('%Y%m%d_%H%M%S'))
  logging.basicConfig(filename=f'logs/{timestamp}.log',
    filemode='w', level=log_numeric, datefmt='%H:%M:%S', 
    format='%(asctime)s - %(levelname)s: %(message)s')