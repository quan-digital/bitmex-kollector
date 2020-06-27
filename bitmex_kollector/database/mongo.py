"""Core module for database related operations"""

from bitmex_kollector import settings
import pymongo
import json
import os


class KollectaDB():
    def __init__(self):
        self.client = self.make_client()
        self.kollecta_db = self.client.kollecta
        # self.clean_collections()
        self.setup_collections()

    def close(self):
        self.client.close()

    def make_client(self, db = 'kollecta'):
        """Utility funciton to load MongoClient"""
        client = pymongo.MongoClient(settings.MONGO_STR)
        return client

    def capped_collection(self, coll_name, max_size = 50000000):
        self.kollecta_db.create_collection(coll_name, capped=True, size=max_size)

    def drop_collection(self, coll_name):
        collection = getattr(self.kollecta_db, coll_name)
        collection.drop()

    def setup_collections(self):
        try:
            self.capped_collection('indicators', 100000000)
            self.capped_collection('status')
            self.capped_collection('instrument')
            self.capped_collection('candles')
        except pymongo.errors.CollectionInvalid:
            # print('Collections already created.')
            pass

    def clean_collections(self):
        self.drop_collection('indicators')
        self.drop_collection('status')
        self.drop_collection('instrument')
        self.drop_collection('candles')

    def insert_status(self, status_dict):
        self.kollecta_db.status.insert_one(status_dict)

    def insert_instrument(self, exec_dict):
        self.kollecta_db.instrument.insert_one(exec_dict)

    def insert_candle(self, trades_dict):
        self.kollecta_db.candles.insert_one(trades_dict)

    def insert_indicators(self, bill_dict):
        self.kollecta_db.indicators.insert_one(bill_dict)
    
    def get_latest_instrument(self):
        self.kollecta_db.instrument.find_one(sort=[( '_id', pymongo.DESCENDING )])

    def get_latest_status(self):
        self.kollecta_db.status.find_one(sort=[( '_id', pymongo.DESCENDING )])

    def get_latest_candle(self):
        self.kollecta_db.candles.find_one(sort=[( '_id', pymongo.DESCENDING )])

    def get_latest_indicators(self):
        self.kollecta_db.indicators.find_one(sort=[( '_id', pymongo.DESCENDING )])


if __name__ == "__main__":
    mongo_client = KollectaDB()
    sample = dict(test=True)
    # mongo_client.capped_collection('test2', max_size=100000)
    # mongo_client.setup_collections()
    mongo_client.insert_status(sample)
    mongo_client.insert_instrument(sample)
    mongo_client.insert_candles(sample)
    mongo_client.insert_indicators(sample)