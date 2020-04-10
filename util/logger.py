# -*- coding: utf-8 -*-

# - Logger functions -
# * Quan.digital *

from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

import util.settings as settings

def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
    # Available levels: logging.(DEBUG|INFO|WARN|ERROR)
    #logger.setLevel(logging.DEBUG)  # Change this to DEBUG if you want a lot more info
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def setup_logbook(name, extension='.txt', level=logging.INFO):
    """Setup logger that writes to file, supports multiple instances with no overlap.
       Available levels: DEBUG|INFO|WARN|ERROR"""
    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d (%(name)s) - %(message)s', datefmt='%d-%m-%y %H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')
    log_path = str(settings.DATA_DIR + name + '_' + date + extension)

    handler = RotatingFileHandler(log_path, maxBytes=settings.MAX_FILE_SIZE, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def setup_db(name, extension='.csv'):
    """Setup writer that formats data to csv, supports multiple instances with no overlap."""
    formatter = logging.Formatter(fmt='%(asctime)s,%(message)s', datefmt='%d-%m-%y,%H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')
    db_path = str(settings.DATA_DIR + name + '_' + date + extension)

    handler = RotatingFileHandler(db_path, maxBytes=settings.MAX_FILE_SIZE, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger