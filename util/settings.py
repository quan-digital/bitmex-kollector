# -*- coding: utf-8 -*-

# - Settings -
# * Quan.digital *

#####################################################
# Kollector Parameters
#####################################################

# Path to directory for data storage
DATA_DIR = 'data/'

# Max file size in bytes
MAX_FILE_SIZE = 100000000 # 100MB

# Time in seconds to wait after each loop
LOOP_INTERVAL = 1

#####################################################
# Websocket
#####################################################

# # API pair
# API_KEY = "7JEjfUfpt7T9gMno8NSw86Ld"
# API_SECRET = "Qya14PDUSNc8w7gRG_XGrv_Gy0IczQeeKrumVxsPhF6JnFdr"

# API pair
API_KEY = "rolMDEfUQwwASTckmugBkeM5"
API_SECRET = "anR6vCI74u10ggGAxAlCVN05ITrtC8bwiK4_s86vtXRARddP"


# Don't grow a table larger than 200. Helps cap memory usage.
MAX_TABLE_LEN = 200

# Timeout for Websocket, in seconds
WS_TIMEOUT = 5

# Instrument to market make on BitMEX.
SYMBOL = "XBTUSD"

# API endpoint URL
# BASE_URL = "https://www.bitmex.com/api/v1/"
BASE_URL = "https://testnet.bitmex.com/api/v1/"

