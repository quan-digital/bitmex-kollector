# -*- coding: utf-8 -*-

# - Logger functions -
# * Quan.digital *

from datetime import datetime
import logging
import json
import sys
from logging.handlers import RotatingFileHandler

import bitmex_kollector.settings as settings
import bitmex_kollector.util.tools as tools

def setup_logger():
    '''Prints logger info to terminal'''
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def setup_logbook(name, extension='.txt', level=logging.INFO, soloDir = True):
    """Setup logger that writes to file, supports multiple instances with no overlap.
       Available levels: DEBUG|INFO|WARN|ERROR"""
    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d (%(name)s) - %(message)s', datefmt='%d-%m-%y %H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')
    if soloDir:
        log_path = str(settings.DATA_DIR + name + '/' + name.replace('_', '') +'_' + date + extension)
    else:
        log_path = str(settings.DATA_DIR + name +'_' + date + extension)
    handler = RotatingFileHandler(log_path, maxBytes=settings.MAX_FILE_SIZE, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def setup_db(name, extension='.csv', getPath = False):
    """Setup writer that formats data to csv, supports multiple instances with no overlap."""
    formatter = logging.Formatter(fmt='%(asctime)s,%(message)s', datefmt='%d-%m-%y,%H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')
    db_path = str(settings.DATA_DIR + name + '/' + name + '_' + date + extension)

    handler = RotatingFileHandler(db_path, maxBytes=settings.MAX_FILE_SIZE, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    if getPath:
        return logger, db_path
    else:
        return logger

# Global error_logger so all functions can use it
error_logger = logging.getLogger('_error')

def setup_error_logger():
    '''Basic handler setup for error_logger'''
    date = datetime.today().strftime('%Y-%m-%d')
    log_path = settings.DATA_DIR + '_error/error_' + date + '.txt'

    global error_logger
    error_logger = logging.getLogger('_error')
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=settings.MAX_FILE_SIZE, backupCount=1) # stream=sys.stdout
    error_logger.addHandler(handler)

def close_error_logger():
    error_logger.removeHandler(error_logger.handlers[0])
    return

def log_exception(exc_type, exc_value, exc_traceback):
    '''Log unhandled exceptions'''
    update_status('Exception')
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info(str(datetime.now()))
    error_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info('')
    return
# then set sys.excepthook = logger.log_exception on main file

def log_error(message):
    '''Log handled errors'''
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info(str(datetime.now()))
    error_logger.error(message)
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info('')
    update_status()
    return

def update_status(message = 'Error'):
    with open(settings.DATA_DIR + 'status.json', 'r') as handler:
        status = json.load(handler)
    status['status'] = message
    with open(settings.DATA_DIR + 'status.json', 'w') as handler:
        json.dump(status,handler)
    return