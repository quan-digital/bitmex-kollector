# -*- coding: utf-8 -*-

# - Tools -
# * Quan.digital *

import os 
import math
from decimal import Decimal
import util.settings as settings

def XBt_to_XBT(XBt):
    """Satoshi to XBT converter"""
    return float(XBt) / 100000000

def to_nearest(num, tickSize = 1):
    """Given a number, round it to the nearest tick. 
       More reliable than round and/or using floats."""
    tickDec = Decimal(str(tickSize))
    return float((Decimal(round(num / tickSize, 0)) * tickDec))

def find_by_keys(keys, table, matchData):
    """Utility method for finding an item in the store when an update comes through on the websocket.
        On a data push, we have a "keys" array. These are the
        fields we can use to uniquely identify an item. Sometimes there is more than one, so we iterate through all
        provided keys."""
    for item in table:
        if all(item[k] == matchData[k] for k in keys):
            return item
 
def create_dirs():
    '''Creates data directories'''
    total_subs = settings.PUB_SYM_SUBS + settings.PRIV_SYM_SUBS + settings.PUB_GEN_SUBS + settings.PRIV_GEN_SUBS

    try:
        os.mkdir(settings.DATA_DIR.replace('/', ''))
        os.mkdir(settings.DATA_DIR + '_ws')
        os.mkdir(settings.DATA_DIR + '_error')
        os.mkdir(settings.DATA_DIR + 'status')
        if 'execution' in total_subs:
            os.mkdir(settings.DATA_DIR + 'execution')
        if 'transact' in total_subs:
            os.mkdir(settings.DATA_DIR + 'transact')
        if 'liquidation' in total_subs:
            os.mkdir(settings.DATA_DIR + 'liquidation')
        if 'chat' in total_subs:
            os.mkdir(settings.DATA_DIR + 'chat')
        if 'quoteBin1m' in total_subs:
            os.mkdir(settings.DATA_DIR + 'quote')
        if 'tradeBin1m' in total_subs:
            os.mkdir(settings.DATA_DIR + 'trade')
        if 'instrument' in total_subs:
            os.mkdir(settings.DATA_DIR + 'instrument')
        if 'margin' in total_subs:
            os.mkdir(settings.DATA_DIR + 'margin')
        if 'position' in total_subs:
            os.mkdir(settings.DATA_DIR + 'position')
        print("Directories created.")

    except FileExistsError:
        print("Directories already exist.")

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0