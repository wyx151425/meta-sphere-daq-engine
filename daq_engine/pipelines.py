# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class DaqEnginePipeline:
    def process_item(self, item, spider):
        return item


class WeiboMongoPipeline(object):

    def __init__(self) -> None:
        super().__init__()
        self.collection = None

    def open_spider(self, spider):
        if spider.name == "weibo":
            host = spider.settings["MONGO_HOST"]
            port = spider.settings["MONGO_PORT"]
            db_name = spider.settings["MONGO_DB"]
            username = spider.settings["MONGO_USERNAME"]
            password = spider.settings["MONGO_PASSWORD"]
            client = MongoClient("mongodb://%s:%s@%s:%s/%s" % (username, password, host, str(port), db_name))
            db = client[db_name]
            self.collection = db[spider.settings["MONGO_DOC_WEIBO"]]

    def process_item(self, item, spider):
        if spider.name == "weibo":
            self.collection.insert_one(dict(item))
        return item
