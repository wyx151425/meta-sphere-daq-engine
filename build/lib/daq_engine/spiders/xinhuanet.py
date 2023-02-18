import scrapy


class XinhuanetSpider(scrapy.Spider):
    name = 'xinhuanet'
    allowed_domains = ['xinhuanet.com']
    start_urls = ['http://www.xinhuanet.com/']

    def parse(self, response):
        pass
