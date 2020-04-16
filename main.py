import util.kollector as kollector

if __name__ == '__main__':
    # kollector = kollector.Kollector()
    kollector = kollector.Kollecta(storeMargin = True)
    kollector.run_loop()