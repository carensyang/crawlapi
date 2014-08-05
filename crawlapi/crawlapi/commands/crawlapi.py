#encoding:utf-8
from scrapy.crawler import Crawler
import signal

from twisted.internet import reactor, threads, defer
from twisted.python import threadable
from w3lib.url import any_to_uri

from scrapy.utils.misc import load_object
from scrapy.settings import Settings
from scrapy.http import Request, Response
from scrapy.exceptions import IgnoreRequest

from scrapy.command import ScrapyCommand
from scrapy.utils.project import get_project_settings
from myscrapy.basespiders.tmall import TmallSpiderBase
from myscrapy.items import Product

import json
from twisted.web import server, resource
from twisted.web.resource import ErrorPage
from twisted.web._responses import BAD_REQUEST

crawl_queue  = []
output_queue = []

class CrawlRuntime(ScrapyCommand):

    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'crawl api'

    def _open_spider(self, spider_class):
        spider = spider_class()
        spider.set_crawler(self.crawler_instance)
        self.crawler_instance.engine.open_spider(spider, close_if_idle=False)
        self.spider = spider
        return spider

    def fetch(self, request_or_url, meta, spider=None):
        if spider == None:
            spider = self.spider
        url = any_to_uri(request_or_url)
        request = Request(url, dont_filter=True, callback=spider.parse_item)
        request.meta['source'] = meta['request']
        self.crawler.engine.crawl(request, spider)

    def run(self, args, opts):
        self.spider = None
        self.start_server()
        settings = get_project_settings()
        self.item_class = Product
        self.crawler_instance = self.crawler_process.create_crawler()
        self.crawler_instance.start()
        spider = self._open_spider(TmallSpiderBase)
        self.crawler.engine.running = True
        self.get_from_crawl_queue()
        self.crawler_process.start()

    def get_from_crawl_queue(self):
        while(len(crawl_queue)) > 0:
            crawl_item = crawl_queue.pop()
            self.fetch(crawl_item['url'], {'request' : crawl_item['request']})
        reactor.callLater(0.01, self.get_from_crawl_queue)

    def process_item(self, item, spider):
        if item['source'] != 50:
            output_queue.append(item)
        return item

    def start_server(self):
        root = resource.Resource()
        root.putChild("find_products", CrawlApi())
        reactor.listenTCP(8999, server.Site(root))

class ErrorMessage(ErrorPage):
    def render(self, request):
        request.setResponseCode(self.code)
        request.setHeader(b"content-type", b"application/json; charset=utf-8")
        interpolated = json.dumps({'error':self.code, 'message' : self.brief})
        return interpolated

class CrawlApi(resource.Resource):

    isLeaf = True

    def __init__(self):
        self.children = {}
        self.chech_crawl_result()

    def chech_crawl_result(self):
        try:
            while(len(output_queue)) > 0:
                output_item = output_queue.pop()
                dat = {}
                dat['name'] = output_item['name']
                dat['price'] = output_item['price']
                output_item['source'].write(json.dumps(dat))
                output_item['source'].finish()
            reactor.callLater(0.01, self.chech_crawl_result)
        except:
            reactor.callLater(0.01, self.chech_crawl_result)

    def crawl_timeout(self, request):
        if request.finished != True:
            request.write(ErrorMessage(100, 'Timeout', '').render(request))
            request.finish()

    def render_GET(self, request):
        try:
            request.setHeader(b"content-type", b"application/json; charset=utf-8")
            url = request.args.get('url')[0]
            crawl_queue.append({'url' : url, 'request' : request})
            reactor.callLater(5, self.crawl_timeout, request)
            return server.NOT_DONE_YET
        except:
            return ErrorMessage(200, 'Invalid args', '').render(request)

