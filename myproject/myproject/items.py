# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyprojectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    store_elem_id = scrapy.Field()
    store_name = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    sales_unit = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    item_size = scrapy.Field()
