# -*- coding: utf-8 -*-
import sys
import time
import random

import scrapy

sys.path.append('/home/ignisor/dev/cars_recognition/tf_cr/')
from data.models import Image


class UrlsSpider(scrapy.Spider):
    name = 'main_spider'
    allowed_domains = ['cars-data.com']
    start_urls = ['http://cars-data.com/']

    def parse(self, response):
        brands = response.css('.row.footerbrands > .a_footer::text').extract()
        urls = response.css('.row.footerbrands > .a_footer::attr(href)').extract()

        for brand, url in zip(brands[:3], urls[:3]):
            img_spider = ImagesSpider(brand)
            scrapy.Request(url, callback=img_spider.parse)
            time.sleep(5)


class ImagesSpider(scrapy.Spider):
    name = 'images_spider'
    allowed_domains = ['cars-data.com']

    def __init__(self, brand):
        super(ImagesSpider, self).__init__()
        self.brand = brand
        print('init')

    def parse(self, response):
        self.log('Scrapping: {}({})'.format(self.brand, response.url))
        images = response.css('.models > div.col-4 > a > img::attr(src)').extract()
        print('parsing')

        for img_url in images[:3]:
            # skip image if it already in DB
            try:
                Image.objects.get(pk=img_url)
                self.log('Image already exists: {}'.format(img_url))
                continue
            except Image.DoesNotExist:
                pass

            img = Image(url=img_url,
                        is_car=True,
                        is_test=random.randint(1,100) < 10)
            
            img.save()
            print('saved: ', img_url)

            self.log('New image saved: {}'.format(img_url))

            time.sleep(5)

