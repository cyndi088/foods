# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy import Request
from scrapy import FormRequest


class Foods12331Spider(scrapy.Spider):
    name = 'foods12331'
    allowed_domains = ['www.foods12331.cn/web/index.jsp']
    start_urls = ['http://www.foods12331.cn/web/index.jsp']

    # def parse(self, response):
    #     url = 'http://www.foods12331.cn/food/detail/findFoodByPage.json'
    #     res = response.xpath("//div[@class='secenddiv']/a/@onclick").extract()
    #     # 食品类型
    #     for food_type in res:
    #         food_type = self.type_list(food_type)
    #         # 合格
    #         qualified_data = '{"food_type": %s , "check_flag": "合格", "order_by": "0", "pageNo": 0, ' \
    #                          '"pageSize": 20,"bar_code": "", "sampling_province": "", "name_first_letter": null, ' \
    #                          '"food_name": null}' % food_type
    #         qualified_data = {
    #             'filters': qualified_data
    #         }
    #         qualified_request = FormRequest(
    #             url=url, callback=self.qualified_detail, formdata=qualified_data, dont_filter=False
    #         )
    #         print('0000000000000000000000000000000000000000000')
    #         yield qualified_request

    def start_requests(self):
        url = 'http://www.foods12331.cn/food/detail/findFoodByPage.json'

        # 合格
        qualified_data = {
            'filters': '{"food_type": "粮食加工品" , "check_flag": "合格", "order_by": "0", "pageNo": 0, "pageSize": 20, '
                       '"bar_code": "", "sampling_province": "", "name_first_letter": null, "food_name": null}'
        }
        print(qualified_data)
        qualified_request = FormRequest(
            url=url, formdata=qualified_data, callback=self.qualified_detail, dont_filter=False
        )

        # 不合格
        unqualified_data = {
            'filters': '{"food_type": "粮食加工品", "check_flag": "不合格", "order_by": "0", "pageNo": 0, "pageSize": 20, '
                       '"bar_code": "", "sampling_province": "", "name_first_letter": null, "food_name": null}'
        }
        unqualified_request = FormRequest(
            url=url, formdata=unqualified_data, callback=self.unqualified_detail, dont_filter=False
        )

        yield qualified_request

    def qualified_detail(self, response):
        res = json.loads(response.text,  encoding='utf-8')
        print('111111111111111111111111111111111111111')
        print(res)
        print('111111111111111111111111111111111111111')

    def unqualified_detail(self, response):
        res = json.loads(response.text, encoding='utf-8')
        print('222222222222222222222222222222222222222')
        print(response.text)
        print('222222222222222222222222222222222222222')

    @staticmethod
    def type_list(str):
        str_list = str.split("'")
        res = str_list[1]
        return res