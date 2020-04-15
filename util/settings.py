# -*- coding: utf-8 -*-

# - Settings -
# * Quan.digital *

import util.secret as secret

#####################################################
# Kollector Parameters
#####################################################

# Path to directory for daily data storage
# 'data/' will be gitignored, so change directory on deploy
#DATA_DIR = 'data/'
DATA_DIR = 'kollection/'

# Max file size in bytes
MAX_FILE_SIZE = 100000000 # 100MB

# Time in seconds to wait after each loop
LOOP_INTERVAL = 1

# Array of seconds when transition between days should occur
TRANSITION_SECS = [56, 57, 58, 59]

#####################################################
# Websocket
#####################################################

# API pair
API_KEY = "JP7uC-IALzH453flus79MKHG" # Mainet Kraudin
API_SECRET = "4Dw_7hwiDLpTuqMQ5PuCIyd8oJVHcfzlI83ipRQLRlVGeBjd"
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
BASE_URL = "https://www.bitmex.com/api/v1/"
# BASE_URL = "https://testnet.bitmex.com/api/v1/"