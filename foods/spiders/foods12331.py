# -*- coding: utf-8 -*-
import json
import scrapy
from ..items import FoodsItem
from scrapy import FormRequest
from scrapy_redis.spiders import RedisSpider


class Foods12331Spider(RedisSpider):
    name = 'foods12331'
    allowed_domains = ['foods12331.cn']
    # start_urls = ['http://www.foods12331.cn/web/index.jsp']
    redis_key = "foods:start_url"

    def parse(self, response):
        url = 'http://www.foods12331.cn/food/detail/findFoodByPage.json'
        res = response.xpath("//div[@class='secenddiv']/a/@onclick").extract()
        # 食品类型
        for food_type in res:
            # 大分类下的小分类
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

            yield unqualified_request

            yield qualified_request

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
                formdata['production_name'] = item['production_name']
                formdata['food_model'] = item['food_model']
                request = FormRequest(
                    url=getResultUrl, formdata=formdata, callback=self.get_result, dont_filter=False,
                    meta={'qualification': '合格', 'food_type': food_type}
                )

                # 检查错误信息
                if formdata['production_name'] == 'null' or formdata['food_model'] == 'null':
                    print(item)
                    continue

                yield request

            # 当抓取数量小于总数时，抓取下一页
            if current_total < total:
                pageNo += 1
                # 合格
                qualified_data = '{"food_type": \"%s\",' \
                                 ' "check_flag": "合格",' \
                                 ' "order_by": "1",' \
                                 ' "pageNo": %d,' \
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
                if item['production_name']:
                    formdata['production_name'] = item['production_name']
                else:
                    formdata['production_name'] = 'null'
                if item['food_model']:
                    formdata['food_model'] = item['food_model']
                else:
                    formdata['food_model'] = 'null'

                request = FormRequest(
                    url=getResultUrl, formdata=formdata, callback=self.get_result, dont_filter=False,
                    meta={'qualification': '不合格', 'food_type': food_type}
                )

                yield request

            # 当抓取数量小于总数时，抓取下一页
            if current_total < total:
                pageNo += 1
                # 不合格
                unqualified_data = '{"food_type": \"%s\" ,' \
                                   ' "check_flag": "不合格",' \
                                   ' "order_by": "0",' \
                                   ' "pageNo": %d,' \
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
        qualification = response.meta['qualification']  # pipeline校验用
        food_type = response.meta['food_type']
        # 以防返回php错误页
        foods = None
        try:
            res = json.loads(response.text, encoding='utf-8')
            foods = res['resultData']['foods']
        except Exception as e:
            print(e)

        if foods:
            for fd in foods:
                food = FoodsItem()
                food['id'] = fd['id']
                food['check_no'] = fd['check_no']
                food['food_brand'] = fd['food_brand']
                food['production_name'] = fd['production_name']
                food['production_adress'] = fd['production_adress']
                food['producing_area'] = fd['producing_area']
                food['sampling_name'] = fd['sampling_name']
                food['sampling_province'] = fd['sampling_province']
                food['sampling_adress'] = fd['sampling_adress']
                food['food_name'] = fd['food_name']
                food['food_model'] = fd['food_model']
                food['food_product_time'] = fd['food_product_time']
                food['food_type'] = food_type
                food['notice_no'] = fd['notice_no']
                food['check_projiect'] = fd['check_projiect']
                food['unqualified_reason'] = fd['unqualified_reason']
                food['bar_code'] = fd['bar_code']
                food['remark'] = fd['remark']
                food['check_flag'] = fd['check_flag']
                food['data_source'] = fd['data_source']

                food['qualification'] = qualification

                yield food
        else:
            print('foods不存在')

    @staticmethod
    def type_list(name):
        str_list = name.split("'")
        res = str_list[1]
        return res
