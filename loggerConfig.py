import logging
import os
from datetime import datetime
from config import path

datetime = datetime.now()

def configure_logger(path):
    # Set the log file path
    logfile = os.path.join(path, datetime.now().strftime('sample_%Y%m%d-%H%M')+".log")

    # Set the log format
    FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"

    # Configure the logger
    logging.basicConfig(filename=logfile, format=FORMAT)
    logger = logging.getLogger()
    logger.setLevel(level=logging.INFO)