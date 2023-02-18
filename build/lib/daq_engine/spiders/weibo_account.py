import scrapy


class WeiboAccountSpider(scrapy.Spider):
    name = 'weibo_account'
    allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com/']

    def parse(self, response):
        pass
