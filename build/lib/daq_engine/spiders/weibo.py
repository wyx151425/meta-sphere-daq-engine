import scrapy

from ..items import WeiboItem

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com/']
    # start_urls = ['https://s.weibo.com/weibo?q=%E4%BD%A9%E6%B4%9B%E8%A5%BF&page=1']

    cookies = {
        'SINAGLOBAL': '5224461449577.875.1652078588225',
        'UOR': ', , www.baidu.com',
        'PC_TOKEN': 'd80d1e1a8b',
        'SCF': 'AvXwBy3vK2EWYi1uAMAWXc3tulfOQFHteO8JexIO - 8GAFM9lkWqey9ArjxG9TxNzCECdY2d_EjS4TQlwmz1rwNM.',
        'SUB': '_2A25OWi0GDeRhGeRO4lQS8izMzD6IHXVtLhnOrDV8PUJbmtAKLVnSkW9NUErOupMWfWQsPS5G7xRVRM1KBIzjhJ5W',
        'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WW4qRg9syb2K5yYvmW6_z3F5JpX5K - hUgL.Foz71Kq0eoz7S0z2dJLoIpjLxKML12 - L12zLxKqLB - qL1h - LxK - LBoMLB.Bt',
        'ALF': '1698662301',
        'SSOLoginState': '1667128662',
        '_s_tentry': 'weibo.com',
        'Apache': '7586928003044.655.1667128674339',
        'ULV': '1667128674358:12: 4:1: 7586928003044.655.1667128674339: 1666783108572'
    }

    # def start_requests(self):
    #     yield scrapy.Request(self.start_urls[0], callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        yield scrapy.Request(self.start_urls[0], callback=self.parse, cookies=self.cookies)

        # card_wrap_list = response.xpath('//div[@class="card-wrap"]')
        #
        # items = []
        #
        # index = 0
        # for card_wrap_item in card_wrap_list:
        #
        #     item = WeiboItem()
        #
        #     item["author_name"] = card_wrap_item.xpath('.//div[@class="info"]/div[2]/a/text()').extract_first()
        #     publish_time = card_wrap_item.xpath('.//div[@class="from"]/a[1]/text()').extract_first()
        #     if item is not None:
        #         publish_time = publish_time.strip()
        #     item["publish_time"] = publish_time
        #     item["publish_platform"] = card_wrap_item.xpath('.//div[@class="from"]/a[2]/text()').extract_first()
        #
        #     p_text_tags = card_wrap_item.xpath('.//p[last()]/text()')
        #     content = ""
        #     for p_text_tag in p_text_tags:
        #         text = p_text_tag.get().strip()
        #         content += text
        #     item["weibo_text"] = content
        #     print(item)
        #
        #     items.append(item)



