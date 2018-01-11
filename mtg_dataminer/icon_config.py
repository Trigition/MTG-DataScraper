import bs4 as bs
from urllib import parse

# '$' is replaced with cost specifier, like 'g' for 'green' mana cost
# https://github.com/andrewgioia/Mana

ICON_TAG = 'i'
ICON_CLASSES = "ms ms-$ ms_cost ms_shadow"
#ICON_TEMPLATE = '<i class="ms ms-$ ms-cost ms-shadow"></i>'

def get_delimited_cost(icon_path):
    soup = bs.BeautifulSoup(icon_path.extract())
    img_url = soup.img['src']

    # Delimit Cost
    cost_id = get_icon_specifier(img_url)
    return '{' + cost_id + '}'

def get_icon(icon_path):
    return convert_icon(icon_path.extract())

def convert_icon(img_string):
    soup = bs.BeautifulSoup(img_string)
    
    # Extract name field from image handler request url
    img_url = soup.img['src']
    icon_name = get_icon_specifier(img_url)
    
    try:
        # Sanitize name
        icon_name = icon_name.strip().lower()
        new_icon_html = construct_icon_string(icon_name)
    except AttributeError:
        # Likely no name was found, return emptystring back
        new_icon_html = ''
   
    return new_icon_html

def get_icon_specifier(img_url):
    parsed = parse.urlparse(img_url)
    icon_specifier = parse.parse_qs(parsed.query)['name'][0]

    # We might need to delimit hybrid costs with '/' but not
    # Phyrexian costs
    # We also need to preserve multiple digit converted costs
    if len(icon_specifier) > 1 and 'p' not in icon_specifier.lower() and not icon_specifier.isdigit():
        icon_specifier = '/'.join( list(icon_specifier) )

    return icon_specifier.lower()

def construct_icon_string(icon_specifier):

    icon_class = construct_icon_class(icon_specifier)
    icon_string = construct_tag(ICON_TAG, icon_class)

    return icon_string

def construct_tag(tag_class, class_string):
    start_tag = '<' + ICON_TAG
    end_tag = '</' + ICON_TAG + '>'

    tag = start_tag + ' class="' + class_string + '">' + end_tag

    return tag

def construct_icon_class(icon_specifier):
    return ICON_CLASSES.replace('$', icon_specifier)
