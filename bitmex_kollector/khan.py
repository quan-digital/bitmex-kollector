# -*- coding: utf-8 -*-

# - Bitmex Khan -
#   * Quan.digital *

# author: canokaue
# date: 06/05/2020
# kaue.cano@quan.digital

# Data fetcher for Kollector

import json
import time
import os
import sys
import datetime as dt
import logging
from bitmex_kollector.util import logger
from bitmex_kollector import settings


class Khan:

    def __init__(self, data_path = settings.DATA_DIR):
        self.base_path = data_path

        self.status = {}
        self.instrument = {}
        self.margin = {}
        self.position = {}

        self.logger = logger.setup_logbook('_khan')
        self.logger.info('Khan started.')

        self.wait_for_data()

    def wait_for_data(self):
        self.logger.info('Waiting for data...')
        self.wait_for_files()
        self.load_data()
        while not self.check_timestamp():
            time.sleep(0.1)
            self.load_data()
        self.logger.info('Data received, all set.')

    def wait_for_files(self):
        while not(os.path.exists(self.base_path + 'status.json') \
            and os.path.exists(self.base_path + 'instrument.json') \
            and os.path.exists(self.base_path + 'position.json') \
            and os.path.exists(self.base_path + 'margin.json') ):
            time.sleep(0.1)

    def __del__(self):
        self.exit()

    def exit(self):
        self.logger.warning('Closing Khan.')
        self.status = {}
        self.instrument = {}
        self.margin = {}
        self.position = {}
        self.logger.removeHandler(self.logger.handlers[0])

    def reset(self):
        self.logger.warning('Khan is resetting.')
        self.exit()
        self.__init__()


    # Data load functions

    def load_data(self):
        self.load_status()
        self.load_instrument()
        self.load_margin()
        self.load_position()

    def load_status(self):
        load_path = self.base_path + 'status.json'
        try:
            with open(load_path, 'r') as handler:
                self.status = json.load(handler)
            return self.status
        except:
            self.logger.info('Unable to open status file, retrying.')
            time.sleep(0.1)
            self.load_status()

    def load_instrument(self):
        load_path = self.base_path + 'instrument.json'
        try:
            with open(load_path, 'r') as handler:
                self.instrument = json.load(handler)
            return self.instrument
        except:
            self.logger.info('Unable to open instrument file, retrying.')
            time.sleep(0.1)
            self.load_instrument()

    def load_margin(self):
        load_path = self.base_path + 'margin.json'
        if not os.path.exists(load_path):
            self.margin = False
            return
        try:
            with open(load_path, 'r') as handler:
                self.margin = json.load(handler)
            return self.margin
        except:
            self.logger.info('Unable to open margin file, retrying.')
            time.sleep(0.1)
            self.load_margin()

    def load_position(self):
        load_path = self.base_path + 'position.json'
        if not os.path.exists(load_path):
            self.position = False
            return
        try:
            with open(load_path, 'r') as handler:
                self.position = json.load(handler)
            return self.position
        except:
            self.logger.info('Unable to open position file, retrying.')
            time.sleep(0.1)
            self.load_position()

    # Verification functions

    def check_deviation(self):
        status = self.status
        deviation = False
        if not status:
            deviation = 'No status found.'
        elif status['status'] != 'Running':
            deviation = 'Kollector not running.'
        elif not status['connected']:
            deviation = 'Websocket disconnected.'
        elif status['market'] != 'Open':
            deviation = 'Market closed.'
        
        now = dt.datetime.now()
        elapsed = now - dt.datetime.strptime(status['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        if elapsed.total_seconds() > settings.KHAN_TIMEOUT:
            deviation = 'Khan timeout. Last status received at %s' % status['timestamp']
        
        if deviation:
            self.logger.warning(deviation)

        return deviation

    def check_timestamp(self):
        now = dt.datetime.now()
        elapsed = now - dt.datetime.strptime(self.instrument['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        return False if elapsed.total_seconds() > settings.KHAN_TIMEOUT else True