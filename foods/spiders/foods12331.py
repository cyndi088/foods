# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy import FormRequest


class Foods12331Spider(scrapy.Spider):
    name = 'foods12331'
    allowed_domains = ['www.foods12331.cn/web/index.jsp']
    start_urls = ['http://www.foods12331.cn/web/index.jsp']

    def parse(self, response):
        pass

    def start_requests(self):
        url = 'http://www.foods12331.cn/food/detail/findFoodByPage.json'
        qualified_data = {
            'filters': '{"food_type": "粮食加工品", "check_flag": "合格", "order_by": "0", "pageNo": 473, "pageSize": 200, '
                       '"bar_code": "", "sampling_province": "", "name_first_letter": null, "food_name": null}'
        }
        unqualified_data = {
            'filters': '{"food_type": "粮食加工品", "check_flag": "不合格", "order_by": "0", "pageNo": 0, "pageSize": 20, '
                       '"bar_code": "", "sampling_province": "", "name_first_letter": null, "food_name": null}'
        }
        qualified_request = FormRequest(
            url=url, formdata=qualified_data, callback=self.qualified_detail, dont_filter=True
        )
        unqualified_request = FormRequest(
            url=url, formdata=unqualified_data, callback=self.unqualified_detail, dont_filter=True
        )

        yield qualified_request


    def qualified_detail(self, response):
        res = json.loads(response.text,  encoding='utf-8')
        print('111111111111111111111111111111111111111')
        print(response.text)
        print('111111111111111111111111111111111111111')

    def unqualified_detail(self, response):
        res = json.loads(response.text, encoding='utf-8')
        print('222222222222222222222222222222222222222')
        print(response.text)
        print('222222222222222222222222222222222222222')
