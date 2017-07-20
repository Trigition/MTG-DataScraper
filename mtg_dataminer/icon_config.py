import BeautifulSoup as bs
import urlparse

# '$' is replaced with cost specifier, like 'g' for 'green' mana cost
# https://github.com/andrewgioia/Mana

ICON_TAG = 'i'
ICON_CLASSES = "ms ms-$ ms_cost ms_shadow"
#ICON_TEMPLATE = '<i class="ms ms-$ ms-cost ms-shadow"></i>'

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
        # Likely no name was found, return emptystring bacl
        new_icon_html = ''
   
    return new_icon_html

def get_icon_specifier(img_url):
    parsed = urlparse.urlparse(img_url)
    icon_specifier = urlparse.parse_qs(parsed.query)['name'][0]

    return icon_specifier

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
