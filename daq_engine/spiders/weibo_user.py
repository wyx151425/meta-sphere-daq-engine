import scrapy

from ..utils import get_redis_conn


class WeiboUserSpider(scrapy.Spider):
    name = 'weibo_user'
    allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com/ajax/profile/detail?uid={}']

    redis_key = 'DAQ_TASK:WEIBO_USERS:'

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop("domain", "")
        self.task_code = kwargs.pop("task_code")
        cookie_str = get_redis_conn().get("DAQ_SPIDER:COOKIES:WEIBO")
        self.cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookie_str.split('; ')}
        self.allowed_domains = list(filter(None, domain.split(",")))
        super(WeiboUserSpider, self).__init__(*args, **kwargs)

    def make_requests_from_url(self, url):
        cookies_str = "SINAGLOBAL=7698893317343.656.1676625108281; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW4qRg9syb2K5yYvmW6_z3F5JpX5KMhUgL.Foz71Kq0eoz7S0z2dJLoIpjLxKML12-L12zLxKqLB-qL1h-LxK-LBoMLB.Bt; UOR=,,www.baidu.com; ULV=1679986583023:4:1:1:2908704636197.419.1679986583017:1677581670786; XSRF-TOKEN=9gIb8ASw11N-AxWytxYMDVaM; ALF=1683341028; SSOLoginState=1680749028; SCF=AiMEd3XcailKoXZSrB6VEBc2pjNYoSGiCaRG66DKVPJBwxD5DwPnT3SoJYoezuNbL1gdQ4OLPofGgB3Pady_gAs.; SUB=_2A25JKkG0DeRhGeRO4lQS8izMzD6IHXVqXjR8rDV8PUNbmtANLRWjkW9NUErOugbYiofoTDh5HTj1ccizdBEYT91N; WBPSESS=j1bUqD_uu3DXTXvt20EN1O1sMUDbqv3FNH3iWPBaPvGl9W44tnW4xNxyukYfeSnltGq5WvCqYsZ1zDdqc3zmu6ZXhEUuWc79St53LpJmg_8CarhS8JhP88SZVpUteAuDA0572h2dy77HyJD4cK0SFw=="
        cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies_str.split('; ')}
        return scrapy.Request(url, dont_filter=True, callback=self.parse, cookies=cookies)

    def start_requests(self):
        r = get_redis_conn()
        r_key = "DAQ_TASK:KEYWORDS:" + self.task_code
        keywords = r.lrange(r_key, 0, -1)
        for keyword in keywords:
            start_url = self.search_url.format(keyword, "1")
            yield scrapy.Request(start_url, callback=self.parse, cookies=self.cookies,
                                 meta={"task_code": self.task_code, "keyword": keyword})

    def parse(self, response, **kwargs):
        pass
