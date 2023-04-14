import json
import os
import sys

import scrapy
from dateutil.parser import parse
from ..utils import get_redis_conn

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from items import WeiboItem, WeiboUserItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    search_url = "https://s.weibo.com/weibo?q={}&page={}"
    weibo_url_format = "https://weibo.com/ajax/statuses/show?id={}"
    user_url_format = "https://weibo.com/ajax/profile/info?uid={}"
    prefix_url = 'https://s.weibo.com/'

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop("domain", "")
        # self.task_code = kwargs.pop("task_code")
        cookie_str = get_redis_conn().get("DAQ_SPIDER:COOKIES:WEIBO")
        self.cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_str.split('; ')}
        self.allowed_domains = list(filter(None, domain.split(",")))
        super(WeiboSpider, self).__init__(*args, **kwargs)

    # def make_requests_from_url(self, url):
    #     cookies_str = "SINAGLOBAL=7698893317343.656.1676625108281; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW4qRg9syb2K5yYvmW6_z3F5JpX5KMhUgL.Foz71Kq0eoz7S0z2dJLoIpjLxKML12-L12zLxKqLB-qL1h-LxK-LBoMLB.Bt; UOR=,,www.baidu.com; ULV=1679986583023:4:1:1:2908704636197.419.1679986583017:1677581670786; XSRF-TOKEN=9gIb8ASw11N-AxWytxYMDVaM; ALF=1683341028; SSOLoginState=1680749028; SCF=AiMEd3XcailKoXZSrB6VEBc2pjNYoSGiCaRG66DKVPJBwxD5DwPnT3SoJYoezuNbL1gdQ4OLPofGgB3Pady_gAs.; SUB=_2A25JKkG0DeRhGeRO4lQS8izMzD6IHXVqXjR8rDV8PUNbmtANLRWjkW9NUErOugbYiofoTDh5HTj1ccizdBEYT91N; WBPSESS=j1bUqD_uu3DXTXvt20EN1O1sMUDbqv3FNH3iWPBaPvGl9W44tnW4xNxyukYfeSnltGq5WvCqYsZ1zDdqc3zmu6ZXhEUuWc79St53LpJmg_8CarhS8JhP88SZVpUteAuDA0572h2dy77HyJD4cK0SFw=="
    #     cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies_str.split('; ')}
    #     return scrapy.Request(url, dont_filter=True, callback=self.parse, cookies=cookies)

    # def start_requests(self):
    #     r = get_redis_conn()
    #     r_key = "DAQ_TASK:KEYWORDS:" + self.task_code
    #     keywords = r.lrange(r_key, 0, -1)
    #     for keyword in keywords:
    #         start_url = self.search_url.format(keyword, "1")
    #         yield scrapy.Request(start_url, callback=self.parse, cookies=self.cookies,
    #                              meta={"task_code": self.task_code, "keyword": keyword})

    def start_requests(self):
        # r = get_redis_conn()
        # r_key = "DAQ_TASK:KEYWORDS:" + self.task_code
        start_url = self.search_url.format("联想小新", "1")
        yield scrapy.Request(start_url, callback=self.parse, cookies=self.cookies,
                                 meta={"task_code": "test", "keyword": "联想小新"})

    def parse(self, response, **kwargs):
        task_code = response.meta["task_code"]
        keyword = response.meta["keyword"]
        card_tags = response.xpath('//div[@class="card"]')

        for card_tag in card_tags:
            weibo_item = WeiboItem()
            weibo_item["task_code"] = task_code
            weibo_item["spider_code"] = self.name
            weibo_item["keyword"] = keyword
            weibo_item["user"] = {}

            # 避开热门文章Card
            weibo_url_tag = card_tag.xpath('.//div[@class="from"]//a/@href')
            if 0 == len(weibo_url_tag):
                continue

            # 获取微博URL
            weibo_url = "https:" + \
                        card_tag.xpath('.//div[@class="from"]//a/@href').extract_first().split('?refer_flag')[0]
            [user_id, weibo_id] = weibo_url.split('https://weibo.com/')[-1].split('/')

            weibo_item["weibo_url"] = weibo_url

            weibo_item["user_id"] = user_id
            user_profile_url = "https://weibo.com/u/" + user_id
            weibo_item["user_profile_url"] = user_profile_url

            # 解析微博详细内容
            yield scrapy.Request(self.weibo_url_format.format(weibo_id), callback=self.parse_weibo_detail,
                                 cookies=self.cookies,
                                 meta={"weibo_item": weibo_item})

        # 检索下一页
        next_page_tag = response.xpath('//div[@class="m-page"]//a[@class="next"]')
        if 0 != len(next_page_tag):
            next_url = self.prefix_url + next_page_tag[0].xpath('./@href').extract_first()
            yield scrapy.Request(next_url, callback=self.parse, cookies=self.cookies,
                                 meta={"task_code": self.task_code, "keyword": keyword})

    def parse_weibo_detail(self, response):
        weibo_item = response.meta['weibo_item']

        weibo_obj = json.loads(response.text)

        weibo_item["mid"] = weibo_obj["mid"]
        weibo_item["mblog_id"] = weibo_obj["mblogid"]
        weibo_item["created_at"] = str(parse(weibo_obj["created_at"])).split('+')[0]
        weibo_item["text_raw"] = weibo_obj["text_raw"]
        weibo_item["text"] = weibo_obj["text"]
        weibo_item["text_length"] = weibo_obj["textLength"]
        weibo_item["reposts_count"] = weibo_obj["reposts_count"]
        weibo_item["comments_count"] = weibo_obj["comments_count"]
        weibo_item["attitudes_count"] = weibo_obj["attitudes_count"]
        if "region_name" in weibo_obj:
            weibo_item["region_name"] = weibo_obj["region_name"].split(" ")[-1]
        weibo_item["source"] = weibo_obj["source"]

        # 解析微博所属用户详细信息
        user_detail_url = self.user_url_format.format(weibo_item["user_id"])
        yield scrapy.Request(user_detail_url, callback=self.parse_weibo_user, cookies=self.cookies,
                             meta={"weibo_item": weibo_item})

    def parse_weibo_user(self, response):
        weibo_item = response.meta['weibo_item']

        user = WeiboUserItem()

        user_obj = json.loads(response.text)["data"]["user"]

        user["id"] = user_obj["id"]
        user["id_str"] = user_obj["idstr"]

        user["screen_name"] = user_obj["screen_name"]
        user["gender"] = "男" if "m" == user_obj["gender"] else "女"  # m男 f女
        user["location"] = user_obj["location"]
        user["description"] = user_obj["description"]

        user["profile_url"] = "https://weibo.com" + user_obj["profile_url"]
        user["profile_image_url"] = user_obj["profile_image_url"]
        user["avatar_large_url"] = user_obj["avatar_large"]
        user["avatar_hd_url"] = user_obj["avatar_hd"]

        user["followers_count"] = user_obj["followers_count"]
        if "followers_count_str" in user_obj:
            user["followers_count_str"] = user_obj["followers_count_str"]
        else:
            user["followers_count_str"] = ""

        user["friends_count"] = user_obj["friends_count"]
        if "friends_count_str" in user_obj:
            user["friends_count_str"] = user_obj["friends_count_str"]
        else:
            user["friends_count_str"] = ""

        user["statuses_count"] = user_obj["statuses_count"]
        if "statuses_count_str" in user_obj:
            user["statuses_count_str"] = user_obj["statuses_count_str"]
        else:
            user["statuses_count_str"] = ""

        weibo_item["user"] = user

        yield weibo_item
