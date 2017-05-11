from scrapy.crawler import CrawlerProcess
from scrapper.scrapper.spiders.cars_spider import UrlsSpider


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(UrlsSpider)
process.start()
