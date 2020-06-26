# -*- coding: utf-8 -*-

# - Settings -
# * Quan.digital *

#####################################################
# Kollector Parameters
#####################################################

# Path to directory for daily data storage
# 'data/' will be gitignored, so change directory on deploy
#DATA_DIR = 'data/'
# DATA_DIR = 'kollection/' # for kollector
DATA_DIR = 'testnet_kaka/' # make bot name for bots

STORE_INSTRUMENT = True
STORE_MARGIN = True
STORE_POSITION = True

# Enable MongoDB for instrument, status and trades
DATABASE = True
MONGO_STR = "mongodb+srv://arc10:sleeping6pills9#ban@kollector0-chshr.mongodb.net/kollecta?retryWrites=true&w=majority"

# Fetch indicators via HTTP
INDICATORS = True

# Max file size in bytes
MAX_FILE_SIZE = 100000000 # 100MB

# Time in seconds to wait after each kollector loop
LOOP_INTERVAL = 1
# LOOP_INTERVAL = 30 # for bot

# Timeout in seconds on the main kollector loop for lack of status updates
LOOP_TIMEOUT = KHAN_TIMEOUT = 20

# Mail to warn on errors
MAIL_TO = "kauecano@gmail.com"

#####################################################
# Websocket
#####################################################

# Debug level websocket logger
DEBUG_WS = False

# Write instrument, position and margin data to json in DATA_DIR root
JSON_OUT = True

# Public topic subs
# available: ["instrument", "liquidation", "quoteBin1m", "tradeBin1m"]
PUB_SYM_SUBS = ["instrument", "liquidation", "quoteBin1m", "tradeBin1m"]
# PUB_SYM_SUBS = ["instrument"] # for bot
# available: ["chat"]
PUB_GEN_SUBS = ["chat"]
# PUB_GEN_SUBS = [] # for bot

# Private topic subs - needs API pair
# available: ["execution", "position"]
PRIV_SYM_SUBS = ["execution", "position"]
# available: ["transact", "margin"]
PRIV_GEN_SUBS = ["transact", "margin"]

# Don't grow a table larger than 200, helps cap memory usage
MAX_TABLE_LEN = 200

# Timeout for Websocket, in seconds
WS_TIMEOUT = 5

# Instrument pair on BitMEX
SYMBOL = "XBTUSD"

# API endpoint URL
BASE_URL = "https://www.bitmex.com/api/v1/"
# BASE_URL = "https://testnet.bitmex.com/api/v1/"