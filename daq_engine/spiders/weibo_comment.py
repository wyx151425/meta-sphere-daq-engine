import scrapy


class WeiboCommentSpider(scrapy.Spider):
    name = 'weibo_comment'
    allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com/']

    def parse(self, response):
        pass
