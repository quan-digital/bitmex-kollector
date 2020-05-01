# -*- coding: utf-8 -*-

# - Settings -
# * Quan.digital *

#import util.secret as secret

#####################################################
# Kollector Parameters
#####################################################

# Path to directory for daily data storage
# 'data/' will be gitignored, so change directory on deploy
#DATA_DIR = 'data/'
# DATA_DIR = 'kollection/' # for kollector
DATA_DIR = 'testnet_kaka/' # make bot name for bots

# Max file size in bytes
MAX_FILE_SIZE = 100000000 # 100MB

# Time in seconds to wait after each kollector loop
# LOOP_INTERVAL = 1
LOOP_INTERVAL = 60 # for bot

# Mail to warn on errors
MAIL_TO = "kauecano@gmail.com"

#####################################################
# Websocket
#####################################################

# Write instrument, position and margin data to json in DATA_DIR root
JSON_OUT = True

# Public topic subs
# available: ["instrument", "liquidation", "quoteBin1m", "tradeBin1m"]
# PUB_SYM_SUBS = ["instrument", "liquidation", "quoteBin1m", "tradeBin1m"]
PUB_SYM_SUBS = ["instrument"] # for bot
# available: ["chat"]
# PUB_GEN_SUBS = ["chat"]
PUB_GEN_SUBS = [] # for bot

# Private topic subs - need API pair
# available: ["execution", "position"]
PRIV_SYM_SUBS = ["execution", "position"]
# available: ["transact", "margin"]
PRIV_GEN_SUBS = ["transact", "margin"]

# API pair
# API_KEY = "JP7uC-IALzH453flus79MKHG" # Mainet Kraudin
# API_SECRET = "4Dw_7hwiDLpTuqMQ5PuCIyd8oJVHcfzlI83ipRQLRlVGeBjd"
API_KEY = "rolMDEfUQwwASTckmugBkeM5" # Testnet Kaka
API_SECRET = "anR6vCI74u10ggGAxAlCVN05ITrtC8bwiK4_s86vtXRARddP"
# Uncomment below to use API from secret.py for more privacy
# API_KEY = secret.BITMEX_KEY
# API_SECRET secret.BITMEX_SECRET

# Don't grow a table larger than 200, helps cap memory usage
MAX_TABLE_LEN = 200

# Timeout for Websocket, in seconds
WS_TIMEOUT = 5

# Instrument pair on BitMEX
SYMBOL = "XBTUSD"

# API endpoint URL
# BASE_URL = "https://www.bitmex.com/api/v1/"
BASE_URL = "https://testnet.bitmex.com/api/v1/"