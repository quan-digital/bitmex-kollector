# -*- coding: utf-8 -*-

# - Bitmex Kollector -
#   * Quan.digital *

# author: canokaue
# date: 12/04/2020
# kaue@engineer.com

# The ultimate data collector for Bitmex

import sys
import time
import logging
import datetime as dt

from util.logger import setup_logger, setup_db
from util.ws_thread import BitMEXWebsocket
import util.tools as tools
import util.settings as settings
import util.logger as logger

class Kollector:

    def run_loop(self):
        '''Setup loggers and store to .csv'''
        tools.create_dirs()
        self.logger = setup_logger()

        self.ws = BitMEXWebsocket()

        self.instrument_logger, instrument_path = setup_db('instrument', getPath=True)
        self.margin_logger = setup_db('margin')
        self.position_logger = setup_db('position')

        # If this is our first time initializing files, write headers
        if tools.is_file_empty(instrument_path):
            self.logger.info('Files empty, writing headers.')
            self.write_headers()

        try:
            while(self.ws.ws.sock.connected):

                # Log instrument data every second
                self.log_instrument()

                # Log margin data on changes
                if self.ws._UPDATE_MARGIN:
                    self.log_margin()
                    self.ws._UPDATE_MARGIN = False

                # Log position data on changes
                if self.ws._UPDATE_POSITION:
                    self.log_position()
                    self.ws._UPDATE_POSITION = False

                # If day changes, restart
                now = dt.datetime.now()
                if now.hour == 23 and now.minute == 59:
                    print('Last minute of the day, restart will take place shortly.')
                    if now.second in settings.TRANSITION_SECS:
                        logger.log_error('Restarting...')
                        self.restart()

                time.sleep(settings.LOOP_INTERVAL)

        except AttributeError:
            logger.log_error('Connection to Websocket lost. Restarting...')
            self.reset()

    def restart(self):
        '''Close Websocket, loggers, wait and restart'''
        self.logger.info('Restarting...')
        self.ws.exit()
        # Close loggers
        self.logger.removeHandler(self.logger.handlers[0])
        self.instrument_logger.removeHandler(self.instrument_logger.handlers[0])
        self.margin_logger.removeHandler(self.margin_logger.handlers[0])
        self.position_logger.removeHandler(self.position_logger.handlers[0])
        #logging.shutdown()
        time.sleep(len(settings.TRANSITION_SECS) + 1)
        self.run_loop()

    def reset(self):
        '''Close loggers and reset'''
        self.logger.info('Resetting...')
        self.logger.removeHandler(self.logger.handlers[0])
        self.instrument_logger.removeHandler(self.instrument_logger.handlers[0])
        self.margin_logger.removeHandler(self.margin_logger.handlers[0])
        self.position_logger.removeHandler(self.position_logger.handlers[0])
        #logging.shutdown()
        self.run_loop()

    def log_instrument(self):
        '''Log instrument data'''
        instrument = self.ws.get_instrument_data()
        self.instrument_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
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
        self.margin_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
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
        self.position_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
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
        self.instrument_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s" % ('symbol','state','fundingRate','indicativeFundingRate','prevClosePrice',
'totalVolume','volume','volume24h','totalTurnover','turnover','turnover24h','homeNotional24h',
'foreignNotional24h','prevPrice24h','vwap','highPrice','lowPrice','lastPrice','lastPriceProtected',
'lastTickDirection','lastChangePcnt','bidPrice','midPrice','askPrice','impactBidPrice','impactMidPrice',
'impactAskPrice','openInterest','openValue','markPrice','indicativeSettlePrice'))
        self.margin_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % ('account','currency',
        'amount','realisedPnl','unrealisedPnl','indicativeTax','unrealisedProfit','walletBalance','marginBalance',
        'marginLeverage','marginUsedPcnt','availableMargin','withdrawableMargin'))
        self.position_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % ('account','symbol','commission',
        'leverage','crossMargin','rebalancedPnl','openOrderBuyQty','openOrderBuyCost','openOrderSellQty',
        'openOrderSellCost','execBuyQty','execBuyCost','execSellQty','execSellCost','currentQty','currentCost',
        'isOpen','markPrice','markValue','homeNotional','foreignNotional','posState','realisedPnl','unrealisedPnl',
        'avgCostPrice','avgEntryPrice','breakEvenPrice','liquidationPrice','bankruptPrice'))
        return

class Kollecta:
    '''Simplified Kollector to run with bot'''

    def __init__(self, storeMargin = False, storePosition = False):
        '''Initialize Websocket and setup required csv loggers'''
        self.storeMargin = storeMargin
        self.storePosition = storePosition
        tools.create_dirs()
        self.logger = setup_logger()
        self.ws = BitMEXWebsocket()
        log_path = False
        if storeMargin:
            self.margin_logger, log_path = setup_db('margin', getPath=True)
        if storePosition:
            self.position_logger, log_path = setup_db('position', getPath=True)

        # If this is our first time initializing files, write headers
        if log_path:
            if tools.is_file_empty(log_path):
                self.logger.info('Files empty, writing headers.')
                self.write_headers()
    
    def run_loop(self):
        '''Setup loggers and store to .csv'''
        try:
            while(self.ws.ws.sock.connected):

                # Log margin data on changes
                if self.ws._UPDATE_MARGIN and self.storeMargin:
                    self.log_margin()
                    self.ws._UPDATE_MARGIN = False

                # Log position data on changes
                if self.ws._UPDATE_POSITION and self.storePosition:
                    self.log_position()
                    self.ws._UPDATE_POSITION = False

                # If day changes, restart
                now = dt.datetime.now()
                if now.hour == 23 and now.minute == 59:
                    print('Last minute of the day, restart will take place shortly.')
                    if now.second in settings.TRANSITION_SECS:
                        logger.log_error('Restarting...')
                        self.restart()

                time.sleep(settings.LOOP_INTERVAL)

        except AttributeError:
            logger.log_error('Connection to Websocket lost. Restarting...')
            self.reset()

    def restart(self):
        '''Close Websocket, loggers, wait and restart; called on daily transition'''
        self.logger.info('Restarting...')
        self.ws.exit()
        # Close loggers
        self.logger.removeHandler(self.logger.handlers[0])
        self.instrument_logger.removeHandler(self.instrument_logger.handlers[0])
        self.margin_logger.removeHandler(self.margin_logger.handlers[0])
        self.position_logger.removeHandler(self.position_logger.handlers[0])
        #logging.shutdown()
        time.sleep(len(settings.TRANSITION_SECS) + 1)
        self.run_loop()

    def reset(self):
        '''Close loggers and reset; called on Websocket failure'''
        self.logger.info('Resetting...')
        self.logger.removeHandler(self.logger.handlers[0])
        self.instrument_logger.removeHandler(self.instrument_logger.handlers[0])
        self.margin_logger.removeHandler(self.margin_logger.handlers[0])
        self.position_logger.removeHandler(self.position_logger.handlers[0])
        #logging.shutdown()
        self.run_loop()

    def log_margin(self):
        '''Log margin data'''
        margin = self.ws.get_margin_data()
        self.margin_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
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
        self.position_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
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
        if self.storeMargin:
            self.margin_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % ('account','currency',
            'amount','realisedPnl','unrealisedPnl','indicativeTax','unrealisedProfit','walletBalance','marginBalance',
            'marginLeverage','marginUsedPcnt','availableMargin','withdrawableMargin'))
        if self.storePosition:
            self.position_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % ('account','symbol','commission',
            'leverage','crossMargin','rebalancedPnl','openOrderBuyQty','openOrderBuyCost','openOrderSellQty',
            'openOrderSellCost','execBuyQty','execBuyCost','execSellQty','execSellCost','currentQty','currentCost',
            'isOpen','markPrice','markValue','homeNotional','foreignNotional','posState','realisedPnl','unrealisedPnl',
            'avgCostPrice','avgEntryPrice','breakEvenPrice','liquidationPrice','bankruptPrice'))
        return