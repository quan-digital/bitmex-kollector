# -*- coding: utf-8 -*-

# - Websocket Thread -
# * Quan.digital *

# author: canokaue
# date: 10/04/2020
# kaue@engineer.com

# Websocket based on stock Bitmex API connectors - https://github.com/BitMEX/api-connectors/tree/master/official-ws/python
# and on the sample-market-maker WS thread - https://github.com/BitMEX/sample-market-maker/tree/master/market_maker/ws

# Introduces direct data functions for better storage and less polluted
# usability, as well as complements stock functions with more 
# data sources.

# The Websocket offers a bunch of data as raw properties right on the object.
# On connect, it synchronously asks for a push of all this data then returns.

# Docs: https://www.bitmex.com/app/wsAPI
# API Explorer : https://www.bitmex.com/api/explorer/

import websocket
import logging
import threading
import traceback
import urllib
import ssl
import sys
from time import sleep
import math
import json

from util.api_auth import generate_nonce, generate_signature
import util.tools as tools
import util.logger as logger
import util.settings as settings

class BitMEXWebsocket:

    def __init__(self, endpoint = settings.BASE_URL, symbol = settings.SYMBOL, \
                 api_key=settings.API_KEY, api_secret=settings.API_SECRET):
        '''Connect to the websocket and initialize data.'''
        
        logger.setup_error_logger()
        sys.excepthook = logger.log_exception
        self.logger = logger.setup_logbook('_ws', level=logging.DEBUG)

        self.liquidation_logger = logger.setup_db('liquidation')
        self.transact_logger = logger.setup_db('transact')
        self.chat_logger = logger.setup_db('chat')
        self.execution_logger = logger.setup_db('execution')
        
    
        self.logger.info("Initializing WebSocket...")
        self.endpoint = endpoint
        self.symbol = symbol

        if api_key is not None and api_secret is None:
            raise ValueError('api_secret is required if api_key is provided')
        if api_key is None and api_secret is not None:
            raise ValueError('api_key is required if api_secret is provided')
        self.api_key = api_key
        self.api_secret = api_secret

        self.data = {}
        self.keys = {}
        self.exited = False

        self._UPDATE_MARGIN = False
        self._UPDATE_POSITION = False

        # Subscribe to all pertinent endpoints
        wsURL = self.__get_url()
        self.logger.info("Connecting to URL -- %s" % wsURL)
        self.__connect(wsURL, symbol)
        self.logger.info('Connected to WS.')

        # Connected. Wait for partials
        self.__wait_for_symbol(symbol)
        if api_key:
            self.__wait_for_account()
        self.logger.info('Got all market data. Starting.')

    def init(self):
        '''Connect to the websocket and clear data.'''
        self.logger.debug("Initializing WebSocket...")

        if self.api_key is not None and self.api_secret is None:
            raise ValueError('api_secret is required if api_key is provided')
        if self.api_key is None and self.api_secret is not None:
            raise ValueError('api_key is required if api_secret is provided')

        self.data = {}
        self.keys = {}
        self.exited = False

        # Subscribe to all pertinent endpoints
        wsURL = self.__get_url()
        self.logger.info("Connecting to URL -- %s" % wsURL)
        self.__connect(wsURL, self.symbol)
        self.logger.info('Connected to WS.')

        # Connected. Wait for partials
        self.__wait_for_symbol(self.symbol)
        if self.api_key:
            self.__wait_for_account()
        self.logger.info('Got all market data. Starting.')

    #
    # Lifecycle methods
    #

    def error(self, err):
        self._error = err
        logger.log_error(err)

    def __del__(self):
        self.exit()

    def exit(self):
        '''Call this to exit - will close websocket.'''
        self.exited = True
        self.ws.close()

    def reset(self):
        self.logger.warning('Websocket resetting...')
        self.ws.close()
        self.init()

    #
    # Public data functions
    #

    def get_data(self):
        return self.data

    def get_instrument_data(self):
        '''Return all relevant instrument data'''
        instrument = self.data['instrument'][0]
        return dict(symbol = instrument['symbol'],
                    state = instrument['state'],
                    fundingRate = instrument['fundingRate'],
                    indicativeFundingRate = instrument['indicativeFundingRate'],
                    prevClosePrice = instrument['prevClosePrice'],
                    totalVolume = instrument['totalVolume'],
                    volume = instrument['volume'],
                    volume24h = instrument['volume24h'],
                    totalTurnover = instrument['totalTurnover'],
                    turnover = instrument['turnover'],
                    turnover24h = instrument['turnover24h'],
                    homeNotional24h = instrument['homeNotional24h'],
                    foreignNotional24h = instrument['foreignNotional24h'],
                    prevPrice24h = instrument['prevPrice24h'],
                    vwap = instrument['vwap'],
                    highPrice = instrument['highPrice'],
                    lowPrice = instrument['lowPrice'],
                    lastPrice = instrument['lastPrice'],
                    lastPriceProtected = instrument['lastPriceProtected'],
                    lastTickDirection = instrument['lastTickDirection'],
                    lastChangePcnt = instrument['lastChangePcnt'],
                    bidPrice = instrument['bidPrice'],
                    midPrice = instrument['midPrice'],
                    askPrice = instrument['askPrice'],
                    impactBidPrice = instrument['impactBidPrice'],
                    impactMidPrice = instrument['impactMidPrice'],
                    impactAskPrice = instrument['impactAskPrice'],
                    openInterest = instrument['openInterest'],
                    openValue = instrument['openValue'],
                    markPrice = instrument['markPrice'],
                    indicativeSettlePrice = instrument['indicativeSettlePrice'])

    def get_margin_data(self):
        '''Return all relevant margin data'''
        margin = self.data['margin'][0]
        return dict(account =  margin['account'],
        currency = margin['currency'],
        amount = margin['amount'],
        realisedPnl = margin['realisedPnl'],
        unrealisedPnl = margin['unrealisedPnl'],
        indicativeTax = margin['indicativeTax'],
        unrealisedProfit = margin['unrealisedProfit'],
        walletBalance = margin['walletBalance'],
        marginBalance = margin['marginBalance'],
        marginLeverage = margin['marginLeverage'],
        marginUsedPcnt = margin['marginUsedPcnt'],
        availableMargin = margin['availableMargin'],
        withdrawableMargin = margin['withdrawableMargin'])

    def get_position_data(self):
        '''Return all relevant position data'''
        position = self.data['position'][0]
        return dict(account = position['account'],
        symbol = position['symbol'],
        commission = position['commission'],
        leverage = position['leverage'],
        crossMargin = position['crossMargin'],
        rebalancedPnl = position['rebalancedPnl'],
        openOrderBuyQty = position['openOrderBuyQty'],
        openOrderBuyCost = position['openOrderBuyCost'],
        openOrderSellQty = position['openOrderSellQty'],
        openOrderSellCost = position['openOrderSellCost'],
        execBuyQty = position['execBuyQty'],
        execBuyCost = position['execBuyCost'],
        execSellQty = position['execSellQty'],
        execSellCost = position['execSellCost'],
        currentQty = position['currentQty'],
        currentCost = position['currentCost'],
        isOpen = position['isOpen'],
        markPrice = position['markPrice'],
        markValue = position['markValue'],
        homeNotional = position['homeNotional'],
        foreignNotional = position['foreignNotional'],
        posState = position['posState'],
        realisedPnl = position['realisedPnl'],
        unrealisedPnl = position['unrealisedPnl'],
        avgCostPrice = position['avgCostPrice'],
        avgEntryPrice = position['avgEntryPrice'],
        breakEvenPrice = position['breakEvenPrice'],
        liquidationPrice = position['liquidationPrice'],
        bankruptPrice = position['bankruptPrice'])

    #
    # Private data functions
    #


    #
    # Core Methods
    #

    def __connect(self, wsURL, symbol):
        '''Connect to the websocket in a thread.'''
        self.logger.debug("Starting thread...")

        ssl_defaults = ssl.get_default_verify_paths()
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}

        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=self.__get_auth())

        self.wst = threading.Thread(target=lambda: self.ws.run_forever(sslopt=sslopt_ca_certs))
        self.wst.daemon = True
        self.wst.start()
        self.logger.debug("Started thread")

        # Wait for connect before continuing
        conn_timeout = settings.WS_TIMEOUT
        while (not self.ws.sock or not self.ws.sock.connected) and conn_timeout:
            sleep(1)
            conn_timeout -= 1

        if not conn_timeout:
            self.logger.error("Couldn't connect to WS! Exiting.")
            self.exit()
            raise websocket.WebSocketTimeoutException('Couldn\'t connect to WS! Exiting.')

    def __get_auth(self):
        '''Return auth headers. Will use API Keys if present in settings.'''
        if self.api_key:
            self.logger.info("Authenticating with API Key.")
            # To auth to the WS using an API key, we generate a signature of a nonce and
            # the WS API endpoint.
            expires = generate_nonce()
            return [
                "api-expires: " + str(expires),
                "api-signature: " + generate_signature(self.api_secret, 'GET', '/realtime', expires, ''),
                "api-key:" + self.api_key
            ]
        else:
            self.logger.info("Not authenticating.")
            return []

    def __get_url(self):
        '''Generate a connection URL. We can define subscriptions right in the querystring.
        Most subscription topics are scoped by the symbol we're listening to.'''

        # Public subs
        symbolSubs = ["instrument", "liquidation"]
        genericSubs = ["chat"]

        # Private subs
        symbolSubsPriv = ["execution", "position"]
        genericSubsPriv = ["transact", "margin"]

        # Merge both subs types
        symbolSubs += symbolSubsPriv
        genericSubs += genericSubsPriv

        subscriptions = [sub + ':' + self.symbol for sub in symbolSubs]
        subscriptions += genericSubs

        urlParts = list(urllib.parse.urlparse(self.endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(','.join(subscriptions))
        return urllib.parse.urlunparse(urlParts)

    def __wait_for_account(self):
        '''On subscribe, this data will come down. Wait for it.'''
        while not {"execution", "position", "transact", "margin"} <= set(self.data):
            sleep(0.1)
        return

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        while not {"instrument", "liquidation", "chat"} <= set(self.data):
            sleep(0.1)

    def __send_command(self, command, args=None):
        '''Send a raw command.'''
        if args is None:
            args = []
        self.ws.send(json.dumps({"op": command, "args": args}))

    def __on_message(self, message):
        '''Handler for parsing WS messages.'''
        message = json.loads(message)
        
        #table = message.get("table")
        #action = message.get("action")
        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        try:
            if 'subscribe' in message:
                if message['success']:
                    self.logger.debug("Subscribed to %s." % message['subscribe'])
                else:
                    self.error("Unable to subscribe to %s. Error: \"%s\"" %
                               (message['request']['args'][0], message['error']))
            elif 'status' in message:
                if message['status'] == 400:
                    self.error(message['error'])
                if message['status'] == 401:
                    self.error("API Key incorrect, please check and restart.")
            elif action:

                if table not in self.data:
                    self.data[table] = []

                if table not in self.keys:
                    self.keys[table] = []

                # There are four possible actions from the WS:
                # 'partial' - full table image
                # 'insert'  - new row
                # 'update'  - update row
                # 'delete'  - delete row
                if action == 'partial':
                    self.logger.debug("%s: partial" % table)
                    self.data[table] = message['data']
                    # Keys are communicated on partials to let you know how to uniquely identify
                    # an item. We use it for updates.
                    self.keys[table] = message['keys']
                elif action == 'insert':
                    self.logger.debug('%s: inserting %s' % (table, message['data']))
                    self.data[table] += message['data']

                    # Store chat
                    if table == 'chat':
                        data = message['data'][0]
                        self.chat_logger.info('%s, %s, %s, %s, %s' % (data['channelID'], data['fromBot'], 
                        data['id'], str(data['message']).replace('\n', '').replace(',', '.'), data['user']))

                    # Store liquidations
                    elif table == 'liquidation':
                        data = message['data'][0]
                        self.liquidation_logger.info('%s, %s, %s, %s, %s' % (data['orderID'], data['symbol'], 
                        data['side'], data['price'], data['leavesQty']))

                    # Store transactions
                    elif table == 'transact':
                        data = message['data'][0]
                        self.transact_logger.info('%s, %s, %s, %s, %s, %s, %s, %s, %s' % (data['transactID'], 
                        data['account'], data['currency'], data['transactType'], data['amount'], data['fee'], 
                        data['transactStatus'], data['address'], data['text']))

                    # Store executions
                    elif table == 'execution':
                        data = message['data'][0]
                        self.execution_logger.info('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % 
                        (data['execID'], data['orderID'], data['clOrdID'], data['account'], data['symbol'], 
                        data['side'], data['orderQty'], data['price'], data['execType'], data['ordType'],
                        data['commission'], data['text']))

                    # Limit the max length of the table to avoid excessive memory usage.
                    if len(self.data[table]) > settings.MAX_TABLE_LEN:
                        self.data[table] = self.data[table][settings.MAX_TABLE_LEN // 2:]

                elif action == 'update':
                    self.logger.debug('%s: updating %s' % (table, message['data']))

                    # Set margin update signal to True
                    if table == 'margin':
                        self._UPDATE_MARGIN = True

                    # Set margin update signal to True
                    if table == 'position':
                        self._UPDATE_POSITION = True

                    # Locate the item in the collection and update it.
                    for updateData in message['data']:
                        item = tools.find_by_keys(self.keys[table], self.data[table], updateData)
                        if not item:
                            continue  # No item found to update. Could happen before push
                            
                        # Update this item.
                        item.update(updateData)

                elif action == 'delete':
                    self.logger.debug('%s: deleting %s' % (table, message['data']))
                    # Locate the item in the collection and remove it.
                    for deleteData in message['data']:
                        item = tools.find_by_keys(self.keys[table], self.data[table], deleteData)
                        self.data[table].remove(item)
                else:
                    raise Exception("Unknown received action: %s" % action)
        except:
            self.logger.error(traceback.format_exc())
            if(len(self.data)):
                if(len(self.data['instrument'])):
                    raise Exception("Unknown unhandled action: {0} \n Also Data: {1}".format(traceback.format_exc(),self.data))

    def __on_error(self, error):
        '''Called on fatal websocket errors. We exit on these.'''
        if '502' in error:
            self.logger.error("Bad Gateway, retrying.")
            sleep(1)
            self.reset()

        elif not self.exited:
            self.logger.error("Error : %s" % error)
            raise websocket.WebSocketException(error)

    def __reset(self):
        self.data = {}
        self.keys = {}
        self.exited = False
        self._error = None

    def __on_open(self):
        '''Called when the WS opens.'''
        self.logger.debug("Websocket Opened.")

    def __on_close(self):
        '''Called on websocket close.'''
        self.logger.info('Websocket Closed')