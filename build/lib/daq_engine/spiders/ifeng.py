import scrapy


class IfengSpider(scrapy.Spider):
    name = 'ifeng'
    allowed_domains = ['ifeng.com']
    start_urls = ['https://www.ifeng.com/']

    def parse(self, response):
        while True:
            print("ifeng")
