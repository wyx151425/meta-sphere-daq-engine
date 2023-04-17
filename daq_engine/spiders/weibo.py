import json
import os
import sys

import scrapy
from dateutil.parser import parse
from scrapy_redis.spiders import RedisSpider

from ..utils import get_redis_conn

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from items import WeiboItem, WeiboUserItem, WeiboLikeItem, WeiboCommentItem, WeiboRepostItem


class WeiboSpider(RedisSpider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    redis_key = ""

    f_redis_key = "DAQ_TASK:KEYWORDS:{}"

    f_weibo_prefix_url = 'https://s.weibo.com/{}'
    f_weibo_search_url = "https://s.weibo.com/weibo?q={}&page={}"

    f_weibo_url = "https://weibo.com/ajax/statuses/show?id={}"
    f_weibo_link_url = "https://weibo.com/{}/{}"
    f_weibo_user_info_url = "https://weibo.com/ajax/profile/info?uid={}"
    f_weibo_user_detail_url = "https://weibo.com/ajax/profile/detail?uid={}"

    f_weibo_likes_url = "https://weibo.com/ajax/statuses/likeShow?id={}&attitude_type=0&attitude_enable=1&page={}&count=20"
    f_weibo_comments_url = "https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={}&is_show_bulletin=2&is_mix=0&count=20&uid=6779221195&fetch_level=0&max_id={}"
    f_weibo_reposts_url = "https://weibo.com/ajax/statuses/repostTimeline?id={}&page={}&moduleID=feed&count=20"

    def __init__(self, *args, **kwargs):
        cookie_str = get_redis_conn().get("DAQ_SPIDER:COOKIES:WEIBO")
        self.cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_str.split('; ')}

        self.task_code = kwargs.pop("task_code")
        self.redis_key = self.f_redis_key.format(self.task_code)

        super(WeiboSpider, self).__init__(*args, **kwargs)

    def make_requests_from_url(self, keyword):
        weibo_search_url = self.f_weibo_search_url.format(keyword, 1)
        return scrapy.Request(weibo_search_url, dont_filter=True, callback=self.parse_weibo_search,
                              cookies=self.cookies,
                              meta={"task_code": self.task_code, "task_keyword": keyword})

    def parse_weibo_search(self, response):
        task_code = response.meta["task_code"]
        task_keyword = response.meta["task_keyword"]
        card_tags = response.xpath('//div[@class="card"]')

        for card_tag in card_tags:
            weibo_item = WeiboItem()
            weibo_item["task_code"] = task_code
            weibo_item["task_keyword"] = task_keyword

            # 避开热门文章Card
            weibo_url_tag = card_tag.xpath('.//div[@class="from"]//a/@href')
            if 0 == len(weibo_url_tag):
                continue

            weibo_url = card_tag.xpath('.//div[@class="from"]//a/@href').extract_first()
            [uid, hash_mid] = weibo_url.split('?refer_flag')[0].split('//weibo.com/')[-1].split('/')

            weibo_item["hash_mid"] = hash_mid
            weibo_item["uid"] = uid
            weibo_item["weibo_url"] = self.f_weibo_link_url.format(weibo_item["uid"], weibo_item["hash_mid"])

            user_screen_name = card_tag.xpath('.//div[@class="info"]/div[2]/a/text()').extract_first()
            weibo_item["user_screen_name"] = user_screen_name

            # 解析微博详细内容
            yield scrapy.Request(self.f_weibo_url.format(hash_mid), callback=self.parse_weibo,
                                 cookies=self.cookies,
                                 meta={"weibo_item": weibo_item})

        # 检索下一页
        next_page_tag = response.xpath('//div[@class="m-page"]//a[@class="next"]')
        if 0 != len(next_page_tag):
            next_url = self.f_weibo_prefix_url.format(next_page_tag[0].xpath('./@href').extract_first())
            yield scrapy.Request(next_url, callback=self.parse_weibo_search, cookies=self.cookies,
                                 meta={"task_code": task_code, "task_keyword": task_keyword})

    def parse_weibo(self, response):
        weibo_item = response.meta['weibo_item']

        weibo_obj = json.loads(response.text)

        weibo_item["mid"] = weibo_obj["mid"]
        weibo_item["created_at"] = str(parse(weibo_obj["created_at"])).split("+")[0]

        weibo_item["text_raw"] = weibo_obj["text_raw"]
        weibo_item["text"] = weibo_obj["text"]
        weibo_item["text_length"] = weibo_obj["textLength"]
        weibo_item["source"] = weibo_obj["source"]

        if "region_name" in weibo_obj:
            weibo_item["region_name"] = weibo_obj["region_name"].split(" ")[-1]
        else:
            weibo_item["region_name"] = "其他"

        weibo_item["reposts_count"] = weibo_obj["reposts_count"]
        weibo_item["comments_count"] = weibo_obj["comments_count"]
        weibo_item["likes_count"] = weibo_obj["attitudes_count"]

        yield weibo_item

        # 解析微博所属用户信息
        weibo_user_info_url = self.f_weibo_user_info_url.format(weibo_item["uid"])
        yield scrapy.Request(weibo_user_info_url, callback=self.parse_weibo_user_info, cookies=self.cookies,
                             meta={"task_code": weibo_item["task_code"], "task_keyword": weibo_item["task_keyword"]})

        # 解析微博点赞信息
        weibo_likes_url = self.f_weibo_likes_url.format(weibo_item["mid"], 1)
        yield scrapy.Request(weibo_likes_url, callback=self.parse_weibo_likes, cookies=self.cookies,
                             meta={"mid": weibo_item["mid"], "page": 1, "task_code": weibo_item["task_code"],
                                   "task_keyword": weibo_item["task_keyword"]})
        # 解析微博评论信息
        weibo_comments_url = self.f_weibo_comments_url.format(weibo_item["mid"], 0)
        yield scrapy.Request(weibo_comments_url, callback=self.parse_weibo_comments, cookies=self.cookies,
                             meta={"mid": weibo_item["mid"], "task_code": weibo_item["task_code"],
                                   "task_keyword": weibo_item["task_keyword"]})

        # 解析微博转发信息
        weibo_reposts_url = self.f_weibo_reposts_url.format(weibo_item["mid"], 1)
        yield scrapy.Request(weibo_reposts_url, callback=self.parse_weibo_reposts, cookies=self.cookies,
                             meta={"oid": weibo_item["mid"], "page": 1, "task_code": weibo_item["task_code"],
                                   "task_keyword": weibo_item["task_keyword"]})

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
        else:
            weibo_user["city"] = ""

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
        else:
            weibo_user["birthday"] = ""
        weibo_user["constellation"] = birthday[-1]

        weibo_user["credit_level"] = user_obj["sunshine_credit"]["level"]

        yield weibo_user

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

            # 下一页
            next_page = page + 1
            weibo_likes_url = self.f_weibo_likes_url.format(mid, next_page)
            yield scrapy.Request(weibo_likes_url, callback=self.parse_weibo_likes, cookies=self.cookies,
                                 meta={"mid": mid, "page": next_page, "task_code": task_code,
                                       "task_keyword": task_keyword})

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

            # 解析评论所属用户详细信息
            weibo_user_info_url = self.f_weibo_user_info_url.format(weibo_comment["uid"])
            yield scrapy.Request(weibo_user_info_url, callback=self.parse_weibo_user_info, cookies=self.cookies,
                                 meta={"task_code": task_code, "task_keyword": task_keyword})

        max_id = json_obj["max_id"]
        if 0 != max_id:
            # 下一页
            weibo_comment_url = self.f_weibo_comments_url.format(mid, max_id)
            yield scrapy.Request(weibo_comment_url, callback=self.parse_weibo_comments, cookies=self.cookies,
                                 meta={"mid": mid, "task_code": task_code, "task_keyword": task_keyword})

    def parse_weibo_reposts(self, response):
        oid = response.meta["oid"]
        page = response.meta["page"]
        task_code = response.meta["task_code"]
        task_keyword = response.meta["task_keyword"]

        json_obj = json.loads(response.text)
        weibo_repost_objs = json_obj["data"]

        if len(weibo_repost_objs) > 0:
            for weibo_repost_obj in weibo_repost_objs:
                weibo_repost = WeiboRepostItem()
                weibo_repost["task_code"] = task_code
                weibo_repost["task_keyword"] = task_keyword

                weibo_repost["mid"] = weibo_repost_obj["mid"]
                weibo_repost["oid"] = oid
                weibo_repost["uid"] = weibo_repost_obj["user"]["idstr"]
                weibo_repost["hash_mid"] = weibo_repost_obj["mblogid"]
                weibo_repost["created_at"] = str(parse(weibo_repost_obj["created_at"])).split('+')[0]

                weibo_repost["text_raw"] = weibo_repost_obj["text_raw"]
                weibo_repost["text"] = weibo_repost_obj["text"]
                weibo_repost["source"] = weibo_repost_obj["source"]
                weibo_repost["weibo_url"] = self.f_weibo_link_url.format(weibo_repost["uid"], weibo_repost["hash_mid"])

                if "region_name" in weibo_repost_obj:
                    weibo_repost["region_name"] = weibo_repost_obj["region_name"].split(" ")[-1]
                else:
                    weibo_repost["region_name"] = "其他"

                weibo_repost["reposts_count"] = weibo_repost_obj["reposts_count"]
                weibo_repost["comments_count"] = weibo_repost_obj["comments_count"]
                weibo_repost["likes_count"] = weibo_repost_obj["attitudes_count"]

                weibo_repost["user_screen_name"] = weibo_repost_obj["user"]["screen_name"]

                yield weibo_repost

                # 解析转发所属用户详细信息
                weibo_user_info_url = self.f_weibo_user_info_url.format(weibo_repost["uid"])
                yield scrapy.Request(weibo_user_info_url, callback=self.parse_weibo_user_info, cookies=self.cookies,
                                     meta={"task_code": task_code, "task_keyword": task_keyword})

            # 下一页
            next_page = page + 1
            weibo_reposts_url = self.f_weibo_reposts_url.format(oid, next_page)
            yield scrapy.Request(weibo_reposts_url, callback=self.parse_weibo_reposts, cookies=self.cookies,
                                 meta={"oid": oid, "page": next_page, "task_code": task_code,
                                       "task_keyword": task_keyword})
