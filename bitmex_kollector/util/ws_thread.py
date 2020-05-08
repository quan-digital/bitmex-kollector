# -*- coding: utf-8 -*-

# - Websocket Thread -
# * Quan.digital *

# author: canokaue
# date: 13/04/2020
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
import datetime as dt

from bitmex_kollector.util.api_auth import generate_nonce, generate_signature
import bitmex_kollector.util.tools as tools
import bitmex_kollector.util.logger as logger
import bitmex_kollector.settings as settings

class BitMEXWebsocket:

    def __init__(self, api_key, api_secret, log_level = logging.INFO,
         endpoint = settings.BASE_URL, symbol = settings.SYMBOL):
        '''Connect to the websocket and initialize data.'''
        if settings.DEBUG_WS == True:
            log_level = logging.DEBUG
        # Setup core loggers
        logger.setup_error_logger()
        sys.excepthook = logger.log_exception
        self.logger = logger.setup_logbook('_ws', level= log_level)

        # Get subscriptions
        self.symbol_subs = settings.PUB_SYM_SUBS + settings.PRIV_SYM_SUBS
        self.generic_subs = settings.PUB_GEN_SUBS + settings.PRIV_GEN_SUBS
        self.total_subs = self.symbol_subs + self.generic_subs

        # Create loggers
        if 'execution' in self.total_subs:
            self.execution_logger, log_path = logger.setup_db('execution', getPath=True)
        if 'transact' in self.total_subs:
            self.transact_logger, log_path = logger.setup_db('transact', getPath=True)
        if 'liquidation' in self.total_subs:
            self.liquidation_logger, log_path = logger.setup_db('liquidation', getPath=True)
        if 'chat' in self.total_subs:
            self.chat_logger, log_path = logger.setup_db('chat', getPath=True)
        if 'quoteBin1m' in self.total_subs:
            self.quote_logger, log_path = logger.setup_db('quote', getPath=True)
        if 'tradeBin1m' in self.total_subs:
            self.trade_logger, log_path = logger.setup_db('trade', getPath=True)

        # If this is our first time initializing files, write headers
        if log_path:
            if tools.is_file_empty(log_path):
                self.logger.debug('Files empty, writing headers.')
                self.write_headers()

        self.logger.info("Initializing WebSocket...")
        self.endpoint = endpoint
        self.symbol = symbol

        if api_key is not None and api_secret is None:
            raise ValueError('api_secret is required if api_key is provided')
        if api_key is None and api_secret is not None:
            raise ValueError('api_key is required if api_secret is provided')
        if (api_key is None or api_secret is None) and ('execution' in self.total_subs or 'transact' in self.total_subs):
            raise ValueError('api_key is required for subscribed topics')
        self.api_key = api_key
        self.api_secret = api_secret

        self.data = {}
        self.keys = {}
        self.got_partial = False
        self.exited = False
        self.status_dict = dict(timestamp = str(dt.datetime.now()))

        self._UPDATE_MARGIN = False
        self._UPDATE_POSITION = False

        # Subscribe to all pertinent endpoints
        wsURL = self.__get_url()
        self.logger.debug("Connecting to URL -- %s" % wsURL)
        self.__connect(wsURL, symbol)
        self.logger.info('Connected to WS.')

        # Connected. Wait for partials
        self.__wait_for_symbol(symbol)
        if api_key:
            self.__wait_for_account()
        self.got_partial = True
        self.dump_instrument()
        self.dump_margin()
        self.dump_position()

        self.logger.info('Got all market data. Starting.')

    def init(self):
        '''Connect to the websocket and clear data.'''
        self.logger.debug("Initializing WebSocket...")

        self.data = {}
        self.keys = {}
        self.exited = False

        # Subscribe to all pertinent endpoints
        wsURL = self.__get_url()
        self.logger.debug("Connecting to URL -- %s" % wsURL)
        self.__connect(wsURL, self.symbol)
        self.logger.info('Connected to WS.')

        # Connected. Wait for partials
        self.__wait_for_symbol(self.symbol)
        if self.api_key:
            self.__wait_for_account()
        self.logger.info('Got all market data. Starting.')
        self.dump_status()

    def write_headers(self):
        '''Log csv headers to subbed topics'''
        if 'execution' in self.total_subs:
            self.execution_logger.debug('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % ('execID','orderID',
            'clOrdID','account','symbol','side','orderQty','price','execType','ordType','commission','text'))
        if 'transact' in self.total_subs:
            self.transact_logger.debug('%s, %s, %s, %s, %s, %s, %s, %s, %s' % ('transactID','account','currency',
            'transactType','amount','fee','transactStatus','address','text'))
        if 'liquidation' in self.total_subs:
            self.liquidation_logger.debug('%s, %s, %s, %s, %s' % ('orderID', 'symbol','side','price','leavesQty'))
        if 'chat' in self.total_subs:
            self.chat_logger.debug('%s, %s, %s, %s, %s' % ('channelID','fromBot','id','message','user'))
        if 'quoteBin1m' in self.total_subs:
            self.quote_logger.debug('%s, %s, %s, %s, %s' % ('symbol','bidSize','bidPrice','askPrice','askSize'))
        if 'tradeBin1m' in self.total_subs:
            self.trade_logger.debug('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % ('symbol','open',
            'high','low','close','trades','volume','vwap','lastSize','turnover','homeNotional','foreignNotional'))
        return

    #
    # Lifecycle methods
    #

    def error(self, err):
        self._error = err
        self.update_status('Error')
        logger.log_error(err)
        self.dump_status()

    def __del__(self):
        self.exit()

    def exit(self):
        '''Call this to exit - will close websocket.'''
        self.exited = True
        self.logger.info('Websocket closing...')
        self.ws.close()
        self.update_status('Exited')
        self.dump_status()
        # Close logging files
        self.logger.removeHandler(self.logger.handlers[0])
        if 'execution' in self.total_subs:
            self.execution_logger.removeHandler(self.execution_logger.handlers[0])
        if 'transact' in self.total_subs:
            self.transact_logger.removeHandler(self.transact_logger.handlers[0])
        if 'liquidation' in self.total_subs:
            self.liquidation_logger.removeHandler(self.liquidation_logger.handlers[0])
        if 'chat' in self.total_subs:
            self.chat_logger.removeHandler(self.chat_logger.handlers[0])
        if 'quoteBin1m' in self.total_subs:
            self.quote_logger.removeHandler(self.quote_logger.handlers[0])
        if 'tradeBin1m' in self.total_subs:
            self.trade_logger.removeHandler(self.trade_logger.handlers[0])
        logger.close_error_logger()
        #logging.shutdown()
        print('Websocket closed.')

    def reset(self):
        self.logger.warning('Websocket resetting...')
        self.ws.close()
        self.update_status()
        self.dump_status()
        self.init()

    #
    # Public data functions
    #

    def get_data(self):
        '''Return entire data object, use for debugging'''
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
                    indicativeSettlePrice = instrument['indicativeSettlePrice'],
                    timestamp = instrument['timestamp'])

    #
    # Private data functions
    #

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
        withdrawableMargin = margin['withdrawableMargin'],
        timestamp = margin['timestamp'])

    def get_position_data(self):
        '''Return all relevant position data'''
        try:
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
            bankruptPrice = position['bankruptPrice'],
            timestamp = position['timestamp'])
        except:
            return dict(account = 0, symbol = 0, commission = 0, leverage = 0, crossMargin = 0, rebalancedPnl = 0,
            openOrderBuyQty = 0, openOrderBuyCost = 0, openOrderSellQty = 0, openOrderSellCost = 0, execBuyQty = 0,
            execBuyCost = 0, execSellQty = 0, execSellCost = 0, currentQty = 0, currentCost = 0, isOpen = 0, markPrice = 0,
            markValue = 0, homeNotional = 0, foreignNotional = 0, posState = 0, realisedPnl = 0, unrealisedPnl = 0, avgCostPrice = 0,
            avgEntryPrice = 0, breakEvenPrice = 0, liquidationPrice = 0, bankruptPrice = 0, timestamp = 0)

    def get_status_data(self, message):
        instrument = self.get_instrument_data()
        margin = self.get_margin_data()
        position = self.get_position_data()
        status = dict(
            status = message,
            connected = self.ws.sock.connected,
            market = instrument['state'],
            lastPrice = instrument['lastPrice'],
            markPrice = instrument['markPrice'],
            balance = margin['amount'],
            realisedPnl = margin['realisedPnl'],
            unrealisedPnl = margin['unrealisedPnl'],
            position = position['isOpen'],
            contractNum = position['currentQty'],
            contractCost = position['currentCost'],
            openOrders = position['openOrderBuyQty'] + position['openOrderSellQty'],
            timestamp = str(dt.datetime.now()))
        return status


    #
    # Json functions
    #

    def dump_instrument(self):
        '''Save instrument to json'''
        instrument = self.get_instrument_data()
        with open(settings.DATA_DIR + 'instrument.json', 'w') as handler:
            json.dump(instrument,handler)
        return

    def dump_position(self):
        '''Save position to json'''
        position = self.get_position_data()
        with open(settings.DATA_DIR + 'position.json', 'w') as handler:
            json.dump(position,handler)
        return

    def dump_margin(self):
        '''Save margin to json'''
        margin = self.get_margin_data()
        with open(settings.DATA_DIR + 'margin.json', 'w') as handler:
            json.dump(margin,handler)
        return

    def dump_status(self):
        '''Save status to json'''
        status = self.status_dict
        with open(settings.DATA_DIR + 'status.json', 'w') as handler:
            json.dump(status,handler)
        return

    def update_status(self, message = 'Restarting'):
        self.status_dict['status'] = message
        return

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
            # self.exit()
            # raise websocket.WebSocketTimeoutException('Couldn\'t connect to WS! Exiting.')
            self.reset()

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

        # Merge both subs types
        symbolSubs = self.symbol_subs
        genericSubs = self.generic_subs

        subscriptions = [sub + ':' + self.symbol for sub in symbolSubs]
        subscriptions += genericSubs

        urlParts = list(urllib.parse.urlparse(self.endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(','.join(subscriptions))
        return urllib.parse.urlunparse(urlParts)

    def __wait_for_account(self):
        '''On subscribe, this data will come down. Wait for it.'''
        account_subs = set(settings.PRIV_SYM_SUBS + settings.PRIV_GEN_SUBS)
        while not account_subs <= set(self.data):
            sleep(0.1)
        return

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        public_subs = set(settings.PUB_SYM_SUBS + settings.PUB_GEN_SUBS)
        while not public_subs <= set(self.data):
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

                # Update status every message received, except for partial
                if action != 'partial' and self.got_partial:
                    self.status_dict = self.get_status_data('Running')

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
                        self.chat_logger.debug('%s, %s, %s, %s, %s' % (data['channelID'], data['fromBot'], 
                        data['id'], str(data['message']).replace('\n', '').replace(',', '.'), data['user']))

                    # Store liquidations
                    elif table == 'liquidation':
                        data = message['data'][0]
                        self.liquidation_logger.debug('%s, %s, %s, %s, %s' % (data['orderID'], data['symbol'], 
                        data['side'], data['price'], data['leavesQty']))

                    # Store transactions
                    elif table == 'transact':
                        data = message['data'][0]
                        self.transact_logger.debug('%s, %s, %s, %s, %s, %s, %s, %s, %s' % (data['transactID'], 
                        data['account'], data['currency'], data['transactType'], data['amount'], data['fee'], 
                        data['transactStatus'], data['address'], data['text']))

                    # Store executions
                    elif table == 'execution':
                        data = message['data'][0]
                        self.execution_logger.debug('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % 
                        (data['execID'], data['orderID'], data['clOrdID'], data['account'], data['symbol'],
                        data['side'], data['orderQty'], 
                        data['stopPx'] if data['stopPx'] else (data['price'] or 0),
                        data['execType'], data['ordType'], data['commission'], data['text']))

                    # Store quote bins
                    elif table == 'quoteBin1m':
                        data = message['data'][0]
                        self.quote_logger.debug('%s, %s, %s, %s, %s' % (data['symbol'], data['bidSize'], 
                        data['bidPrice'], data['askPrice'], data['askSize']))

                    # Store trade bins
                    elif table == 'tradeBin1m':
                        data = message['data'][0]
                        self.trade_logger.debug('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
                        (data['symbol'], data['open'], data['high'], data['low'], data['close'], data['trades'],
                        data['volume'], data['vwap'], data['lastSize'], data['turnover'], data['homeNotional'], 
                        data['foreignNotional']))

                    # Limit the max length of the table to avoid excessive memory usage.
                    if len(self.data[table]) > settings.MAX_TABLE_LEN:
                        self.data[table] = self.data[table][settings.MAX_TABLE_LEN // 2:]

                elif action == 'update':
                    self.logger.debug('%s: updating %s' % (table, message['data']))

                    # Locate the item in the collection and update it.
                    for updateData in message['data']:
                        item = tools.find_by_keys(self.keys[table], self.data[table], updateData)
                        if not item:
                            continue  # No item found to update. Could happen before push

                        # Update this item.
                        item.update(updateData)

                    # Set margin update signal to True
                    if table == 'margin':
                        self._UPDATE_MARGIN = True
                        if settings.JSON_OUT:
                            self.dump_margin()

                    # Set position update signal to True
                    if table == 'position':
                        self._UPDATE_POSITION = True
                        if settings.JSON_OUT:
                            self.dump_position()

                    if table == 'instrument':
                        if settings.JSON_OUT:
                            self.dump_instrument()

                elif action == 'delete':
                    self.logger.debug('%s: deleting %s' % (table, message['data']))
                    # Locate the item in the collection and remove it.
                    for deleteData in message['data']:
                        item = tools.find_by_keys(self.keys[table], self.data[table], deleteData)
                        self.data[table].remove(item)
                else:
                    raise Exception("Unknown received action: %s" % action)

                self.dump_status()

        except:
            self.logger.error(traceback.format_exc())
            if(len(self.data)):
                if(len(self.data['instrument'])):
                    raise Exception("Unknown unhandled action: {0} \n Also Data: {1}".format(traceback.format_exc(),self.data))

    def __on_error(self, error):
        '''Called on fatal websocket errors. We exit on these.'''
        if '502' in error:
            self.logger.error("Bad Gateway, retrying.")
            self.update_status('502 Error')
            sleep(1)
            self.reset()

        elif not self.exited:
            self.logger.error("Error : %s" % error)
            # raise websocket.WebSocketException(error)
            self.reset()

        self.dump_status()

    def __reset(self):
        self.update_status('Resetting')
        self.data = {}
        self.keys = {}
        self.exited = False
        self._error = None
        self.dump_status()

    def __on_open(self):
        '''Called when the WS opens.'''
        self.logger.debug("Websocket Opened.")
        self.dump_status()

    def __on_close(self):
        '''Called on websocket close.'''
        self.update_status('Closed')
        self.logger.info('Websocket Closed')
        self.dump_status()