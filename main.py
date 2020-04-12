import sys
import time
import logging

from util.logger import setup_logger, setup_db
from util.ws_thread import BitMEXWebsocket
from util.tools import create_dirs
import util.settings as settings

if __name__ == '__main__':

    create_dirs()
    logger = setup_logger()

    ws = BitMEXWebsocket()

    instrument_logger = setup_db('instrument')
    margin_logger = setup_db('margin')
    position_logger = setup_db('position')

    while(ws.ws.sock.connected):

        data = ws.get_data()
        instrument = ws.get_instrument_data()

        # Log instrument data every second
        instrument_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
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
        
        # Log margin data on changes
        if ws._UPDATE_MARGIN:
            margin = ws.get_margin_data()
            margin_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
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
            ws._UPDATE_MARGIN = False

        time.sleep(settings.LOOP_INTERVAL)
