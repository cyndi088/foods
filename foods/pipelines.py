# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

from .items import FoodsItem


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


            # food = FoodsItem()
            # if item['qualification'] == '不合格' and item['check_flag'] == '合格':
            #     return
            # else:
                # food['id'] = item['id']
                # food['check_no'] = item['check_no']
                # if not item['food_brand']:
                #     food['food_brand'] = '/'
                # else:
                #     food['food_brand'] = item['food_brand']
                # food['production_name'] = item['production_name']
                # food['production_adress'] = item['production_adress']
                # if not item['producing_area']:
                #     food['producing_area'] = '/'
                # else:
                #     food['producing_area'] = item['producing_area']
                # food['sampling_name'] = item['sampling_name']
                # food['sampling_province'] = item['sampling_province']
                # if not item['sampling_adress']:
                #     food['sampling_adress'] = '/'
                # else:
                #     food['sampling_adress'] = item['sampling_adress']
                # food['food_name'] = item['food_name']
                # food['food_model'] = item['food_model']
                # if not item['food_product_time']:
                #     # food['food_product_time'] = self.get_product_time()
                #     food['food_product_time'] = '/'
                # else:
                #     food['food_product_time'] = item['food_product_time']
                # food['food_type'] = item['food_type']
                # food['notice_no'] = item['notice_no']
                # if not item['check_projiect']:
                #     food['check_projiect'] = '/'
                # else:
                #     food['check_projiect'] = item['check_projiect']
                # if not item['unqualified_reason']:
                #     food['unqualified_reason'] = '/'
                # else:
                #     food['unqualified_reason'] = item['unqualified_reason']
                # if not item['bar_code']:
                #     food['bar_code'] = '/'
                # else:
                #     food['bar_code'] = item['bar_code']
                # if not item['remark']:
                #     food['remark'] = '/'
                # else:
                #     food['remark'] = item['remark']
                # food['check_flag'] = item['check_flag']
                # food['data_source'] = item['data_source']
                # print('***********************************')
                # print(food)
                # print('***********************************')
                # self.save_foods(food)
        # return item

    def save_foods(self, item):
        self.db['shiancha_2.0'].save(dict(item))

    # @staticmethod
    # def get_product_time():
    #     timeStamp = time.time() - 3600 * 24 * 30 * 6
    #     timeArray = time.localtime(timeStamp)
    #     product_time = time.strftime("%Y-%m-%d", timeArray)
    #     return product_time
    #
    # @staticmethod
    # def time_format(time_string):
    #     res = time_string.st.replace('/', '-')
    #     return res
