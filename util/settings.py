# -*- coding: utf-8 -*-

# - Settings -
# * Quan.digital *

#####################################################
# Kollector Parameters
#####################################################

# Path to directory for daily data storage
# 'data/' will be gitignored, so change directory on deploy
DATA_DIR = 'data/'

# Max file size in bytes
MAX_FILE_SIZE = 100000000 # 100MB

# Time in seconds to wait after each loop
LOOP_INTERVAL = 1

# Array of seconds when transition between days should occur
TRANSITION_SECS = [50, 52, 53, 54, 55, 56, 57, 58, 59, 60]

#####################################################
# Websocket
#####################################################

# API pair
API_KEY = "SeaqRPlqes8KtO37EjI_khFh"
API_SECRET = "j10Hg4MhYiYFIwUVRHCskk8JH-TrDfu7uRF8-iX18o3QoV0j"

# Don't grow a table larger than 200. Helps cap memory usage.
MAX_TABLE_LEN = 200

# Timeout for Websocket, in seconds
WS_TIMEOUT = 5

# Instrument to market make on BitMEX.
SYMBOL = "XBTUSD"

# API endpoint URL
BASE_URL = "https://www.bitmex.com/api/v1/"
# BASE_URL = "https://testnet.bitmex.com/api/v1/"