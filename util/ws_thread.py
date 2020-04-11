# -*- coding: utf-8 -*-

# - Websocket Thread -
# * Quan.digital *

# author: canokaue
# date: 10/04/2020
# kaue@engineer.com

# Websocket based on stock Bitmex API connectors - https://github.com/BitMEX/api-connectors/tree/master/official-ws/python
# and on the sample-market-maker WS thread - https://github.com/BitMEX/sample-market-maker/tree/master/market_maker/ws

# Introduces direct  data functions for better storage and less polluted
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
        # self.logger = logger.setup_logbook('ws')
        self.logger = logger.setup_logbook('ws', level=logging.DEBUG)

        self.liq_logger = logger.setup_db('liquidation')
        self.chat_logger = logger.setup_db('chat')
        self.exec_logger = logger.setup_db('exec')
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
        self.error_logger.error(err)

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

    def get_market_state(self):
        # checks if market is open or closed
        instrument = self.data['instrument'][0]
        return instrument['state'].lower()
    
    def get_trade_price(self):
        lastTrade = self.data['trade'][-1]
        lastPrice = lastTrade['price']
        instrument = self.data['instrument'][0]
        return tools.to_nearest(float(lastPrice or 0), instrument['tickSize'])

    def get_bid_price(self):
        lastQuote = self.data['quote'][-1]
        lastPrice = lastQuote['bidPrice']
        instrument = self.data['instrument'][0]
        return tools.to_nearest(float(lastPrice or 0), instrument['tickSize'])

    def get_ask_price(self):
        lastQuote = self.data['quote'][-1]
        lastPrice = lastQuote['askPrice']
        instrument = self.data['instrument'][0]
        return tools.to_nearest(float(lastPrice or 0), instrument['tickSize'])

    def get_mark_price(self):
        # Mark Price is used on all PNL calculations to avoid market manipulations
        instrument = self.data['instrument'][0]
        lastPrice = instrument['markPrice']
        return tools.to_nearest(float(lastPrice or 0), instrument['tickSize'])

    def get_24h_price(self):
        # Get previous 24h price
        instrument = self.data['instrument'][0]
        return tools.to_nearest(float(instrument['prevPrice24h'] or 0), instrument['tickSize'])

    def get_funding_rate(self):
        # if positive longs pay shorts
        # if negative shorts pay longs
        instrument = self.data['instrument'][0]
        return float(instrument['fundingRate'])

    def get_total_volume(self):
        instrument = self.data['instrument'][0]
        return round(float(instrument['totalVolume'] or 0))

    def get_24_volume(self):
        instrument = self.data['instrument'][0]
        return round(float(instrument['volume24h'] or 0))

    def get_volume(self):
        instrument = self.data['instrument'][0]
        return round(float(instrument['volume'] or 0))

    def get_instrument(self, symbol):
        instruments = self.data['instrument']
        matchingInstruments = [i for i in instruments if i['symbol'] == symbol]
        if len(matchingInstruments) == 0:
            raise Exception("Unable to find instrument or index with symbol: " + symbol)
        instrument = matchingInstruments[0]
        return instrument

    #
    # Private data functions
    #

    def get_balance(self):
        marginData = self.data['margin'][0]
        return float(marginData['walletBalance'])

    def get_available_margin(self):
        marginData = self.data['margin'][0]
        return float(marginData['availableMargin'])

    def get_withdrawable_margin(self):
        marginData = self.data['margin'][0]
        return float(marginData['withdrawableMargin'])

    def get_realised_pnl(self):
        marginData = self.data['margin'][0]
        return float(marginData['realisedPnl'])

    def get_unrealised_pnl(self):
        marginData = self.data['margin'][0]
        return float(marginData['unrealisedPnl'])

    def get_unrealised_profit(self):
        marginData = self.data['margin'][0]
        return float(marginData['unrealisedProfit'])

    def get_margin_leverage(self):
        marginData = self.data['margin'][0]
        return round(float(marginData['marginLeverage']), 2)

    def get_margin_used(self):
        # Percentage of margin used
        marginData = self.data['margin'][0]
        return round(float(marginData['marginUsedPcnt']), 4)

    def get_liq_price(self):
        instrument = self.data['instrument'][0]
        if(len(self.data['position'])):
            positionData = self.data['position'][0]
            return tools.to_nearest(float(positionData['liquidationPrice'] or 0), instrument['tickSize'])
        else:
            return float(0)

    def get_beven_price(self):
        # Break even price
        instrument = self.data['instrument'][0]
        if(len(self.data['position'])):
            positionData = self.data['position'][0]
            return tools.to_nearest(float(positionData['breakEvenPrice'] or 0), instrument['tickSize'])
        else:
            return float(0)
    def get_avgentry_price(self):
        # Average entry price on position
        instrument = self.data['instrument'][0]
        if(len(self.data['position'])):
            positionData = self.data['position'][0]
            return tools.to_nearest(float(positionData['avgEntryPrice'] or 0), instrument['tickSize'])
        else:
            return float(0)

    def get_leverage(self):
        # Leverage number or cross
        if(len(self.data['position'])):
            positionData = self.data['position'][0]
            if positionData['crossMargin']:
                return 'Cross'
            else:
                return round(float(positionData['leverage']))
        else:
            return float(0)

    def get_position_commission(self):
        # Market fee received from position
        positionData = self.data['position'][0]
        return round(float(positionData['commission']), 5)

    def get_position(self):
        # Position contracts
        instrument = self.data['instrument'][0]
        if(len(self.data['position'])):
            positionData = self.data['position'][0]
            return tools.to_nearest(float(positionData['currentQty'] or 0), instrument['tickSize'])
        else:
            return float(0)

    def get_account_id(self):
        # Gets account ID from position
        positionData = self.data['position'][0]
        return round(float(positionData['account']))

    def get_order_num(self):
        # Gets number of all orders
        orders = self.data['order']
        return len(orders)

    def get_all_orders(self):
        orders = self.data['order']
        return [o for o in orders]

    def get_all_order_ids(self):
        orders = self.data['order']
        return [o['orderID'] for o in orders]

    def get_all_order_clids(self):
        orders = self.data['order']
        return [o['clOrdID'] for o in orders]

    def get_current_orders(self):
        orders = self.data['order']
        return [(order['side'], order['orderQty'],order['price'] if order['price'] else order['stopPx'],
            order['clOrdID'][9:13]) for order in orders]

    def get_whole_order(self, clOrdIDPrefix):
        orders = self.data['order']
        # Filter to only open orders and clOrdIDPrefix
        return [o for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_clean_order(self, clOrdIDPrefix):
        orders = self.data['order']
        return [{'orderID': o['orderID'],
                'account': o['account'],
                'side': o['side'],
                'orderQty': o['orderQty'],
                'price': o['price'],
                'ordType': o['ordType'],
                'ordStatus': o['ordStatus'],
        'timestamp': o['timestamp']} for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_id(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['orderID'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_account(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['account'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_side(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['side'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_qty(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['orderQty'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_price(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['price'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_type(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['ordType'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_status(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['ordStatus'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_order_timestamp(self, clOrdIDPrefix):
        orders = self.data['order']
        return [o['timestamp'] for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and tools.order_leaves_quantity(o)]

    def get_stopPx(self):
        try:
            execution = self.data['execution'][-1]
            return execution['stopPx']
        except: 
            return 0


    def get_status(self):
        status_dict = {'timestamp' : self.get_timestamp(),
                'latest_price' : self.get_trade_price(),
                'mark_price' : self.get_mark_price(),
                'balance' : self.get_balance(),
                'order_num' : self.get_order_num(),
                'open_orders' : self.get_current_orders(),
                'position' : self.get_position(),
                'leverage' : self.get_leverage(),
                'liquidation' : self.get_liq_price(),
                'funding_rate' : self.get_funding_rate(),
                'unrealized_pnl' : self.get_unrealised_pnl(),
                'realized_pnl' : self.get_realised_pnl(),
                'volume' : self.get_volume(),
                'avg_entry_price' : self.get_avgentry_price(),
                'break_even' : self.get_beven_price(),
                'unrealized_profit' : self.get_unrealised_profit(),
                'available_margin' : self.get_available_margin(),
                }
        return status_dict

    def get_delta_dep(self):
        wallet = self.data['wallet'][0]
        return wallet['deltaDeposited']

    def get_prev_dep(self):
        wallet = self.data['wallet'][0]
        return wallet['prevDeposited']

    def get_delta_with(self):
        wallet = self.data['wallet'][0]
        return wallet['deltaWithdrawn']

    def get_prev_with(self):
        wallet = self.data['wallet'][0]
        return wallet['prevWithdrawn']

    def get_wallet(self):
        wallet = self.data['wallet'][0]
        return wallet

    def get_prev_wallet(self):
        wallet = self.data['wallet'][0]
        return wallet['prevAmount']

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
        '''
        Generate a connection URL. We can define subscriptions right in the querystring.
        Most subscription topics are scoped by the symbol we're listening to.
        '''

        symbolSubs = ["instrument", "liquidation"]
        genericSubs = ["chat"]

        subscriptions = [sub + ':' + self.symbol for sub in symbolSubs]
        subscriptions += genericSubs

        urlParts = list(urllib.parse.urlparse(self.endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(','.join(subscriptions))
        return urllib.parse.urlunparse(urlParts)

    def __wait_for_account(self):
        '''On subscribe, this data will come down. Wait for it.'''
        # while not {'margin', 'position', 'order'} <= set(self.data):
        #     sleep(0.1)
        return

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        sleep(5)
        while not {'instrument', 'liquidation', 'chat'} <= set(self.data):
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

                    # Limit the max length of the table to avoid excessive memory usage.
                    # Don't trim orders because we'll lose valuable state if we do.
                    if table not in ['order'] and len(self.data[table]) > settings.MAX_TABLE_LEN:
                        self.data[table] = self.data[table][settings.MAX_TABLE_LEN // 2:]

                elif action == 'update':
                    self.logger.debug('%s: updating %s' % (table, message['data']))
                    # Locate the item in the collection and update it.
                    for updateData in message['data']:
                        item = tools.find_by_keys(self.keys[table], self.data[table], updateData)
                        if not item:
                            continue  # No item found to update. Could happen before push
                            
                        # Log executions
                        if table == 'order':
                            is_canceled = 'ordStatus' in updateData and updateData['ordStatus'] == 'Canceled'
                            if 'cumQty' in updateData and not is_canceled:
                                contExecuted = updateData['cumQty'] - item['cumQty']
                                if contExecuted > 0:
                                    instrument = self.get_instrument(item['symbol'])

                                    # Here we log (item['price'] or 0) because when positions are market closed 
                                    # through bitmex dashboard, neither price nor stopPx is returns, which can lead to errors
                                    self.logger.info("Execution: %s %d Contracts of %s at %.*f" %
                                             (item['side'], contExecuted, item['symbol'],
                                             # here used to be tickLog but lets make it simple
                                              1, item['stopPx'] if item['stopPx'] else (item['price'] or 0)))
                                    
                                    self.exec_logger.info("%s, %s, %s, %s, %s" %
                                             (item['clOrdID'][9:13], item['side'], contExecuted, 
                                             item['symbol'], item['stopPx'] if item['stopPx'] else (item['price'] or 0)))


                                    # Execution handling for email notification
                                    
                                    # High step case
                                    if str(item['clOrdID'][9:12]) == ('Buy' or 'Sel'):
                                        if int(item['clOrdID'][12]) > settings.SEND_EMAIL_GRADLE:
                                            settings._HIGH_STEP_ORDER = True
                                            self._ExecStatusHighStep = item

                                    # Stop reached case
                                    elif str(item['clOrdID'][9:12]) == 'Stm':
                                        settings._REACHED_STOP = True
                                        self._ExecStatusStop = item

                                    # Target reached case
                                    elif str(item['clOrdID'][9:12]) == 'Tgt':
                                        settings._REACHED_TARGET = True
                                        self._ExecStatusTarget = item
                                    
                        # Update this item.
                        item.update(updateData)

                        # Remove cancelled / filled orders
                        if table == 'order' and not tools.order_leaves_quantity(item):
                            self.data[table].remove(item)
                        
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







