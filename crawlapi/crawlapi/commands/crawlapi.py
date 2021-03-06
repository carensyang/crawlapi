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
from myscrapy.basespiders.jingdong import JingdongSpiderBase
from myscrapy.items import Product

import json
import urlparse
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

    def _open_spider(self, spider_class, site_id):
        spider = spider_class()
        spider.set_crawler(self.crawler_instances[site_id])
        self.crawler_instances[site_id].engine.open_spider(spider, close_if_idle=False)
        self.spiders[site_id] = spider
        self.spiders_class[site_id] = spider_class
        return spider

    def fetch(self, request_or_url, meta, spider=None):
        site_id = meta['crawl_site_id']
        spider  = self.spiders.get(site_id)
        url = any_to_uri(request_or_url)
        request = Request(url, dont_filter=True, callback=self.spiders[site_id].parse_item)
        request.meta['source'] = meta['request']
        self.crawler_instances[site_id].engine.crawl(request, spider)

    def run(self, args, opts):
        port = int(args[0])
        site_id = int(args[1])
        self.spiders = {}
        self.spiders_class = {}
        self.crawler_instances = {}
        self.start_server(port)
        self.item_class = Product
        self.crawler_instances[site_id] = self.crawler_process.create_crawler()
        self.crawler_instances[site_id].start()
        if site_id == 4:
            self._open_spider(TmallSpiderBase, 4)
        elif site_id == 2:
            self._open_spider(JingdongSpiderBase, 2)
        self.crawler.engine.running = True
        self.get_from_crawl_queue()
        self.crawler_process.start()

    def get_from_crawl_queue(self):
        while(len(crawl_queue)) > 0:
            crawl_item = crawl_queue.pop()
            self.fetch(crawl_item['url'], {'request' : crawl_item['request'], 'crawl_site_id' : crawl_item['crawl_site_id']})
        reactor.callLater(0.01, self.get_from_crawl_queue)

    def process_item(self, item, spider):
        output_queue.append(item)
        return item

    def start_server(self, port):
        root = resource.Resource()
        root.putChild("find_products", CrawlApi())
        reactor.listenTCP(port, server.Site(root))

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
        self.chech_output()
        self.fields = ['name', 'price', 'image']

    def get_fields_val(self, item):
        dat = {}
        for field in self.fields:
            if item.has_key(field):
                dat[field] = item[field]
            else:
                dat[field] = None
        return dat

    def chech_output(self):
        try:
            while(len(output_queue)) > 0:
                output_item = output_queue.pop()
                dat = self.get_fields_val(output_item)
                output_item['source'].write(json.dumps(dat))
                output_item['source'].finish()
            reactor.callLater(0.01, self.chech_output)
        except:
            reactor.callLater(0.01, self.chech_output)

    def crawl_timeout(self, request):
        try:
            if request.finished != True:
                request.write(ErrorMessage(100, 'Timeout', '').render(request))
                request.finish()
        except:
            pass

    def url_format(self, url):
        url_obj = urlparse.urlparse(url)
        url_domain = url_obj.netloc
        if url_domain == 'detail.tmall.com':
            site_id = 4
            query = dict(urlparse.parse_qsl(url_obj.query))
            if query.has_key('id'):
                id = query['id']
                url = 'http://detail.tmall.com/item.htm?id=%s&tbpm=3' % id
                return (site_id, url)
            else:
                return (False, url)
        elif url_domain == 'item.jd.com':
            site_id = 2
            return (site_id, url)

        return (False, url)

    def render_GET(self, request):
        try:
            request.setHeader(b"content-type", b"application/json; charset=utf-8")
            url = request.args.get('url')[0]
            site_id, url = self.url_format(url)
            if site_id == False:
                return ErrorMessage(200, 'Invalid url', '').render(request)
            crawl_queue.append({'url' : url, 'request' : request, 'crawl_site_id' : site_id})
            reactor.callLater(5, self.crawl_timeout, request)
            return server.NOT_DONE_YET
        except:
            return ErrorMessage(200, 'Invalid args', '').render(request)

