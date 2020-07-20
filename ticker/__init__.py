import logging
from ticker.ticker import Ticker

logger = logging.getLogger(__name__)
fmlogger = logging.getLogger('fmframework')
logger.setLevel('DEBUG')

file_handler = logging.FileHandler("ticker.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(funcName)s - %(message)s'))
logger.addHandler(file_handler)
fmlogger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(levelname)s %(name)s:%(funcName)s - %(message)s'))
logger.addHandler(stream_handler)
fmlogger.addHandler(stream_handler)
