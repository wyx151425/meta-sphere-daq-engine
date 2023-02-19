import json

import scrapy
from dateutil.parser import parse

from ..items import WeiboItem, WeiboUserItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    search_url = 'https://s.weibo.com/weibo?q={}&page={}'
    weibo_url_format = "https://weibo.com/ajax/statuses/show?id={}"
    user_url_format = "https://weibo.com/ajax/profile/info?uid={}"
    prefix_url = 'https://s.weibo.com/'

    cookies = {
        "XSRF-TOKEN": "auESbpkyUl6XaudN-1mIijcu",
        "login_sid_t": "8f8249df350597d962ed1b47f613e4ff",
        "cross_origin_proto": "SSL",
        "_s_tentry": "passport.weibo.com",
        "Apache": "7698893317343.656.1676625108281",
        "SINAGLOBAL": "7698893317343.656.1676625108281",
        "ULV": "1676625108285:1: 1:1: 7698893317343.656.1676625108281:",
        "WBtopGlobal_register_version": "2023021717",
        "PC_TOKEN": "b7050a0e0e",
        "SCF": "AiMEd3XcailKoXZSrB6VEBc2pjNYoSGiCaRG66DKVPJBccPiEYeyU4Jzekvp3snX__jtSQ37zIFLpGapjiNu5Go.",
        "SUB": "_2A25O9Zu-DeRhGeRO4lQS8izMzD6IHXVtgop2rDV8PUJbmtANLRD6kW9NUErOun1T8UBGT0Y8unbq9lxGijT8m8K9",
        "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WW4qRg9syb2K5yYvmW6_z3F5JpX5K-hUgL.Foz71Kq0eoz7S0z2dJLoIpjLxKML12-L12zLxKqLB-qL1h-LxK-LBoMLB.Bt",
        "ALF": "1679390946",
        "WBPSESS": "Dt2hbAUaXfkVprjyrAZT_HaxuVWJ0u8PBhgtsyug_WRsocrV0L1Rka2vgIA5l5y-4RW5KPbU3YEZ5uRiNDNy410aQPr2ZRWesDE_0qHR0JgScuOQApt_dxTGBtUhybpFstgam_f4vB80_JsVHHexY1JoqwSKBMuIUNymCt93GiLdabk1nHsAMY5xTN6EHbaDyzJXH5u8HovIXaFCk0KhJg==",
        "UOR": ",,login.sina.com.cn",
        "SSOLoginState": "1676638818"
    }

    def start_requests(self):
        start_url = self.search_url.format('联想小新', '1')
        yield scrapy.Request(start_url, callback=self.parse, cookies=self.cookies)

    def parse(self, response, **kwargs):
        card_tags = response.xpath('//div[@class="card"]')

        weibo_items = []

        for card_tag in card_tags:
            weibo_item = WeiboItem()
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

            # 解析微博所属用户详细信息
            user_detail_url = "https://weibo.com/ajax/profile/info?uid={}".format(user_id)
            yield scrapy.Request(user_detail_url, callback=self.parse_user_detail, cookies=self.cookies,
                                 meta={"weibo_item": weibo_item})

            print(weibo_item)
            weibo_items.append(weibo_item)

        # 检索下一页
        # next_page_tag = response.xpath('//div[@class="m-page"]//a[@class="next"]')
        # if 0 != len(next_page_tag):
        #     next_url = self.prefix_url + next_page_tag[0].xpath('./@href').extract_first()
        #     yield scrapy.Request(next_url, callback=self.parse, cookies=self.cookies)

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
        weibo_item["region_name"] = weibo_obj["region_name"].split(" ")[-1]
        weibo_item["source"] = weibo_obj["source"]

        return weibo_item

    def parse_user_detail(self, response):
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

        return weibo_item
