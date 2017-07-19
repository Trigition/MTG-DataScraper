import re
import BeautifulSoup as bs
import paths
from urllib import quote

# Makes a string http safe
def make_web_safe(string):
    return quote(string)

# This method constructs a dictionary between a div-class and its HTML content
def extract_row_key_value_pairs(response):
    rows = response.xpath(paths.ROW_PATH)
    details = {}

    for row in rows:
        key = row.xpath(paths.KEY_PATH)
        value = row.xpath(paths.VALUE_PATH)

        key_str = get_text(key)
        if len(key_str) > 0:
            key_str = key_str.strip(':')
            details[key_str] = value
        else:
            # Attempt recovery
            key_str = get_text(key, 'b')
            if key_str != '':
                key_str = key_str.strip(':')
                details[key_str] = value

    return details

# This method encodes mana and action symbols according to paths.py
def encode_mana_cost(xml_path):
    images = xml_path.xpath('./img')
    mana_costs = []

    for image in images:
        soup = bs.BeautifulSoup(image.extract())
        soup.img['src'] = get_new_image_path(soup.img)
        del soup.img['align']
        mana_costs.append(str(soup.img))

    return ''.join(mana_costs)

# This method gets the Gatherer ID from the URL
def get_gatherer_id(response):
    regex = r"(\d+)"
    groups_found = re.finditer(regex, response.url)
    matches = [match.group(match_num) for match_num, match in enumerate(groups_found)]
    return matches[0]

# This method gets the power toughness field
def get_power_toughness(xml_path):
    pt_string = get_text(xml_path)
    # Split string
    power, toughness = pt_string.split(' / ')
    power = power.strip()
    toughness = toughness.strip()
    return (power, toughness)

# This method gets the supertype and subtype if it exists
def get_super_and_sub_type(xml_path):
    types = get_text(xml_path).split(u' \u2014 ')
    if len(types) > 1:
        subtype = types[1].strip()
    else:
        subtype = None
    supertype = types[0].strip()
    return (supertype, subtype)

# Get Flavor Text. Line breaks are described as div tags,
# this method extracts the fields and preserves the line
# breaks via newlines
def get_flavor_text(xml_path):
    
    text_fields = xml_path.xpath(paths.FLAVOR_TEXT_BOX)
    text_strings = [get_text(field) for field in text_fields]

    return '\n'.join(text_strings)

# This method extracts the HTML from card text. Any interior images
# are encoded based upon settings in paths.py
def get_card_textbox(xml_path, path='./div[@class="cardtextbox"]'):
    # Text boxes can be a mix of images and text breaks
    # Ensure all get preserved
    text_lines = []
    text_boxes = xml_path.xpath(path)
    
    for text_box in text_boxes:
        soup = bs.BeautifulSoup(text_box.extract())
        format_html_tree(soup)
        text_lines.append( str(soup) )
   
    return ''.join(text_lines)

# This method gets the inner HTML of the set row
# Note images are encoded via paths.py
def get_expansion(xml_path):
    links = xml_path.xpath('./div/a')
    # First link contains image of set
    # Second link contains set name
    #image = bs.BeautifulSoup( links[0].xpath('./img').extract() )
    text = links[1].xpath('text()').extract()[0]

    #image['src'] = get_new_image_path(image)
    #del image['align']
    #del image['style']
    return text #str(image) + text

# This method extracts any text field within the path (and 
# extra specified interior tags)
def get_text(xml_path, *nested_tags):
    path = './/'
    for tag in nested_tags:
        path += tag + '/'
    return xml_path.xpath(path + 'text()').extract()[0].strip()

# This method gets the image path
def get_image_url(image_xpath, response):
    relative_url = image_xpath.xpath('./div/img/@src').extract()
    
    if len(relative_url) is 0:
        # Attempt to recover
        relative_url = image_xpath.xpath('./img/@src').extract()
    
    image_url = response.urljoin(relative_url[0])
    return [image_url]

def get_filename(card_name, set_name):
    filename = card_name.replace(' ', '_') + '__' + set_name.replace(' ', '_')
    return filename

# This method encodes image symbol sources
def get_new_image_path(image_soup):
    alt_text = image_soup['alt']
    alt_text.replace(' ', '-').lower()
    return alt_text + ".jpg"

# This method parses the HTML Tree to find images, specifically
# those inside of card-box-text divs and encode them based upon
# settings in paths.py
def format_html_tree(soup, depth=0):
    if isinstance(soup, bs.NavigableString):
        return

    # Replace image text
    if soup.name == 'img':
        soup['src'] = get_new_image_path(soup)
        soup['class'] = paths.CARD_IMAGE_TOKEN_CLASS
        del soup['align']
        return
    if soup.name == 'div':
        # Remove styling
        del soup['style']
        soup['class'] = paths.CARD_TEXT_BOX_CLASS
    
    for content in soup.contents:
        format_html_tree(content, depth+1)
