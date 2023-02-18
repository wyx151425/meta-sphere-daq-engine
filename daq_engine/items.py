# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DaqEngineItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WeiboItem(scrapy.Item):
    mid = scrapy.Field()
    mblog_id = scrapy.Field()
    created_at = scrapy.Field()
    text_raw = scrapy.Field()
    text = scrapy.Field()
    text_length = scrapy.Field()
    reposts_count = scrapy.Field()
    comments_count = scrapy.Field()
    attitudes_count = scrapy.Field()
    region_name = scrapy.Field()
    source = scrapy.Field()
    weibo_url = scrapy.Field()

    user = scrapy.Field()
    user_id = scrapy.Field()
    user_screen_name = scrapy.Field()
    user_profile_url = scrapy.Field()


class WeiboUserItem(scrapy.Item):
    origin_id = scrapy.Field()
    origin_id_str = scrapy.Field()

    screen_name = scrapy.Field()
    avatar_url = scrapy.Field()
    profile_url = scrapy.Field()
    gender = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    user_type = scrapy.Field()

    followers_count = scrapy.Field()
    followers_count_str = scrapy.Field()
    friends_count = scrapy.Field()
    friends_count_str = scrapy.Field()

class WeiboCommentItem(scrapy.Item):
    pass

