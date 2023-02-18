import json

import scrapy

from ..items import WeiboItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    search_url = 'https://s.weibo.com/weibo?q={}&page={}'
    prefix_url = 'https://s.weibo.com/'

    cookies = {'login_sid_t': '8f8249df350597d962ed1b47f613e4ff',
               'cross_origin_proto': 'SSL',
               '_s_tentry': 'passport.weibo.com',
               'Apache': '7698893317343.656.1676625108281',
               'SINAGLOBAL': '7698893317343.656.1676625108281',
               'ULV': '1676625108285:1: 1:1: 7698893317343.656.1676625108281:',
               'UOR': ', , login.sina.com.cn',
               'PC_TOKEN': '405ce6a853',
               'WBtopGlobal_register_version': '2023021720',
               'SCF': 'AiMEd3XcailKoXZSrB6VEBc2pjNYoSGiCaRG66DKVPJBP3guWpEQd6hFvC2FYw9bEFn4yfs1yuh_o5nB0F2OHYE.',
               'SUB': '_2A25O6woyDeRhGeRO4lQS8izMzD6IHXVtgXz6rDV8PUNbmtAGLWvVkW9NUErOugmeEeM1vUtDrk29phX2IFqXnfcq',
               'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WW4qRg9syb2K5yYvmW6_z3F5JpX5KzhUgL.Foz71Kq0eoz7S0z2dJLoIpjLxKML12 - L12zLxKqLB - qL1h - LxK - LBoMLB.Bt',
               'ALF': '1708174818',
               'SSOLoginState': '1676638818'
               }

    def start_requests(self):
        start_url = self.search_url.format('联想小新', '1')
        yield scrapy.Request(start_url, callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        card_tags = response.xpath('//div[@class="card"]')

        weibo_items = []

        for card_tag in card_tags:
            weibo_item = WeiboItem()

            # 避开热门文章Card
            weibo_url_tag = card_tag.xpath('.//div[@class="from"]//a/@href')
            if 0 == len(weibo_url_tag):
                continue

            # 获取微博URL
            weibo_url = "https:" + card_tag.xpath('.//div[@class="from"]//a/@href').extract_first().split('?refer_flag')[0]
            uw_ids = weibo_url.split('https://weibo.com/')[-1].split('/')

            weibo_item["origin_weibo_id"] = uw_ids[-1]
            weibo_item["weibo_url"] = weibo_url

            weibo_item["origin_user_id"] = uw_ids[0]
            user_profile_url = "https://weibo.com/u/" + uw_ids[0]
            weibo_item["user_profile_url"] = user_profile_url

            # 提取微博动作部分
            act_tags = card_tag.xpath('.//div[@class="card-act"]/ul/li/a')
            weibo_item["repost_total"] = isActEmpty(act_tags[0].xpath('./text()')[-1].get(), "转发")
            weibo_item["comment_total"] = isActEmpty(act_tags[1].xpath('./text()')[-1].get(), "评论")
            weibo_item["like_total"] = isActEmpty(act_tags[2].xpath('./button/span')[-1].xpath('./text()').get(), "赞")



            # 解析微博详细内容
            new_weibo_url = "https://weibo.com/ajax/statuses/show?id={}".format(weibo_item["origin_weibo_id"])
            yield scrapy.Request(new_weibo_url, callback=self.parse_weibo_detail, cookies=self.cookies, meta={"weibo_item": weibo_item})
            # 解析微博所属用户详细信息
            yield scrapy.Request(user_profile_url, callback=self.parse_weibo_detail, cookies=self.cookies, meta={"weibo_item": weibo_item})

            print(weibo_item)
            weibo_items.append(weibo_item)

        # 检索下一页
        # next_page_tag = response.xpath('//div[@class="m-page"]//a[@class="next"]')
        # if 0 != len(next_page_tag):
        #     next_url = self.prefix_url + next_page_tag[0].xpath('./@href').extract_first()
        #     yield scrapy.Request(next_url, callback=self.parse, cookies=self.cookies)

    def parse_weibo_detail(self, response):
        weibo_item = response.meta['weibo_item']

        weibo_obj = json.loads(response.text)

        weibo_item["mid"] = weibo_obj["mid"]
        weibo_item["mblog_id"] = weibo_obj["mblogid"]
        weibo_item["created_at"] = weibo_obj["created_at"]
        weibo_item["text_raw"] = weibo_obj["text_raw"]
        weibo_item["text"] = weibo_obj["text"]
        weibo_item["text_length"] = weibo_obj["text_length"]
        weibo_item["reposts_count"] = weibo_obj["reposts_count"]
        weibo_item["comments_count"] = weibo_obj["comments_count"]
        weibo_item["attitudes_count"] = weibo_obj["attitudes_count"]
        weibo_item["region_name"] = weibo_obj["region_name"].split(" ")[-1]
        weibo_item["source"] = weibo_obj["source"]


def isActEmpty(target, actName):
    if target is not None:
        target = target.strip()
        if target != actName:
            return target
        else:
            return "0"
    else:
        return "0"

        # print(item)
        #
        # content_tag = card_tag.xpath('.//div[@class="content"]')
        #
        #
        # auther_tag = card_tag.xpath('.//div[@class="info"]/div[2]/a')
        #
        # item["author_name"] = auther_tag.xpath('./text()').extract_first()
        # # item["author_website"] = auther_tag.xpath('./@href').extract_first()
        # publish_time = card_tag.xpath('.//div[@class="from"]/a[1]/text()').extract_first()
        # if item is not None:
        #     publish_time = publish_time.strip()
        # item["publish_time"] = publish_time
        # item["publish_platform"] = "新浪微博"
        # # card_wrap_item.xpath('.//div[@class="from"]/a[2]/text()').extract_first()
        #
        # p_text_tags = card_tag.xpath('.//p[last()]/text()')
        # content = ""
        # for p_text_tag in p_text_tags:
        #     text = p_text_tag.get().strip()
        #     content += text
        # item["weibo_content"] = content
