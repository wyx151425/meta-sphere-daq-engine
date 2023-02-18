import scrapy


class ThepaperSpider(scrapy.Spider):
    name = 'thepaper'
    allowed_domains = ['thepaper.cn']
    start_urls = ['https://www.thepaper.cn/']

    def parse(self, response):
        pass
