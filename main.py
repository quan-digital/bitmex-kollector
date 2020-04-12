import sys
import time
import logging

from util.logger import setup_logger, setup_logbook
from util.ws_thread import BitMEXWebsocket

if __name__ == '__main__':

    logger = setup_logger()
    # announcement = setup_logbook('announcement')
    # chat = setup_logbook('chot')
    # connected = setup_logbook('connected')
    # instrument = setup_logbook('instrument')
    # insurance = setup_logbook('insurance')
    # liquidation = setup_logbook('liquodation')
    # affiliate = setup_logbook('affiliate', soloDir=False)

    ws = BitMEXWebsocket()

    while(ws.ws.sock.connected):

        data = ws.get_data()

        # announcement.info(data['announcement'])
        # chat.info(data['chat'])
        # connected.info(data['connected'])
        # instrument.info(data['instrument'])
        # insurance.info(data['insurance'])
        # liquidation.info(data['liquidation'])
        # affiliate.info(data['affiliate'])

        time.sleep(1)

