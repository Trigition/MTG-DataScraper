# -*- coding: utf-8 -*-
import scrapy
import paths
from mtg_dataminer.items import Card
from mtg_dataminer.items import MTG_Card
from card_extractors import *

# Main Spider
class CardCrawlerSpider(scrapy.Spider):
    
    name = 'card_crawler'
    allowed_domains = ['gatherer.wizards.com']
    base_search_url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx/?'
    defined_ids = []

    # Define actions upon initialization of spider
    def __init__(self, *args, **kwargs):
        super(CardCrawlerSpider, self).__init__(*args, **kwargs)
        
        # Interpret Scrapy Command Line Arguments
        
        card_search = 'set=[' + make_web_safe( kwargs.get('card_set') ) + ']'
        variant_flag = kwargs.get('variants')

        if variant_flag.lower() == 'true':
            print "Scrubbing for variants"
            card_search = 'set=[' + make_web_safe('"' + kwargs.get('card_set') + '"') + ']'
            self.variants = True
            self.start_urls = [self.base_search_url + 'action=advanced&' + card_search ]
        else:
            self.variants = False
            self.start_urls = [self.base_search_url + card_search ]
        print self.start_urls

    # This default parse method is called upon the first search
    # This method merely calls our other, more specific, parse methods
    def parse(self, response):
        # Scrape each page
        card_links = self.extract_card_links(response)
        for card_link in card_links[::1]:
            new_card = MTG_Card()    
            new_card['front'] = Card()
            new_card['back'] = Card()
            
            # Remove "&part=card"
            clean_link = card_link.split('&part=')[0]
            printed_link = clean_link + "&printed=true"

            yield response.follow(printed_link, self.extract_printed_text, meta={'card':new_card})
            yield response.follow(clean_link, self.parse_card_page, meta={'card':new_card})

            # If variants are wanted, add them to request queue
            if self.variants:
                variant_links = self.extract_variant_links(response)

                for variant_link in variant_links:
                    variant_card = MTG_Card()
                    variant_card['front'] = Card()
                    variant_card['back'] = Card()
                    yield response.follow(variant_link, self.parse_card_page, meta={'card':variant_card})
        
        # Go to next page if it exists
        next_page = self.get_next_result_page(response)
        if next_page:
            # Next page exists, follow next page using parse()
            yield response.follow(next_page, self.parse)

    # This method parses the HTML page representing a physical card
    # Cards may have two faces and we must handle that appropriately
    def parse_card_page(self, response):
        
        # Get HTML Table describing card
        card_table = response.xpath(paths.CARD_HTML_TABLE)
        
        # It's possible that two cards exist in this table (double card)
        # Ensure that both get recorded
        if card_table.xpath(paths.MULTIPLE_CARD_PATH):
            
            # Multiple Cards!
            card_components = card_table.xpath(paths.MULTIPLE_CARD_CONTAINER)
 
            front_card = self.load_card(card_components[0].xpath(paths.INDIVIDUAL_MULTIPLE_CARD), response)
            back_card = self.load_card(card_components[1].xpath(paths.INDIVIDUAL_MULTIPLE_CARD), response, 'back')

            front_card['gatherer_id'] = get_gatherer_id(response)
            back_card['gatherer_id'] = get_gatherer_id(response)

            print "Double Card: %s // %s, %s" % (front_card['card_name'], back_card['card_name'], front_card['gatherer_id'])
            yield front_card
            yield back_card

        elif card_table.xpath(paths.SINGLE_CARD_PATH):
        
            # Single Card!
            new_card = self.load_card(card_table.xpath(paths.SINGLE_CARD_PATH), response)
            new_card['gatherer_id'] = get_gatherer_id(response)
            
            print "Card: %s, %s" % (new_card['card_name'], new_card['gatherer_id'])
            yield new_card
        else:
            # Error!
            print "Error parsing page:", response.url

    # This method loads a single card (for double-faced cards, this method will
    # be called twice
    def load_card(self, card_detail_table, response, side='front'):

        card_image_container = card_detail_table.xpath(paths.CARD_IMAGE_CONTAINER)
        card_detail_container = card_detail_table.xpath(paths.CARD_DETAILS_CONTAINER)
        
        # Information on the card is stored in a table
        # Each row of the table stores a div for the information 'key'
        # and another div for its 'value'
        details = extract_row_key_value_pairs(card_detail_container)

        # New card objects are instantiated before 'load_card' is called
        # this grabs the appropriate card for this page
        new_card = response.meta['card'][side]
        
        # Extract Common card attributes
        new_card['card_name'] = get_text(details['Card Name'])
        new_card['supertypes'], new_card['subtypes'] = get_super_and_sub_type(details["Types"])
        new_card['rarity'] = get_text(details['Rarity'], 'span')
        new_card['set_name'] = get_expansion(details['Expansion'])
        
        try:
            new_card['artist'] = get_text(details['Artist'], 'a')
        except IndexError:
            # Attempt to recover
            new_card['artist'] = get_text(details['Artist'])

        # Extract image of the card
        # Use custom field name
        # Due to meld cards, this selection may fail
        new_card['image_urls'] = get_image_url(card_image_container, response)
        new_card['image_name'] = new_card['set_name'] + \
                                '__' + \
                                new_card['card_name']


        # Extract optional card attributes
        try:
            new_card['oracle_text'] = get_card_textbox(details["Card Text"])
        except KeyError:
            new_card['oracle_text'] = None

        try:
            new_card['flavor_text'] = get_flavor_text(details['Flavor Text'])
        except KeyError:
            new_card['flavor_text'] = None
        
        try:
            new_card['mana_cost'] = encode_mana_cost(details['Mana Cost'])
        except KeyError:
            new_card['mana_cost'] = None

        try:
            new_card['converted_mana_cost'] = get_text(details['Converted Mana Cost'])
        except KeyError:
            new_card['converted_mana_cost'] = None

        try:
            new_card['power'], new_card['toughness'] = get_power_toughness(details['P/T'])
        except KeyError:
            new_card['power'] = None
            new_card['toughness'] = None

        try:
            new_card['loyalty'] = get_text(details['Loyalty'])
        except KeyError:
            new_card['loyalty'] = None

        try:
            new_card['collectors_number'] = get_text(details['Card Number'])
        except KeyError:
            new_card['collectors_number'] = None

        # Using MTG JSON Attempt to load set attributes
        try:
            new_card['set_code'] = set_code_lookup[new_card['set_name']]
            new_card['border_type'] = border_lookup[new_card['set_code']]
            new_card['foil'] = foil_lookup[new_card['set_code']]
            new_card['frame_type'] = card_frame_lookup[new_card['set_code']]

        except KeyError:
            print "No code for set: %s" % new_card['set_name']
            new_card['set_code'] = None


        # Finally, create field which aren't given but can be deduced
        new_card['colors'] = get_color(new_card['mana_cost'])

        return new_card

    # This method finds hyperlinks to cards on a roster page
    def extract_card_links(self, response):
        # Get divs that represent a card row
        links = []
        card_divs = response.xpath(paths.CARD_LINKS)

        # Links are relative to current page. Convert them to absolute urls before
        # returning them
        for card_div in card_divs:
            relative_link = "../" + card_div.xpath('./@href').extract()[0]
            card_url = response.urljoin( relative_link )
            links.append(card_url)

        return links

    # This method extracts the hyperlinks to any card sets that may exist
    def extract_variant_links(self, response):
        # Extract individual links to the 'same' card in other sets
        links = []
        xpath_links = response.xpath(paths.CARD_VARIANT_PATH + '//a')

        # Links are relative to current page. Convert them to absolute urls
        for link in xpath_links:
            relative_link = "../" + link.xpath('./@href').extract()[0]
            variant_url = response.urljoin( relative_link )
            links.append(variant_url)

        return links

    # This method finds the printed text of a card and extracts to current item context
    # Since this information exists on a separate page, it cannot be extracted by 'load_card'
    # it needs to be a separate callback function
    def extract_printed_text(self, response):
        front_card = response.meta['card']['front']
        back_card = response.meta['card']['back']

        card_table = response.xpath(paths.CARD_HTML_TABLE)

        if card_table.xpath(paths.MULTIPLE_CARD_PATH):

            card_components = card_table.xpath(paths.MULTIPLE_CARD_CONTAINER)

            front_text = get_card_textbox(card_components[0], '.' + paths.TEXT_BOX_PATH)
            back_text = get_card_textbox(card_components[1], '.' + paths.TEXT_BOX_PATH)

            front_card['printed_text'] = front_text
            back_card['printed_text'] = back_text
        else:
            text = get_card_textbox( response, paths.TEXT_BOX_PATH )
            front_card['printed_text'] = text
        

    # Card results are paginated, this method will return
    # the next search result page url if it exists
    def get_next_result_page(self, response):
        nav_links = response.xpath(paths.NEXT_PAGE)

        # Grab next link using the link string: ' >'
        for nav_link in nav_links:

            # Extracting text is placed in array
            if nav_link.xpath('text()').extract()[0] == u'\xa0>':
                # We need to construct the next url
                relative_url = nav_link.xpath('./@href').extract()[0]
                next_page_url = response.urljoin(relative_url)
                return next_page_url
        
        return None # No such link found
