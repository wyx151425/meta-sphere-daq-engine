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
    task_code = scrapy.Field()
    task_keyword = scrapy.Field()

    mid = scrapy.Field()
    uid = scrapy.Field()
    hash_mid = scrapy.Field()
    created_at = scrapy.Field()

    text_raw = scrapy.Field()
    text = scrapy.Field()
    text_length = scrapy.Field()
    source = scrapy.Field()
    weibo_url = scrapy.Field()
    region_name = scrapy.Field()

    reposts_count = scrapy.Field()
    comments_count = scrapy.Field()
    likes_count = scrapy.Field()

    user_screen_name = scrapy.Field()


class WeiboUserItem(scrapy.Item):
    task_code = scrapy.Field()
    task_keyword = scrapy.Field()

    uid = scrapy.Field()  # 用户的ID
    created_at = scrapy.Field()  # 用户创建时间
    screen_name = scrapy.Field()  # 微博昵称
    gender = scrapy.Field()  # 性别（m男f女）
    birthday = scrapy.Field()  # 生日
    constellation = scrapy.Field()  # 星座
    province = scrapy.Field()  # 所在省份
    city = scrapy.Field()  # 所在城市
    description = scrapy.Field()  # 个人描述
    profile_url = scrapy.Field()  # 个人主页网址
    verified = scrapy.Field()  # 认证用户
    credit_level = scrapy.Field()  # 信用等级

    followers_count = scrapy.Field()  # 粉丝数量
    followers_count_str = scrapy.Field()  # 粉丝数量字符串
    follows_count = scrapy.Field()  # 关注数量
    follows_count_str = scrapy.Field()  # 关注数量字符串
    weibos_count = scrapy.Field()  # 历史微博数量
    weibos_count_str = scrapy.Field()  # 历史微博数量字符串


class WeiboCommentItem(scrapy.Item):
    task_code = scrapy.Field()
    task_keyword = scrapy.Field()

    cid = scrapy.Field()  # 评论的ID
    mid = scrapy.Field()  # 微博的ID
    uid = scrapy.Field()  # 发评论用户的ID

    text_raw = scrapy.Field()  # 评论原始文本
    text = scrapy.Field()  # 评论格式化文本
    likes_count = scrapy.Field()  # 点赞数
    source = scrapy.Field()  # 评论发布地
    created_at = scrapy.Field()  # 评论发布时间


class WeiboRepostItem(scrapy.Item):
    task_code = scrapy.Field()
    task_keyword = scrapy.Field()

    mid = scrapy.Field()  # 该转发微博的ID
    oid = scrapy.Field()  # 被转发微博的ID
    uid = scrapy.Field()
    hash_mid = scrapy.Field()
    created_at = scrapy.Field()

    text_raw = scrapy.Field()
    text = scrapy.Field()
    source = scrapy.Field()
    weibo_url = scrapy.Field()
    region_name = scrapy.Field()

    reposts_count = scrapy.Field()
    comments_count = scrapy.Field()
    likes_count = scrapy.Field()

    user_screen_name = scrapy.Field()


class WeiboLikeItem(scrapy.Item):
    task_code = scrapy.Field()
    task_keyword = scrapy.Field()

    mid = scrapy.Field()  # 微博的ID
    uid = scrapy.Field()  # 点赞用户的ID
    like = scrapy.Field()
