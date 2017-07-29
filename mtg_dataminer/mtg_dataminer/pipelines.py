# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

# See https://doc.scrapy.org/en/latest/topics/media-pipeline.html for documentation
class MtgImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url, meta={'card':item})

    def file_path(self, request, response=None, info=None):
        cur_card = request.meta['card']
        set_name = cur_card['set_name']
        image_name = cur_card['image_name']
        return '%s/%s.jpg' % (set_name, image_name)

class MtgDataminerPipeline(object):
    def process_item(self, item, spider):
        return item
