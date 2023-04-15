import json

import scrapy
from dateutil.parser import parse

from items import WeiboLikeItem, WeiboUserItem
from utils import get_redis_conn


class WeiboLikeSpider(scrapy.Spider):
    name = 'weibo_like'
    allowed_domains = ['weibo.com']
    start_urls = ['http://weibo.com/']

    f_weibo_likes_url = "https://weibo.com/ajax/statuses/likeShow?id={}&attitude_type=0&attitude_enable=1&page={}&count=20"
    f_weibo_user_info_url = "https://weibo.com/ajax/profile/info?uid={}"
    f_weibo_user_detail_url = "https://weibo.com/ajax/profile/detail?uid={}"

    def __init__(self, *args, **kwargs):
        super(WeiboLikeSpider, self).__init__(*args, **kwargs)

        domain = kwargs.pop("domain", "")
        self.allowed_domains = list(filter(None, domain.split(",")))

        cookie_str = get_redis_conn().get("DAQ_SPIDER:COOKIES:WEIBO")
        self.cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_str.split('; ')}

    def start_requests(self):
        task_code = "ms-daq-engine"
        task_keyword = "test"
        start_url = self.f_weibo_likes_url.format("4890372830923147", 1)
        yield scrapy.Request(start_url, callback=self.parse_weibo_likes, cookies=self.cookies,
                             meta={"mid": "4890372830923147", "page": 1, "task_code": task_code,
                                   "task_keyword": task_keyword})

    def parse_weibo_likes(self, response):
        mid = response.meta["mid"]
        page = response.meta["page"]
        task_code = response.meta["task_code"]
        task_keyword = response.meta["task_keyword"]

        json_obj = json.loads(response.text)
        weibo_like_objs = json_obj["data"]

        if len(weibo_like_objs) > 0:
            for weibo_like_obj in weibo_like_objs:
                weibo_like = WeiboLikeItem()
                weibo_like["task_code"] = task_code
                weibo_like["task_keyword"] = task_keyword
                weibo_like["mid"] = mid
                weibo_like["uid"] = weibo_like_obj["user"]["idstr"]
                weibo_like["like"] = weibo_like_obj["attitude"]
                yield weibo_like

                # 解析点赞所属用户详细信息
                weibo_user_info_url = self.f_weibo_user_info_url.format(weibo_like["uid"])
                yield scrapy.Request(weibo_user_info_url, callback=self.parse_weibo_user_info, cookies=self.cookies,
                                     meta={"task_code": task_code, "task_keyword": task_keyword})

            # 解析微博所属用户详细信息
            next_page = page + 1
            weibo_likes_url = self.f_weibo_likes_url.format(mid, next_page)
            yield scrapy.Request(weibo_likes_url, callback=self.parse_weibo_likes, cookies=self.cookies,
                                 meta={"mid": mid, "page": next_page, "task_code": task_code,
                                       "task_keyword": task_keyword})

    def parse_weibo_user_info(self, response):
        task_code = response.meta["task_code"]
        task_keyword = response.meta["task_keyword"]

        json_obj = json.loads(response.text)
        user_obj = json_obj["data"]["user"]

        weibo_user = WeiboUserItem()

        weibo_user["task_code"] = task_code
        weibo_user["task_keyword"] = task_keyword
        weibo_user["uid"] = user_obj["idstr"]
        weibo_user["screen_name"] = user_obj["screen_name"]
        weibo_user["gender"] = "男" if "m" == user_obj["gender"] else "女"  # m男 f女

        location = user_obj["location"].split(" ")
        weibo_user["province"] = location[0]
        if len(location) > 1:
            weibo_user["city"] = location[-1]

        weibo_user["description"] = user_obj["description"]
        weibo_user["profile_url"] = "https://weibo.com" + user_obj["profile_url"]
        weibo_user["verified"] = 1 if user_obj["description"] else 0

        weibo_user["follows_count"] = user_obj["friends_count"]
        if "friends_count_str" in user_obj:
            weibo_user["follows_count_str"] = user_obj["friends_count_str"]
        else:
            weibo_user["follows_count_str"] = ""

        weibo_user["followers_count"] = user_obj["followers_count"]
        if "followers_count_str" in user_obj:
            weibo_user["followers_count_str"] = user_obj["followers_count_str"]
        else:
            weibo_user["followers_count_str"] = ""

        weibo_user["weibos_count"] = user_obj["statuses_count"]
        if "statuses_count_str" in user_obj:
            weibo_user["weibos_count_str"] = user_obj["statuses_count_str"]
        else:
            weibo_user["weibos_count_str"] = ""

        weibo_user_detail_url = self.f_weibo_user_detail_url.format(weibo_user["uid"])
        yield scrapy.Request(weibo_user_detail_url, callback=self.parse_weibo_user_detail, cookies=self.cookies,
                             meta={"weibo_user": weibo_user})

    def parse_weibo_user_detail(self, response):
        weibo_user = response.meta["weibo_user"]

        json_obj = json.loads(response.text)
        user_obj = json_obj["data"]

        weibo_user["created_at"] = str(parse(user_obj["created_at"])).split("+")[0]

        birthday = user_obj["birthday"].split(" ")
        if len(birthday) > 1:
            weibo_user["birthday"] = birthday[0]
        weibo_user["constellation"] = birthday[-1]

        weibo_user["credit_level"] = user_obj["sunshine_credit"]["level"]

        yield weibo_user
