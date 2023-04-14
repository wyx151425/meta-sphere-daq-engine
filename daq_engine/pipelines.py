# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from items import WeiboCommentItem, WeiboUserItem
from utils import get_mongo_conn


class DaqEnginePipeline:
    def process_item(self, item, spider):
        return item


class WeiboMongoPipeline(object):

    def __init__(self) -> None:
        super().__init__()
        self.weibo_collection = None

    def open_spider(self, spider):
        mongo_conn = get_mongo_conn()
        self.weibo_collection = mongo_conn[spider.name]

    def process_item(self, item, spider):
        if spider.name == "weibo":
            item["user"] = dict(item["user"])
            self.weibo_collection.insert_one(dict(item))

        if type(item) == WeiboUserItem:
        # if spider.name == "weibo_comment":
            print(item)

        return item
