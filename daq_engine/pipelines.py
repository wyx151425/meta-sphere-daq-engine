# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from items import WeiboCommentItem, WeiboUserItem, WeiboRepostItem, WeiboLikeItem, WeiboItem
from utils import get_mongo_conn


class DaqEnginePipeline:
    def process_item(self, item, spider):
        return item


class WeiboMongoPipeline(object):

    def __init__(self) -> None:
        super().__init__()
        self.weibo_collection = None
        self.weibo_user_collection = None
        self.weibo_like_collection = None
        self.weibo_comment_collection = None
        self.weibo_repost_collection = None

    def open_spider(self, spider):
        mongo_conn = get_mongo_conn()
        self.weibo_collection = mongo_conn["weibo"]
        self.weibo_user_collection = mongo_conn["weibo_user"]
        self.weibo_like_collection = mongo_conn["weibo_like"]
        self.weibo_comment_collection = mongo_conn["weibo_comment"]
        self.weibo_repost_collection = mongo_conn["weibo_repost"]

    def process_item(self, item, spider):
        if type(item) == WeiboItem:
            self.weibo_collection.insert_one(dict(item))
        if type(item) == WeiboUserItem:
            self.weibo_user_collection.insert_one(dict(item))
        if type(item) == WeiboLikeItem:
            self.weibo_like_collection.insert_one(dict(item))
        if type(item) == WeiboCommentItem:
            self.weibo_comment_collection.insert_one(dict(item))
        if type(item) == WeiboRepostItem:
            self.weibo_repost_collection.insert_one(dict(item))
        return item
