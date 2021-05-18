# -*- coding: utf-8 -*-
from scrapy.http.response import Response
import scrapy


class MebliSpider(scrapy.Spider):
    name = 'mebli'
    allowed_domains = ['mebli-lviv.com.ua']
    start_urls = ['https://mebli-lviv.com.ua/ua/chairs/']

    def parse(self, response: Response):
        products = response.xpath("//div[contains(@class, 'product-block')]")[:19]
        for product in products:
            yield {
                'description': product.xpath(".//img[@class='img-responsive']/@title").get(),
                'price': product.xpath(".//span[@class='special-price']/text()").get(),
                'img': product.xpath(".//img[@class='img-responsive']/@src").get()
            }
