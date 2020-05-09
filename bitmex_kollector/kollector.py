# -*- coding: utf-8 -*-

# - Bitmex Kollector -
#   * Quan.digital *

# author: canokaue
# date: 03/05/2020
# kaue.cano@quan.digital

# The ultimate data collector for Bitmex

import sys
import time
import logging
import datetime as dt
import os
import json

from bitmex_kollector.util.logger import setup_logbook, setup_db
from bitmex_kollector.util.ws_thread import BitMEXWebsocket
from bitmex_kollector.util import tools
from bitmex_kollector.util import logger
from bitmex_kollector import settings

class Kollector:

    def __init__(self, apiKey, apiSecret, log_level = logging.INFO,
        storeInstrument = None,
        storeMargin = None,
        storePosition = None):
        '''Create dirs, initialize Websocket and setup required csv loggers'''
        tools.create_dirs()
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.storeInstrument = storeInstrument if storeInstrument else settings.STORE_INSTRUMENT
        self.storeMargin = storeMargin if storeMargin else settings.STORE_MARGIN
        self.storePosition = storePosition if storePosition else settings.STORE_POSITION

        self.logger = setup_logbook('_kollector', level = log_level)
        self.logger.info('Kollector is starting.')
        self.status_logger, log_path = setup_db('status', getPath=True)
        if self.storeInstrument:
            self.instrument_logger, log_path = setup_db('instrument', getPath=True)
        if self.storeMargin:
            self.margin_logger, log_path = setup_db('margin', getPath=True)
        if self.storePosition:
            self.position_logger, log_path = setup_db('position', getPath=True)
        self.logger.debug('Loggers created.')

        # If this is our first time initializing files, write headers
        if tools.is_file_empty(log_path):
            self.logger.debug('Files empty, writing headers.')
            self.write_headers()

        self.ws = BitMEXWebsocket(apiKey, apiSecret)
        self.update_status('Starting')
        while not(self.ws.got_partial) : time.sleep(0.1)

    def run_loop(self):
        '''Setup loggers and store to .csv'''
        self.logger.debug('First run, writing partials.')
        first_run = True # fist run connection check must be ignored
        self.first_status()
        self.log_margin()
        self.log_position()
        try:
            while(self.ws.ws.sock.connected):
                self.dump_status()

                if self.storeInstrument:
                    # Log instrument data every loop
                    self.log_instrument()

                if self.storeMargin:
                    # Log margin data on changes
                    if self.ws._UPDATE_MARGIN:
                        self.log_margin()
                        self.ws._UPDATE_MARGIN = False

                if self.storePosition:
                    # Log position data on changes
                    if self.ws._UPDATE_POSITION:
                        self.log_position()
                        self.ws._UPDATE_POSITION = False

                # if not(first_run):
                self.log_status()

                # If day changes, restart
                date = dt.datetime.today().strftime('%Y-%m-%d')
                path = str(settings.DATA_DIR + '_ws/ws_' + date + '.txt')
                if not(os.path.exists(path)):
                    self.logger.warning('Day changed.')
                    logger.log_error('Restarting...')
                    self.restart()

                if not(self.check_connection()) and not(first_run):
                    raise AttributeError()

                time.sleep(settings.LOOP_INTERVAL)
                first_run = False

        except AttributeError:
            self.logger.warning('Connection to Websocket lost. Restarting...')
            logger.log_error('Connection to Websocket lost. Restarting...')
            self.reset()

    def restart(self):
        '''Close Websocket, loggers, wait and restart'''
        self.logger.info('Restarting...')
        self.update_status()
        self.ws.exit()
        # Close loggers
        self.logger.removeHandler(self.logger.handlers[0])
        self.status_logger.removeHandler(self.status_logger.handlers[0])
        self.instrument_logger.removeHandler(self.instrument_logger.handlers[0])
        self.margin_logger.removeHandler(self.margin_logger.handlers[0])
        self.position_logger.removeHandler(self.position_logger.handlers[0])
        #logging.shutdown()
        time.sleep(1)
        self.__init__(self.apiKey, self.apiSecret)
        self.run_loop()

    def reset(self):
        '''Close loggers and reset'''
        self.logger.info('Resetting...')
        self.update_status()
        self.logger.removeHandler(self.logger.handlers[0])
        self.status_logger.removeHandler(self.status_logger.handlers[0])
        self.instrument_logger.removeHandler(self.instrument_logger.handlers[0])
        self.margin_logger.removeHandler(self.margin_logger.handlers[0])
        self.position_logger.removeHandler(self.position_logger.handlers[0])
        #logging.shutdown()
        self.__init__(self.apiKey, self.apiSecret)
        self.run_loop()

    def log_status(self):
        '''Log status data directly from json'''
        status = self.ws.status_dict
        self.status_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
        status['status'],
        status['connected'],
        status['market'],
        status['lastPrice'],
        status['markPrice'],
        status['balance'],
        status['realisedPnl'],
        status['unrealisedPnl'],
        status['position'],
        status['contractNum'],
        status['contractCost'],
        status['openOrders']))
        return


    def log_instrument(self):
        '''Log instrument data'''
        instrument = self.ws.get_instrument_data()
        self.instrument_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s" % (instrument['symbol'],
        instrument['state'],
        instrument['fundingRate'],
        instrument['indicativeFundingRate'],
        instrument['prevClosePrice'],
        instrument['totalVolume'],
        instrument['volume'],
        instrument['volume24h'],
        instrument['totalTurnover'],
        instrument['turnover'],
        instrument['turnover24h'],
        instrument['homeNotional24h'],
        instrument['foreignNotional24h'],
        instrument['prevPrice24h'],
        instrument['vwap'],
        instrument['highPrice'],
        instrument['lowPrice'],
        instrument['lastPrice'],
        instrument['lastPriceProtected'],
        instrument['lastTickDirection'],
        instrument['lastChangePcnt'],
        instrument['bidPrice'],
        instrument['midPrice'],
        instrument['askPrice'],
        instrument['impactBidPrice'],
        instrument['impactMidPrice'],
        instrument['impactAskPrice'],
        instrument['openInterest'],
        instrument['openValue'],
        instrument['markPrice'],
        instrument['indicativeSettlePrice']))
        return

    def log_margin(self):
        '''Log margin data'''
        margin = self.ws.get_margin_data()
        self.margin_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
        margin['account'],
        margin['currency'],
        margin['amount'],
        margin['realisedPnl'],
        margin['unrealisedPnl'],
        margin['indicativeTax'],
        margin['unrealisedProfit'],
        margin['walletBalance'],
        margin['marginBalance'],
        margin['marginLeverage'],
        margin['marginUsedPcnt'],
        margin['availableMargin'],
        margin['withdrawableMargin']))
        return

    def log_position(self):
        '''Log position data'''
        position = self.ws.get_position_data()
        self.position_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
        position['account'],
        position['symbol'],
        position['commission'],
        position['leverage'],
        position['crossMargin'],
        position['rebalancedPnl'],
        position['openOrderBuyQty'],
        position['openOrderBuyCost'],
        position['openOrderSellQty'],
        position['openOrderSellCost'],
        position['execBuyQty'],
        position['execBuyCost'],
        position['execSellQty'],
        position['execSellCost'],
        position['currentQty'],
        position['currentCost'],
        position['isOpen'],
        position['markPrice'],
        position['markValue'],
        position['homeNotional'],
        position['foreignNotional'],
        position['posState'],
        position['realisedPnl'],
        position['unrealisedPnl'],
        position['avgCostPrice'],
        position['avgEntryPrice'],
        position['breakEvenPrice'],
        position['liquidationPrice'],
        position['bankruptPrice']))
        return

    def write_headers(self):
        '''Log csv headers'''
        # Status csv
        self.status_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % ('status','connected',
            'market','lastPrice','markPrice','balance','realisedPnl','unrealisedPnl','position',
            'contractNum','contractCost','openOrders'))
        # Instrument csv
        if self.storeInstrument:
            self.instrument_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s" % ('symbol','state','fundingRate','indicativeFundingRate','prevClosePrice',
            'totalVolume','volume','volume24h','totalTurnover','turnover','turnover24h','homeNotional24h',
            'foreignNotional24h','prevPrice24h','vwap','highPrice','lowPrice','lastPrice','lastPriceProtected',
            'lastTickDirection','lastChangePcnt','bidPrice','midPrice','askPrice','impactBidPrice','impactMidPrice',
            'impactAskPrice','openInterest','openValue','markPrice','indicativeSettlePrice'))
        # Margin csv
        if self.storeMargin:
            self.margin_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % ('account','currency',
            'amount','realisedPnl','unrealisedPnl','indicativeTax','unrealisedProfit','walletBalance','marginBalance',
            'marginLeverage','marginUsedPcnt','availableMargin','withdrawableMargin'))
        # Position csv
        if self.storePosition:
            self.position_logger.debug("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % ('account','symbol','commission',
            'leverage','crossMargin','rebalancedPnl','openOrderBuyQty','openOrderBuyCost','openOrderSellQty',
            'openOrderSellCost','execBuyQty','execBuyCost','execSellQty','execSellCost','currentQty','currentCost',
            'isOpen','markPrice','markValue','homeNotional','foreignNotional','posState','realisedPnl','unrealisedPnl',
            'avgCostPrice','avgEntryPrice','breakEvenPrice','liquidationPrice','bankruptPrice'))
        return

    def update_status(self, message = 'Restarting'):
        self.ws.status_dict['status'] = message
        return

    def first_status(self):
        status = dict(status = 'Starting', connected = 0, market = 0, lastPrice = 0, markPrice = 0, balance = 0, realisedPnl = 0,
        unrealisedPnl = 0, position = 0, contractNum = 0, contractCost = 0, openOrders = 0, timestamp = str(dt.datetime.now()))
        self.ws.status_dict = status
        return

    def check_connection(self):
        status = self.ws.status_dict
        now = dt.datetime.now()
        elapsed = now - dt.datetime.strptime(status['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        return False if elapsed.total_seconds() > settings.LOOP_TIMEOUT else True

    def dump_status(self):
        '''Save status to json'''
        status = self.ws.status_dict
        with open(settings.DATA_DIR + 'status.json', 'w') as handler:
            json.dump(status,handler)
        return