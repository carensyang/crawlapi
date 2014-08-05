# Scrapy settings for crawlapi project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawlapi'

SPIDER_MODULES = ['crawlapi.spiders']
NEWSPIDER_MODULE = 'crawlapi.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawlapi (+http://www.yourdomain.com)'

COMMANDS_MODULE = 'crawlapi.commands'

ITEM_PIPELINES = [
    'crawlapi.commands.crawlapi.CrawlRuntime'
]
