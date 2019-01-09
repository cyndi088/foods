# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FoodsItem(scrapy.Item):
    id = scrapy.Field()
    check_no = scrapy.Field()
    food_brand = scrapy.Field()
    production_name = scrapy.Field()
    production_adress = scrapy.Field()
    producing_area = scrapy.Field()
    sampling_name = scrapy.Field()
    sampling_province = scrapy.Field()
    sampling_adress = scrapy.Field()
    food_name = scrapy.Field()
    food_model = scrapy.Field()
    food_product_time = scrapy.Field()
    food_type = scrapy.Field()
    notice_no = scrapy.Field()
    check_projiect = scrapy.Field()
    unqualified_reason = scrapy.Field()
    bar_code = scrapy.Field()
    remark = scrapy.Field()
    check_flag = scrapy.Field()
    data_source = scrapy.Field()

    qualification = scrapy.Field()

    # stampDateTime = scrapy.Field()  # 数据抓取时间
    # id = scrapy.Field()
    # commodityName = scrapy.Field()  # 食品名称
    # corpName = scrapy.Field()  # 标称生产企业名称
    # address = scrapy.Field()  # 标称生产企业地址
    # producing_area = scrapy.Field()
    # productionDate = scrapy.Field()  # 生产日期/批号
    # corpNameBy = scrapy.Field()  # 被抽检单位名称
    # addressBy = scrapy.Field()  # 被抽检单位地址
    # sampling_province = scrapy.Field()
    # fl = scrapy.Field()  # 分类
    # ggh = scrapy.Field()  # 公告所属刊次
    # model = scrapy.Field()  # 规格型号
    # newsDetailType = scrapy.Field()  # 是否合格
    # rwly = scrapy.Field()  # 抽检级别(省抽/国抽)
    # sampleOrderNumber = scrapy.Field()  # 样品单号
    # trademark = scrapy.Field()  # 商标
    # unqualifiedItem = scrapy.Field()  # 抽检项目
    # checkResult = scrapy.Field()  # 检查结果
    # standardValue = scrapy.Field()  # 标准值
