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
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_profile_url = scrapy.Field()
    user_avatar_url = scrapy.Field()
    publish_time = scrapy.Field()
    publish_platform = scrapy.Field()

    origin_weibo_id = scrapy.Field()
    weibo_url = scrapy.Field()
    weibo_content = scrapy.Field()

    repost_total = scrapy.Field()
    comment_total = scrapy.Field()
    like_total = scrapy.Field()


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

