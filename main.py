import bitmex_kollector

if __name__ == '__main__':

    # Edit these bot config
    bitmex_kollector.settings.DATA_DIR = 'botname/'
    bitmex_kollector.settings.MAIL_TO = ['admin@mail.com', 'rep@mail.com']
    bitmex_kollector.settings.API_KEY = "E11UgSCaxoeaKGe8zgeg1d73"
    bitmex_kollector.settings.API_SECRET = "WbxFRGpqgrzqT4c8XHWYcQeIsmt40LizSVFMIxXXuEWfZQ6d"

    # Base bot config - no need to edit
    bitmex_kollector.settings.LOOP_INTERVAL = 30
    bitmex_kollector.settings.PUB_SYM_SUBS = ["instrument"]
    bitmex_kollector.settings.PUB_GEN_SUBS = []

    # Run
    kollector = bitmex_kollector.Kollector()
    kollector.run_loop()