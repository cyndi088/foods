# -*- coding: utf-8 -*-
import scrapy


class Foods12331Spider(scrapy.Spider):
    name = 'foods12331'
    allowed_domains = ['www.foods12331.cn/web/index.jsp']
    start_urls = ['http://www.foods12331.cn/web/index.jsp/']

    def parse(self, response):
        pass
