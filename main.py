import sys
import time
import logging

from util.logger import setup_logger, setup_db
from util.ws_thread import BitMEXWebsocket
from util.tools import create_dirs

if __name__ == '__main__':

    create_dirs()
    logger = setup_logger()

    ws = BitMEXWebsocket()

    instrument_logger = setup_db('instrument')
    user_logger = setup_db('user')

    while(ws.ws.sock.connected):

        data = ws.get_data()
        instrument = ws.get_instrument_data()

        instrument_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
%s, %s, %s," % (instrument['symbol'],
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
        
        user_logger.info(data['order'])
        user_logger.info(data['margin'])
        user_logger.info(data['position'])
            
        time.sleep(1)
