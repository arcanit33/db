# -*- coding: utf-8 -*-
from scrapy.http.response import Response
import scrapy


class StejkaSpider(scrapy.Spider):
    name = 'stejka'
    allowed_domains = ['stejka.com']
    start_urls = ['https://stejka.com/']

    def parse(self, response: Response):
        all_images = response.xpath("//div[@class='foto']/@style[starts-with(., 'background-image: url(/')]")
        all_text = response.xpath("//*[not(self::script)][not(self::style)][string-length(normalize-space(text())) > 30]/text()")
        yield {
            'url': response.url,
            'payload': [{'type': 'text', 'data': text.get().strip()} for text in all_text] +
                       [{'type': 'image', 'data': 'https://stejka.com' + image.get()[22:len(image.get())-2]} for image in all_images]
        }
        if response.url == self.start_urls[0]:
            all_links = response.xpath(
                "//a/@href[starts-with(., '/rus/')]")
            selected_links = ['https://stejka.com' + link.get() for link in all_links][:20]
            for link in selected_links:
                yield scrapy.Request(link, self.parse)
