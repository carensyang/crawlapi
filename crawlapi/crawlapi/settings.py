# encoding: utf-8

from myscrapy.settings import *

BOT_NAME = 'crawlapi'

SPIDER_MODULES = ['crawlapi.spiders']
NEWSPIDER_MODULE = 'crawlapi.spiders'

LOG_LEVEL = 'DEBUG'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawlapi (+http://www.yourdomain.com)'

COMMANDS_MODULE = 'crawlapi.commands'

ITEM_PIPELINES = [
    'crawlapi.commands.crawlapi.CrawlRuntime'
]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None,
    'myscrapy.middlewares.ProxyMiddleware': 750,
    # 'myscrapy.middlewares.ProxyScoreMiddleware': 900,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'myscrapy.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware' : None,
    'myscrapy.middlewares.DelayedRetryMiddleware' : 500,
    'myscrapy.middlewares.TmallRetryMiddleware': 609,
    'myscrapy.middlewares.JingdongRetryMiddleware': 610,
    'myscrapy.middlewares.TmallMiddleware': 611,
    'myscrapy.middlewares.AmazonMiddleware': 612,
    'myscrapy.middlewares.YihaodianCookieMiddleware': 613,
    'myscrapy.middlewares.YihaodianProductUrlMiddleware': 614,
    #'myscrapy.middlewares.AmazonRetryMiddleware': 615,
    'myscrapy.middlewares.ConvertUtf8Middleware': 200,
}

SPIDER_MIDDLEWARES = {
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,
    'myscrapy.middlewares.RefererMiddleware': 700,
}

CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_ITEMS = 100

DOWNLOAD_TIMEOUT = 15

DNSCACHE_ENABLED = True

DOWNLOAD_DELAY = 0.1

RANDOMIZE_DOWNLOAD_DELAY = False

RETRY_TIMES = 5

COOKIES_ENABLED = True

RETRY_HTTP_CODES = [301, 303, 500, 501, 502, 503, 504, 400, 408, 401, 402, 403, 405, 406, 407, 409, 499, 599, 404]

REPORT_PROXY_STATUS = True

ENABLE_PROXY = False
