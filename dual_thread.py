import bitmex_kollector
import json
import time
import os
import sys
import datetime as dt
import logging
from threading import Thread
from bitmex_kollector.util import logger

DIR = 'tchetchenya/'

def run_kollector():
    # Edit these bot config
    bitmex_kollector.settings.DATA_DIR = DIR
    # bitmex_kollector.settings.MAIL_TO = ['kauecano@gmail.com']
    bitmex_kollector.settings.BASE_URL = 'https://testnet.bitmex.com/api/v1/' 
    
    # Base bot config - no need to edit
    bitmex_kollector.settings.LOOP_INTERVAL = 30
    bitmex_kollector.settings.PUB_SYM_SUBS = ["instrument"]
    bitmex_kollector.settings.PUB_GEN_SUBS = []

    # Run
    kollector = bitmex_kollector.Kollector("rolMDEfUQwwASTckmugBkeM5", "anR6vCI74u10ggGAxAlCVN05ITrtC8bwiK4_s86vtXRARddP") # testnet
    # kollector = bitmex_kollector.Kollector("JP7uC-IALzH453flus79MKHG", "4Dw_7hwiDLpTuqMQ5PuCIyd8oJVHcfzlI83ipRQLRlVGeBjd")
    kollector.run_loop()

if __name__ == '__main__':

    try:
        logger.setup_logger()
        Thread(target = run_kollector).start()
        time.sleep(2)
        khan = bitmex_kollector.Khan(data_path=DIR)
        while True:
            khan.load_data()
            print('---------------------------------')
            print(khan.status)
            print(khan.instrument)
            print(khan.margin)
            print(khan.position)
            time.sleep(8)
    except KeyboardInterrupt:
        sys.exit()