# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# This Item represents a 'Physical' card, which may contain multiple cards
class MTG_Card(scrapy.Item):

    # Define physical MTG Card, a maximum of 2 'cards' may exist per MTG Card
    front_card_name = scrapy.Field()
    back_card_name = scrapy.Field()
    gatherer_id = scrapy.Field()

# This Item represents a Card. In such it has a name, type, image, cost, etc
class Card(scrapy.Item):

    # Define the fields for a MTG "card"
    gatherer_id = scrapy.Field()
    name = scrapy.Field()
    mana_cost = scrapy.Field() # <- Determine how to encode
    converted_mana_cost = scrapy.Field() # <- will be determined by encoding
    supertypes = scrapy.Field()
    subtypes = scrapy.Field()
    power = scrapy.Field()
    toughness = scrapy.Field()
    oracle_text = scrapy.Field()
    printed_text = scrapy.Field()
    rarity = scrapy.Field()
    set = scrapy.Field()
    artist = scrapy.Field()
    flavor_text = scrapy.Field()
    collectors_number = scrapy.Field()
    loyalty = scrapy.Field()

    # Define Images
    images = scrapy.Field()
    image_urls = scrapy.Field()
    image_name = scrapy.Field()

    #def __repr__(self):
    #    return repr(None)
