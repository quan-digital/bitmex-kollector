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
from util.tools import create_dirs
import util.settings as settings
import util.logger as logger

class Kollector:

    def run_loop(self):
        '''Setup loggers and store to .csv'''
        create_dirs()
        self.logger = setup_logger()

        self.ws = BitMEXWebsocket()

        self.instrument_logger = setup_db('instrument')
        self.margin_logger = setup_db('margin')
        self.position_logger = setup_db('position')

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
            
            if not(self.ws.ws.sock.connected):
                logger.log_error('Connection to Websocket lost. Restarting...')
                self.restart()

            time.sleep(settings.LOOP_INTERVAL)

    def restart(self):
        '''Close Websocket, loggers, wait and restart'''
        self.ws.exit()
        # Close loggers
        self.logger.removeHandler(self.logger.handlers[0])
        self.instrument_logger.removeHandler(self.instrument_logger.handlers[0])
        self.margin_logger.removeHandler(self.margin_logger.handlers[0])
        self.position_logger.removeHandler(self.position_logger.handlers[0])
        logging.shutdown()
        time.sleep(len(settings.TRANSITION_SECS) + 1)
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

if __name__ == '__main__':
    kollector = Kollector()
    kollector.run_loop()