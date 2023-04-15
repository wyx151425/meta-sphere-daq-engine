import json

import scrapy
from dateutil.parser import parse

from items import WeiboCommentItem, WeiboUserItem
from utils import get_redis_conn


class WeiboCommentSpider(scrapy.Spider):
    name = 'weibo_comment'
    allowed_domains = ['weibo.com']
    start_urls = ['http://weibo.com/']

    f_weibo_comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count=20&uid=6779221195&fetch_level=0&max_id={}"
    f_weibo_user_info_url = "https://weibo.com/ajax/profile/info?uid={}"
    f_weibo_user_detail_url = "https://weibo.com/ajax/profile/detail?uid={}"

    def __init__(self, *args, **kwargs):
        super(WeiboCommentSpider, self).__init__(*args, **kwargs)

        domain = kwargs.pop("domain", "")
        self.allowed_domains = list(filter(None, domain.split(",")))

        cookie_str = get_redis_conn().get("DAQ_SPIDER:COOKIES:WEIBO")
        self.cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_str.split('; ')}

    def start_requests(self):
        task_code = "ms-daq-engine"
        task_keyword = "test"
        start_url = self.f_weibo_comments_url.format("4890372830923147", 0)
        yield scrapy.Request(start_url, callback=self.parse_weibo_comments, cookies=self.cookies,
                             meta={"mid": "4890372830923147", "task_code": task_code, "task_keyword": task_keyword})

    def parse_weibo_comments(self, response):
        mid = response.meta["mid"]
        task_code = response.meta["task_code"]
        task_keyword = response.meta["task_keyword"]

        json_obj = json.loads(response.text)
        weibo_comment_objs = json_obj["data"]

        for weibo_comment_obj in weibo_comment_objs:
            weibo_comment = WeiboCommentItem()
            weibo_comment["task_code"] = task_code
            weibo_comment["task_keyword"] = task_keyword
            weibo_comment["cid"] = weibo_comment_obj["mid"]
            weibo_comment["mid"] = weibo_comment_obj["analysis_extra"].split("|mid:")[-1]
            weibo_comment["uid"] = weibo_comment_obj["user"]["idstr"]
            weibo_comment["text_raw"] = weibo_comment_obj["text_raw"]
            weibo_comment["text"] = weibo_comment_obj["text"]
            weibo_comment["likes_count"] = weibo_comment_obj["like_counts"]
            weibo_comment["source"] = weibo_comment_obj["source"]
            weibo_comment["created_at"] = str(parse(weibo_comment_obj["created_at"])).split('+')[0]
            yield weibo_comment

            # 解析微博所属用户详细信息
            weibo_user_info_url = self.f_weibo_user_info_url.format(weibo_comment["uid"])
            yield scrapy.Request(weibo_user_info_url, callback=self.parse_weibo_user_info, cookies=self.cookies,
                                 meta={"task_code": task_code, "task_keyword": task_keyword})

        max_id = json_obj["max_id"]
        if 0 != max_id:
            # 解析微博所属用户详细信息
            weibo_comment_url = self.f_weibo_comments_url.format(mid, max_id)
            yield scrapy.Request(weibo_comment_url, callback=self.parse_weibo_comments, cookies=self.cookies,
                                 meta={"mid": mid, "task_code": task_code, "task_keyword": task_keyword})

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
