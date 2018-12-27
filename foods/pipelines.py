# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class FoodsPipeline(object):
    def process_item(self, item, spider):
        return item


class MongodbPipeline(object):
    def __init__(self, mongo_host, mongo_port, mongo_user, mongo_psw, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_user = mongo_user
        self.mongo_psw = mongo_psw
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawlder):
        return cls(
            mongo_host=crawlder.settings.get('MONGO_HOST'),
            mongo_port=crawlder.settings.get('MONGO_PORT'),
            mongo_user=crawlder.settings.get('MONGO_USER'),
            mongo_psw=crawlder.settings.get('MONGO_PSW'),
            mongo_db=crawlder.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = MongoClient(host=self.mongo_host, port=self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        cls = item.__class__.__name__
        if cls == 'FoodsItem':
            self.save_foods(item)
        return item

    def save_foods(self, item):
        self.db['guojia'].save(dict(item))

