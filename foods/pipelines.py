# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import random
from datetime import datetime, timedelta

import pymysql
from pymongo import MongoClient
from DBUtils.PooledDB import PooledDB


# from .items import FoodsItem

class FoodsPipeline(object):
    def process_item(self, item, spider):
        return item


class MongodbPipeline(object):
    def __init__(self,
                 mongo_host, mongo_port, mongo_user, mongo_psw, mongo_db,
                 mysql_host, mysql_port, mysql_user, mysql_psw, mysql_db
                 ):
        # mongodb 配置
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_user = mongo_user
        self.mongo_psw = mongo_psw
        self.mongo_db = mongo_db
        # mysql配置
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user
        self.mysql_psw = mysql_psw
        self.mysql_db = mysql_db

        # 开启连接池
        self.pool = PooledDB(pymysql, 16, host=self.mysql_host, port=self.mysql_port, user=self.mysql_user,
                             password=self.mysql_psw, db=self.mysql_db, charset="utf8")

        # 减少mysql查询次数, 在这里直接查询数据
        connect = self.pool.connection()
        cur = connect.cursor()

        # 区县查询语句
        sql_dist = "select region_name from region r where r.parent_id in " \
                   "(select r.region_id from region r where r.parent_id=" \
                   "(select r.region_id from region r where r.region_name='浙江省'))"
        # 城市查询语句
        sql_city = "select region_name from region r where r.parent_id=" \
                   "(select r.region_id from region r where r.region_name='浙江省')"

        cur.execute(sql_dist)
        self.district = cur.fetchall()  # 区县数据

        cur.execute(sql_city)
        self.city = cur.fetchall()  # 城市数据

    @classmethod
    def from_crawler(cls, crawlder):
        return cls(
            mongo_host=crawlder.settings.get('MONGO_HOST'),
            mongo_port=crawlder.settings.get('MONGO_PORT'),
            mongo_user=crawlder.settings.get('MONGO_USER'),
            mongo_psw=crawlder.settings.get('MONGO_PSW'),
            mongo_db=crawlder.settings.get('MONGO_DB'),
            mysql_host=crawlder.settings.get('MYSQL_HOST'),
            mysql_port=crawlder.settings.get('MYSQL_PORT'),
            mysql_user=crawlder.settings.get('MYSQL_USER'),
            mysql_db=crawlder.settings.get('MYSQL_DB'),
            mysql_psw=crawlder.settings.get('MYSQL_PASSWORD'),
        )

    def open_spider(self, spider):
        self.client = MongoClient(host=self.mongo_host, port=self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()
        self.pool.close()

    def process_item(self, item, spider):
        """保存为200k的形式"""
        # cls = item.__class__.__name__
        # if cls == 'FoodsItem':
        #     self.save_foods(item)
        food = {}
        food['stampDateTime'] = datetime.now()
        food['commodityName'] = self.check_null(item['food_name'])

        food['corpNameBy'] = self.check_null(item['sampling_name'])
        food['corpName'] = self.check_null(item['production_name'])
        food['addressBy'] = self.check_null(item['sampling_province'])  # 一致性处理 -- 浙江, 浙江省
        food['address'] = self.check_null(item['production_adress'])
        # 当被抽检地址或者生产地址为 '/',
        if food['addressBy'] == "/" or food['address'] == "/":
            # 并且被抽检商家和生产商相同
            if food['corpNameBy'] == food['corpName']:
                # 那么用另外一个代替
                if ['addressBy'] != "/":
                    food['address'] = food['addressBy']
                elif food['address'] != "/":
                    food['addressBy'] = food['address']
                else:
                    pass
        print(food['corpNameBy'], food['corpName'])
        food['addressByRegionId'] = self.get_region_id(item['sampling_province'], food['corpNameBy'])
        food['addressRegionId'] = self.get_region_id(item['production_adress'], food['corpName'])

        food['flId'] = self.get_food_type_id(item['food_type'])
        food['rwly_id'] = self.get_check_id(item['data_source'])
        food['model'] = self.check_null(item['food_model'])
        food['newsDetailTypeId'] = self.get_check_flag_id(item['check_flag'])
        food['note'] = '/'

        food['trademark'] = self.check_null(item['food_brand'])
        food['unqualifiedItem'] = self.check_null(item['check_projiect'])
        food['checkResult'] = '/'
        food['standardValue'] = '/'
        food['batchNumber'] = '/'

        food['ggh'] = self.check_null(item['notice_no'])
        food['ggrq'], food['productionDate'] = self.get_time(item['food_product_time'], food['ggh'])
        food['createDate'] = food['ggrq'] - timedelta(days=30)
        self.save_foods(food)
        return item

    @staticmethod
    def check_null(field):
        if field == 'null' or field is None:
            return '/'
        else:
            return field

    def get_check_flag_id(self, check_flag):
        check_flag = self.check_null(check_flag)

        if check_flag == '合格':
            return 1
        else:
            return 2

    # TODO 其他地区数据匹配
    def get_region_id(self, region_name, cron_name):
        """匹配地名为id"""
        region_name = self.check_null(region_name)

        if region_name == '/' and cron_name == '/':
            return 1
        # 先判断是否有region_name, 没有就使用crop_name
        if region_name != '/':
            match_name = region_name
        elif cron_name != "/":
            match_name = cron_name

        stp = []
        # self.district 浙江地区的区县数据
        for i in self.district:
            for j in i:
                # xx县/区
                if j[:-1] in match_name:
                    stp.append(j)
                    conn = self.pool.connection()
                    cur = conn.cursor()
                    # 格式化字符串的符号 必须要用 "" 和sql语句区分开
                    sql = 'select region_id from region r where r.region_name="{}"'.format(j)
                    cur.execute(sql)
                    region_id = int(cur.fetchone()[0])
                    conn.close()
                    return region_id
        if not stp:
            for x in self.city:
                for y in x:
                    if y[:-1] in match_name:
                        stp.append(y)
                        conn = self.pool.connection()
                        cur = conn.cursor()
                        sql = 'select region_id from region r where r.region_name="{}"'.format(y)
                        cur.execute(sql)
                        region_id = int(cur.fetchone()[0])
                        conn.close()
                        return region_id
        if not stp and "浙江" in match_name:
            return 12
        elif not stp and "浙江" not in match_name:
            return 1

    def get_food_type_id(self, name):
        if name != None:
            conn = self.pool.connection()
            cur = conn.cursor()
            sql1 = 'select sys_data_group_id from sys_data_item where key_value="{}"'.format(name)
            cur.execute(sql1)
            allData = cur.fetchall()  # ((data1,), (data2,), ...)
            if len(allData) == 1:
                conn.close()
                return allData[0][0]
            elif len(allData) > 1:
                # 先将每条data中的id查询一次, 匹配其parent_id
                sql2 = 'select parent_id from sys_data_group where id="{}"'
                for data in allData:
                    type_id = data[0]
                    cur.execute(sql2.format(type_id))
                    parent_id = cur.fetchone()[0]
                    # 如果parent_id==25 就是抽查的类型id
                    if 25 == parent_id:
                        conn.close()
                        return type_id
            else:
                conn.close()
                return 82
        else:
            return 82

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

    @staticmethod
    def get_check_id(check_name):
        if check_name:
            if '专项' in check_name:
                return 524
            elif '国抽' in check_name or '国' in check_name and not '地方' in check_name:
                return 520
            elif re.search(r'省抽?|地方|总.?局|自治区|兵团', check_name):
                return 521
            elif re.search(r'市级?', check_name):
                return 522
            elif re.search(r'区级?', check_name):
                return 523
            else:
                return 524

    @staticmethod
    def get_ggh_date(ggh):
        # 匹配公告号的年
        if re.search(r'201\d', ggh):
            y = re.search(r'201\d', ggh).group()
            m = random.randint(1, 3)
            d = random.randint(1, 19)
            date_list = [y, m, d]
            return datetime(*[int(i) for i in date_list])
        else:
            return '/'

    @staticmethod
    def get_production_time(proc_date):
        if proc_date.startswith('201'):
            # 匹配8位纯数字
            if re.match(r'\d{8}$', proc_date):
                date_str = re.findall('\d{8}$', proc_date)[0]
                date_list = [date_str[:4], date_str[4:6], date_str[6:8]]
                return datetime(*[int(i) for i in date_list])
            # 匹配格式化日期
            elif re.search(r'201\d.*?\d{1,2}.*?\d{1,2}', proc_date):
                date_list = re.findall(r'(201\d).*?(\d{1,2}).*?(\d{1,2})', proc_date)[0]  # [(...), (...), ...]

                return datetime(*[int(i) for i in date_list])
            # 匹配不完整格式
            elif re.search(r'201\d.*?\d{1,2}|201\d', proc_date):
                date_str = re.search(r'201\d.*?\d{1,2}|201\d', proc_date).group()
                # 只能匹配到年
                if len(date_str) == 4:
                    m = random.randint(1, 12)
                    d = random.randint(1, 19)
                    date_list = [date_str, m, d]
                    return datetime(*[int(i) for i in date_list])
                # 匹配到年和月
                else:
                    time_tuple = re.findall(r'(201\d).*?(\d{1,2})', proc_date)[0]
                    d = random.randint(1, 19)
                    date_list = [time_tuple[0], time_tuple[1], d]
                    return datetime(*[int(i) for i in date_list])
        # 匹配非20开头的日期, 并且包含格式化年月日的
        elif re.search(r'201\d.*?\d{1,2}.*?\d{1,2}', proc_date):
            date_list = re.findall(r'(201\d).*?(\d{1,2}).*?(\d{1,2})', proc_date)[0]
            # 月份不合法
            if date_list[1] not in range(1, 13):
                return '/'
            # 日期不合法
            if date_list[2] not in range(1, 32):
                return '/'
            return datetime(*[int(i) for i in date_list])
        else:
            return '/'

    def get_time(self, proc_date, ggh):
        # 首先判断传入的参数是否都为空
        proc_date = self.check_null(proc_date)
        ggh_date = self.get_ggh_date(ggh)

        production_date = self.get_production_time(proc_date)

        # 没有公告号和生产日期
        if production_date == "/" and ggh_date == "/":
            now = datetime.now()
            ggrq_date = now - timedelta(days=30 * random.randint(3, 6))
            try:
                production_date = ggrq_date - timedelta(days=30 * random.randint(3, 6))
            except Exception as e:
                print(e)
                production_date = ggrq_date - timedelta(days=31 * random.randint(3, 6))
            return ggrq_date, production_date
        # 没有生产日期
        elif ggh_date != "/" and production_date == "/":
            # 使用公告号的年, 随机月和日
            ggrq_date = datetime(year=ggh_date.year, month=random.randint(1, 6), day=random.randint(1, 19))
            production_date = ggrq_date - timedelta(days=30 * random.randint(3, 6))
            return ggrq_date, production_date
        # 没有公告号
        elif production_date != "/" and ggh_date == "/":
            # 使用生产日期的时间 随机增加3到6个月
            ggrq_date = production_date + timedelta(days=30 * random.randint(3, 6))
            return ggrq_date, production_date
        # 两者都有值
        else:
            ggh_year = ggh_date.year
            production_date = self.get_production_time(proc_date)
            proc_date_year = production_date.year
            # 公告日期必须在生产日期之后
            # if ggh_year == proc_date_year:
            #     ggrq_year = ggh_year
            #     # 在生产月份和当年12月之间随机
            #     ggrq_mon = random.randint(production_date.month, 12)
            #     ggrq_day = random.randint(1, 19)
            # 公开日期在2017, 生产日期在2016
            # elif ggh_year > proc_date_year:
            #     ggrq_year = proc_date_year
            #     ggrq_mon = random.randint(production_date.month, 12)
            #     ggrq_day = random.randint(1, 19)
            # else:
            #     ggrq_year = proc_date_year
            #     ggrq_mon = random.randint(production_date.month, 12)
            #     ggrq_day = random.randint(1, 19)
            #

            # 任何情况下公告日期和公告号, 应该在同年
            ggrq_year = ggh_year
            # 生产日期和公告号同年
            if ggh_year == proc_date_year:
                ggrq_mon = random.randint(production_date.month, 12)
            # 公告号是隔年的
            elif ggh_year > proc_date_year:
                # 公告日期的月份在1月和公告号月份之间随机
                ggrq_mon = random.randint(1, ggh_date.month)
            else:
                # 公告时间在生产日期之前, 不可能的情况, 使用生产日期的年份
                ggrq_mon = random.randint(production_date.month, 12)
            ggrq_day = random.randint(1, 19)

            ggrq_date = datetime(int(ggrq_year), int(ggrq_mon), int(ggrq_day))
            return ggrq_date, production_date

    def get_ggrq_date(self, proc_date, ggh):
        ggh_date = self.check_with_ggh(ggh)
        ggh_year = ggh_date.year

        proc_year = proc_date.year

        if ggh_year >= proc_year:
            ggrq_date = ggh_date + timedelta(days=30 * random.randint(1, 3))
            return ggrq_date
        else:
            ggrq_date = ggh_date + timedelta(days=15)
            return ggrq_date

    def save_foods(self, item):
        print(item)
        self.db['shiancha'].save(dict(item))

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
