#!/usr/bin/env python

CARD_IMAGE_TOKEN_CLASS = 'card-small-icon'
CARD_TEXT_BOX_CLASS = 'card-text'

### PATHS
### If Gatherer changes how it stores card details, the paths
### can be edited here

# Path for card links on a search result page
CARD_LINKS = '//tr/td/div/span[@class="cardTitle"]/a'

# Path to the table which holds information on a card
CARD_HTML_TABLE = '//table[@class="cardComponentTable"]'

# Path to card variants
# Note that this path is for the 'results' page
CARD_VARIANT_PATH = '//div[contains(@class, "otherSetSection")]/div[@class="rightCol"]'

# Describe the difference in HTML between a page which describes
# a single card vs. a double card
MULTIPLE_CARD_PATH = './/table[@class="cardDetails cardComponent"]'
MULTIPLE_CARD_CONTAINER = './/td[@class="cardComponentContainer"]'
INDIVIDUAL_MULTIPLE_CARD = './div/table[@class="cardDetails cardComponent"]'

SINGLE_CARD_PATH = '//table[@class="cardDetails"]'

# Describe where the card image and card details are located
CARD_IMAGE_CONTAINER = './/td[contains(@class,"leftCol")]'
CARD_DETAILS_CONTAINER = './/td[contains(@class,"rightCol")]'

### ---END PATHS--- ###

### CARD DETAIL PATHS

# Card details are in rows
ROW_PATH = './/div[contains(@class, "row")]'

# Fields are separated by a "label" div and a "value" div
KEY_PATH = './div[@class="label"]'
VALUE_PATH = './div[@class="value"]'

# Card Text Box
TEXT_BOX_PATH = '//div[@class="cardtextbox"]'
FLAVOR_TEXT_BOX = './div[@class="flavortextbox"]'
### --END CARD DETAIL PATHS

### NEXT PAGE PATH
NEXT_PAGE = '//div[@class="paging"]/a'
### --END NEXT PAGE PATH
