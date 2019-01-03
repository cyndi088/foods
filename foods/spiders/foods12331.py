# -*- coding: utf-8 -*-
import time
import json
import scrapy
from ..items import FoodsItem
from scrapy import FormRequest


class Foods12331Spider(scrapy.Spider):
    name = 'foods12331'
    allowed_domains = ['foods12331.cn']
    start_urls = ['http://www.foods12331.cn/web/index.jsp']

    def parse(self, response):
        url = 'http://www.foods12331.cn/food/detail/findFoodByPage.json'
        res = response.xpath("//div[@class='secenddiv']/a/@onclick").extract()
        # 食品类型
        for food_type in res:
            food_type = self.type_list(food_type)
            # 合格
            qualified_data = '{"food_type": \"%s\",' \
                             ' "check_flag": "合格",' \
                             ' "order_by": "1",' \
                             ' "pageNo": 0,' \
                             ' "pageSize": 20,' \
                             ' "bar_code": "",' \
                             ' "sampling_province": "",' \
                             ' "name_first_letter": null,' \
                             ' "food_name": null}' % food_type
            qualified_data = {
                'filters': qualified_data
            }
            qualified_request = FormRequest(
                url=url, formdata=qualified_data, meta={'food_type': food_type}, callback=self.qualified_detail,
                dont_filter=False
            )

            # 不合格
            unqualified_data = '{"food_type": \"%s\",' \
                               ' "check_flag": "不合格",' \
                               ' "order_by": "0",' \
                               ' "pageNo": 0,' \
                               ' "pageSize": 20,' \
                               ' "bar_code": "",' \
                               ' "sampling_province": "",' \
                               ' "name_first_letter": null,' \
                               ' "food_name": null}' % food_type
            unqualified_data = {
                'filters': unqualified_data
            }
            unqualified_request = FormRequest(
                url=url, formdata=unqualified_data, meta={'food_type': food_type}, callback=self.unqualified_detail,
                dont_filter=False
            )

            yield qualified_request

            yield unqualified_request

    # 合格列表
    def qualified_detail(self, response):
        url = response.url
        food_type = response.meta['food_type']
        res = json.loads(response.text,  encoding='utf-8')
        items = res['resultData']['items']
        current_nums = len(items)
        pageNo = res['resultData']['index'] - 1
        start = res['resultData']['start']
        total = res['resultData']['total']
        current_total = start + current_nums

        # 抽检详情url
        getResultUrl = 'http://www.foods12331.cn/food/detail/getResult.json'
        if items:
            for item in items:
                formdata = {}
                formdata['food_name'] = item['food_name']
                if item['production_name'] == '/':
                    formdata['production_name'] = '——'
                else:
                    formdata['production_name'] = item['production_name']
                formdata['food_model'] = item['food_model']
                request = FormRequest(
                    url=getResultUrl, formdata=formdata, callback=self.get_result, dont_filter=False
                )

                yield request

            # 当抓取数量小于总数时，抓取下一页
            if current_total < total:
                pageNo += 1
                # 合格
                qualified_data = '{"food_type": \"%s\",' \
                                 ' "check_flag": "合格",' \
                                 ' "order_by": "1",' \
                                 ' "pageNo": \"%d\",' \
                                 ' "pageSize": 20,' \
                                 ' "bar_code": "",' \
                                 ' "sampling_province": "",' \
                                 ' "name_first_letter": null,' \
                                 ' "food_name": null}' % (food_type, pageNo)
                qualified_data = {
                    'filters': qualified_data
                }
                qualified_request = FormRequest(
                    url=url, formdata=qualified_data, meta={'food_type': food_type}, callback=self.qualified_detail,
                    dont_filter=False
                )

                yield qualified_request

        else:
            print('合格列表结束')

    # 不合格列表
    def unqualified_detail(self, response):
        url = response.url
        food_type = response.meta['food_type']
        res = json.loads(response.text, encoding='utf-8')
        items = res['resultData']['items']
        current_nums = len(items)
        pageNo = res['resultData']['index'] - 1
        start = res['resultData']['start']
        total = res['resultData']['total']
        current_total = start + current_nums

        # 抽检详情url
        getResultUrl = 'http://www.foods12331.cn/food/detail/getResult.json'
        if items:
            for item in items:
                formdata = {}
                formdata['food_name'] = item['food_name']
                formdata['production_name'] = item['production_name']
                formdata['food_model'] = item['food_model']
                request = FormRequest(
                    url=getResultUrl, formdata=formdata, callback=self.get_result, dont_filter=False
                )

                yield request

            # 当抓取数量小于总数时，抓取下一页
            if current_total < total:
                pageNo += 1
                # 不合格
                unqualified_data = '{"food_type": \"%s\" ,' \
                                   ' "check_flag": "不合格",' \
                                   ' "order_by": "0",' \
                                   ' "pageNo": \"%d\",' \
                                   ' "pageSize": 20,' \
                                   ' "bar_code": "",' \
                                   ' "sampling_province": "",' \
                                   ' "name_first_letter": null,' \
                                   ' "food_name": null}' % (food_type, pageNo)
                unqualified_data = {
                    'filters': unqualified_data
                }
                unqualified_request = FormRequest(
                    url=url, formdata=unqualified_data, meta={'food_type': food_type}, callback=self.unqualified_detail,
                    dont_filter=False
                )

                yield unqualified_request

        else:
            print('不合格列表结束')

    # 抽检详情解析
    def get_result(self, response):
        res = json.loads(response.text, encoding='utf-8')
        foods = res['resultData']['foods']
        if foods:
            for fd in foods:
                food = FoodsItem()
                food['id'] = fd['id']
                food['check_no'] = fd['check_no']
                if not fd['food_brand']:
                    food['food_brand'] = '/'
                else:
                    food['food_brand'] = fd['food_brand']
                food['production_name'] = fd['production_name']
                food['production_adress'] = fd['production_adress']
                if not fd['producing_area']:
                    food['producing_area'] = '/'
                else:
                    food['producing_area'] = fd['producing_area']
                food['sampling_name'] = fd['sampling_name']
                food['sampling_province'] = fd['sampling_province']
                if not fd['sampling_adress']:
                    food['sampling_adress'] = '/'
                else:
                    food['sampling_adress'] = fd['sampling_adress']
                food['food_name'] = fd['food_name']
                food['food_model'] = fd['food_model']
                if not fd['food_product_time']:
                    food['food_product_time'] = self.get_product_time()
                else:
                    food['food_product_time'] = fd['food_product_time']
                food['food_type'] = fd['food_type']
                food['notice_no'] = fd['notice_no']
                if not fd['check_projiect']:
                    food['check_projiect'] = '/'
                else:
                    food['check_projiect'] = fd['check_projiect']
                if not fd['unqualified_reason']:
                    food['unqualified_reason'] = '/'
                else:
                    food['unqualified_reason'] = fd['unqualified_reason']
                if not fd['bar_code']:
                    food['bar_code'] = '/'
                else:
                    food['bar_code'] = fd['bar_code']
                if not fd['remark']:
                    food['remark'] = '/'
                else:
                    food['remark'] = fd['remark']
                food['check_flag'] = fd['check_flag']
                food['data_source'] = fd['data_source']
                print('***********************************')
                print(food)
                print('***********************************')

                yield food
        else:
            print('foods不存在')

    @staticmethod
    def type_list(name):
        str_list = name.split("'")
        res = str_list[1]
        return res

    @staticmethod
    def get_product_time():
        timeStamp = time.time() - 3600 * 24 * 30 * 6
        timeArray = time.localtime(timeStamp)
        product_time = time.strftime("%Y-%m-%d", timeArray)
        return product_time

