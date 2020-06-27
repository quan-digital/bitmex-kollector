import bitmex_kollector
from bitmex_kollector.util.logger import setup_logger
import logging


if __name__ == '__main__':

    setup_logger()

    # # Edit these bot config
    # bitmex_kollector.settings.DATA_DIR = 'botname/'
    # bitmex_kollector.settings.MAIL_TO = ['admin@mail.com', 'rep@mail.com']

    # Base bot config - no need to edit
    # bitmex_kollector.settings.LOOP_INTERVAL = 30
    # bitmex_kollector.settings.PUB_SYM_SUBS = ["instrument"]
    # bitmex_kollector.settings.PUB_GEN_SUBS = []

    # Run
    try:
        kollector = bitmex_kollector.Kollector("kEz41tV6Y4CdWpXeXqNM_nw0", 
        "D_6jHl5vwjN5VWHcTlefzzEHOupduXhVyn0bZl4MpfY3rIHA", log_level = logging.DEBUG)
        kollector.run_loop()
    except KeyboardInterrupt:
        kollector.close(connection=False)