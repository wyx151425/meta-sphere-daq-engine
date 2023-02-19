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
    attitudes_count = scrapy.Field()  # 点赞数
    region_name = scrapy.Field()
    source = scrapy.Field()
    weibo_url = scrapy.Field()

    user = scrapy.Field()
    user_id = scrapy.Field()
    user_screen_name = scrapy.Field()
    user_profile_url = scrapy.Field()


class WeiboUserItem(scrapy.Item):
    id = scrapy.Field()
    id_str = scrapy.Field()

    screen_name = scrapy.Field()  # 网名
    gender = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()

    profile_url = scrapy.Field()  # 个人主页网址
    profile_image_url = scrapy.Field()
    avatar_large_url = scrapy.Field()
    avatar_hd_url = scrapy.Field()

    followers_count = scrapy.Field()  # 粉丝数量
    followers_count_str = scrapy.Field()
    friends_count = scrapy.Field()  # 关注数量
    friends_count_str = scrapy.Field()
    statuses_count = scrapy.Field()  # 历史微博数量
    statuses_count_str = scrapy.Field()


class WeiboCommentItem(scrapy.Item):
    pass
