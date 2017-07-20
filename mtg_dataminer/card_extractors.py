# -*- coding: utf-8 -*-
import re
import BeautifulSoup as bs
import paths
import icon_config
import urllib

# Makes a string http safe
def make_web_safe(string):
    return urllib.quote_plus(string)

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
        mana_cost = icon_config.get_icon(image)
        mana_costs.append(mana_cost)

    return ''.join(mana_costs).strip()

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
    text = links[1].xpath('text()').extract()[0]

    return text

def get_color(mana_cost):
    if mana_cost is None or mana_cost == '':
        return ''
    
    soup = bs.BeautifulSoup(mana_cost)

    colors = set()
    mana_costs = soup.findAll('i')
    
    # For each cost icon look at the ms-$ specifier
    # See icon_config.py
    for cost in mana_costs:
        element_class = cost['class']
        cost_str = element_class.split(' ')[1] # SEE icon_config.py
        
        specifier = cost_str[3:].strip() # Cut off 'ms-'

        if 'w' in specifier:
            colors.add('w')
        if 'u' in specifier:
            colors.add('u')
        if 'b' in specifier:
            colors.add('b')
        if 'r' in specifier:
            colors.add('r')
        if 'g' in specifier:
            colors.add('g')

    return ''.join(colors)

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

# This method parses the HTML Tree to find images, specifically
# those inside of card-box-text divs and encode them based upon
# settings in paths.py
def format_html_tree(soup, depth=0):
    if isinstance(soup, bs.NavigableString):
        return

    # Replace image text
    #if soup.name == 'img':
    #    soup['src'] = get_new_image_path(soup)
    #    soup['class'] = paths.CARD_IMAGE_TOKEN_CLASS
    #    del soup['align']
    #    return
    #if soup.name == 'div':
    #    # Remove styling
    #    del soup['style']
    #    soup['class'] = paths.CARD_TEXT_BOX_CLASS
    
    if soup.name == 'img':
        # Replace with appropriate tag
        soup.name = icon_config.ICON_TAG

        # Replace html class
        img_url = soup['src']
        icon_specifier = icon_config.get_icon_specifier(img_url)
        soup['class'] = icon_config.construct_icon_class(icon_specifier)

        # Delete unnecessary attributes
        del soup['style']
        del soup['src']
        del soup['alt']
        del soup['align']

    if soup.name == 'div':
        # Replace class
        soup['class'] = paths.CARD_TEXT_BOX_CLASS
        # Delete unnecessary stylings
        del soup['style']

    for content in soup.contents:
        format_html_tree(content, depth+1)

set_code_lookup = {
    u"Anthologies" : "ATH",
    u"Clash Pack" : "CPK",
    u"Two-Headed Giant Tournament" : "p2HG",
    u"Guildpact" : "GPT",
    u"The Dark" : "DRK",
    u"Betrayers of Kamigawa" : "BOK",
    u"Zendikar Expeditions" : "EXP",
    u"Dark Ascension" : "DKA",
    u"Worlds" : "pWOR",
    u"Wizards of the Coast Online Store" : "pWOS",
    u"From the Vault: Dragons" : "DRB",
    u"Homelands" : "HML",
    u"Modern Event Deck 2014" : "MD1",
    u"Journey into Nyx" : "JOU",
    u"Aether Revolt" : "AER",
    u"Magic Game Day" : "pMGD",
    u"Antiquities" : "ATQ",
    u"Prerelease Events" : "pPRE",
    u"Weatherlight" : "WTH",
    u"Stronghold" : "STH",
    u"Pro Tour" : "pPRO",
    u"Eighth Edition" : "8ED",
    u"Release Events" : "pREL",
    u"Magic Player Rewards" : "pMPR",
    u"Vanguard" : "VAN",
    u"Limited Edition Alpha" : "LEA",
    u"Champs and States" : "pCMP",
    u"Portal" : "POR",
    u"Theros" : "THS",
    u"Alliances" : "ALL",
    u"Chronicles" : "CHR",
    u"Tempest Remastered" : "TPR",
    u"Mirrodin" : "MRD",
    u"Battle for Zendikar" : "BFZ",
    u"Born of the Gods" : "BNG",
    u"Arena League" : "pARL",
    u"Gateway" : "pGTW",
    u"Dragon's Maze" : "DGM",
    u"Rivals Quick Start Set" : "RQS",
    u"Welcome Deck 2017" : "W17",
    u"Welcome Deck 2016" : "W16",
    u"Visions" : "VIS",
    u"Apocalypse" : "APC",
    u"Celebration" : "pCEL",
    u"Shards of Alara" : "ALA",
    u"Dragons of Tarkir" : "DTK",
    u"Premium Deck Series: Slivers" : "H09",
    u"Prophecy" : "PCY",
    u"Eternal Masters" : "EMA",
    u"Wizards Play Network" : "pWPN",
    u"Mercadian Masques" : "MMQ",
    u"World Magic Cup Qualifiers" : "pWCQ",
    u'Time Spiral "Timeshifted"' : "TSB",
    u"Dragon Con" : "pDRC",
    u"Commander Anthology" : "CMA",
    u"Judge Gift Program" : "pJGP",
    u"Revised Edition" : "3ED",
    u"Planechase Anthology" : "PCA",
    u"Time Spiral" : "TSP",
    u"Collector's Edition" : "CED",
    u"Portal Three Kingdoms" : "PTK",
    u"Judgment" : "JUD",
    u"Unglued" : "UGL",
    u"Duel Decks: Jace vs. Chandra" : "DD2",
    u"Scourge" : "SCG",
    u"Rise of the Eldrazi" : "ROE",
    u"International Collector's Edition" : "CEI",
    u"Tenth Edition" : "10E",
    u"Legend Membership" : "pLGM",
    u"Duel Decks Anthology, Garruk vs. Liliana" : "DD3_GVL",
    u"Masterpiece Series: Amonkhet Invocations" : "MPS_AKH",
    u"Return to Ravnica" : "RTR",
    u"Magic 2015 Core Set" : "M15",
    u"Media Inserts" : "pMEI",
    u"Darksteel" : "DST",
    u"Mirage" : "MIR",
    u"Coldsnap" : "CSP",
    u"15th Anniversary" : "p15A",
    u"Duel Decks: Mind vs. Might" : "DDS",
    u"Duel Decks: Nissa vs. Ob Nixilis" : "DDR",
    u"Duel Decks: Blessed vs. Cursed" : "DDQ",
    u"Duel Decks: Zendikar vs. Eldrazi" : "DDP",
    u"Duel Decks: Sorin vs. Tibalt" : "DDK",
    u"Duel Decks: Izzet vs. Golgari" : "DDJ",
    u"Duel Decks: Venser vs. Koth" : "DDI",
    u"Duel Decks: Ajani vs. Nicol Bolas" : "DDH",
    u"Duel Decks: Elspeth vs. Kiora" : "DDO",
    u"Duel Decks: Speed vs. Cunning" : "DDN",
    u"Duel Decks: Jace vs. Vraska" : "DDM",
    u"Duel Decks: Heroes vs. Monsters" : "DDL",
    u"Duel Decks: Divine vs. Demonic" : "DDC",
    u"Coldsnap Theme Decks" : "CST",
    u"Duel Decks: Knights vs. Dragons" : "DDG",
    u"Duel Decks: Elspeth vs. Tezzeret" : "DDF",
    u"Duel Decks: Phyrexia vs. the Coalition" : "DDE",
    u"Duel Decks: Garruk vs. Liliana" : "DDD",
    u"Duel Decks Anthology, Elves vs. Goblins" : "DD3_EVG",
    u"Duel Decks Anthology, Divine vs. Demonic" : "DD3_DVD",
    u"Planechase 2012 Edition" : "PC2",
    u"Morningtide" : "MOR",
    u"Invasion" : "INV",
    u"Friday Night Magic" : "pFNM",
    u"Avacyn Restored" : "AVR",
    u"Battle Royale Box Set" : "BRB",
    u"Beatdown Box Set" : "BTD",
    u"Masterpiece Series: Kaladesh Inventions" : "MPS",
    u"Lorwyn" : "LRW",
    u"Commander's Arsenal" : "CM1",
    u"Tempest" : "TMP",
    u"European Land Program" : "pELP",
    u"Modern Masters 2017 Edition" : "MM3",
    u"Modern Masters 2015 Edition" : "MM2",
    u"Conflux" : "CON",
    u"Masters Edition IV" : "ME4",
    u"Amonkhet" : "AKH",
    u"Masters Edition III" : "ME3",
    u"Masters Edition II" : "ME2",
    u"Scars of Mirrodin" : "SOM",
    u"Innistrad" : "ISD",
    u"Ravnica: City of Guilds" : "RAV",
    u"Asia Pacific Land Program" : "pALP",
    u"Premium Deck Series: Graveborn" : "PD3",
    u"Premium Deck Series: Fire and Lightning" : "PD2",
    u"Shadowmoor" : "SHM",
    u"Fifth Edition" : "5ED",
    u"Starter 1999" : "S99",
    u"Magic: The Gathering-Commander" : "CMD",
    u"Fate Reforged" : "FRF",
    u"Multiverse Gift Box" : "MGB",
    u"Launch Parties" : "pLPA",
    u"Happy Holidays" : "pHHO",
    u"Ninth Edition" : "9ED",
    u"Eventide" : "EVE",
    u"Unhinged" : "UNH",
    u"Unlimited Edition" : "2ED",
    u"Duel Decks: Elves vs. Goblins" : "EVG",
    u"Fifth Dawn" : "5DN",
    u"Odyssey" : "ODY",
    u"New Phyrexia" : "NPH",
    u"Masters Edition" : "MED",
    u"Limited Edition Beta" : "LEB",
    u"Grand Prix" : "pGPX",
    u"Planeshift" : "PLS",
    u"Nemesis" : "NMS",
    u"Legends" : "LEG",
    u"Starter 2000" : "S00",
    u"Zendikar" : "ZEN",
    u"Vintage Masters" : "VMA",
    u"Magic 2011" : "M11",
    u"Magic 2010" : "M10",
    u"Magic 2013" : "M13",
    u"Magic 2012" : "M12",
    u"Planar Chaos" : "PLC",
    u"Magic 2014 Core Set" : "M14",
    u"Magic Origins" : "ORI",
    u"Modern Masters" : "MMA",
    u"Oath of the Gatewatch" : "OGW",
    u"Introductory Two-Player Set" : "ITP",
    u"Urza's Saga" : "USG",
    u"Super Series" : "pSUS",
    u"Torment" : "TOR",
    u"Fourth Edition" : "4ED",
    u"Gatecrash" : "GTC",
    u"Guru" : "pGRU",
    u"Future Sight" : "FUT",
    u"Duels of the Planeswalkers" : "DPA",
    u"Commander 2013 Edition" : "C13",
    u"Summer of Magic" : "pSUM",
    u"Commander 2015" : "C15",
    u"Commander 2014" : "C14",
    u"Conspiracy: Take the Crown" : "CN2",
    u"Shadows over Innistrad" : "SOI",
    u"Saviors of Kamigawa" : "SOK",
    u"From the Vault: Exiled" : "V09",
    u"Seventh Edition" : "7ED",
    u"Commander 2016" : "C16",
    u"Classic Sixth Edition" : "6ED",
    u"Eldritch Moon" : "EMN",
    u"Onslaught" : "ONS",
    u"Dissension" : "DIS",
    u"Mirrodin Besieged" : "MBS",
    u"Kaladesh" : "KLD",
    u"Fallen Empires" : "FEM",
    u"Magic: The Gathering—Conspiracy" : "CNS",
    u"Portal Second Age" : "PO2",
    u"Ice Age" : "ICE",
    u"Archenemy: Nicol Bolas" : "E01",
    u"Hour of Devastation" : "HOU",
    u"Planechase" : "HOP",
    u"Khans of Tarkir" : "KTK",
    u"Urza's Legacy" : "ULG",
    u"Deckmasters" : "DKM",
    u"Urza's Destiny" : "UDS",
    u"Champions of Kamigawa" : "CHK",
    u"Legions" : "LGN",
    u"From the Vault: Realms" : "V12",
    u"From the Vault: Twenty" : "V13",
    u"From the Vault: Relics" : "V10",
    u"From the Vault: Legends" : "V11",
    u"From the Vault: Lore" : "V16",
    u"Portal Demo Game" : "pPOD",
    u"From the Vault: Annihilation (2014)" : "V14",
    u"From the Vault: Angels" : "V15",
    u"Ugin's Fate promos" : "FRF_UGIN",
    u"Alara Reborn" : "ARB",
    u"Archenemy" : "ARC",
    u"Exodus" : "EXO",
    u"Worldwake" : "WWK",
    u"Duel Decks Anthology, Jace vs. Chandra" : "DD3_JVC",
    u"Arabian Nights" : "ARN"
}

border_lookup = {
    "ATH" : "white",
    "CPK" : "black",
    "p2HG" : "black",
    "GPT" : "black",
    "DRK" : "black",
    "BOK" : "black",
    "EXP" : "black",
    "DKA" : "black",
    "pWOR" : "black",
    "pWOS" : "black",
    "DRB" : "black",
    "HML" : "black",
    "MD1" : "black",
    "JOU" : "black",
    "AER" : "black",
    "pMGD" : "black",
    "ATQ" : "black",
    "pPRE" : "black",
    "WTH" : "black",
    "STH" : "black",
    "pPRO" : "black",
    "8ED" : "white",
    "pREL" : "black",
    "pMPR" : "black",
    "VAN" : "black",
    "LEA" : "black",
    "pCMP" : "black",
    "POR" : "black",
    "THS" : "black",
    "ALL" : "black",
    "CHR" : "white",
    "TPR" : "black",
    "MRD" : "black",
    "BFZ" : "black",
    "BNG" : "black",
    "pARL" : "black",
    "pGTW" : "black",
    "DGM" : "black",
    "RQS" : "white",
    "W17" : "black",
    "W16" : "black",
    "VIS" : "black",
    "APC" : "black",
    "pCEL" : "black",
    "ALA" : "black",
    "DTK" : "black",
    "H09" : "black",
    "PCY" : "black",
    "EMA" : "black",
    "pWPN" : "black",
    "MMQ" : "black",
    "pWCQ" : "black",
    "TSB" : "black",
    "pDRC" : "black",
    "CMA" : "black",
    "pJGP" : "black",
    "3ED" : "white",
    "PCA" : "black",
    "TSP" : "black",
    "CED" : "black",
    "PTK" : "white",
    "JUD" : "black",
    "UGL" : "silver",
    "DD2" : "black",
    "SCG" : "black",
    "ROE" : "black",
    "CEI" : "black",
    "10E" : "black",
    "pLGM" : "black",
    "DD3_GVL" : "black",
    "MPS_AKH" : "black",
    "RTR" : "black",
    "M15" : "black",
    "pMEI" : "black",
    "DST" : "black",
    "MIR" : "black",
    "CSP" : "black",
    "p15A" : "black",
    "DDS" : "black",
    "DDR" : "black",
    "DDQ" : "black",
    "DDP" : "black",
    "DDK" : "black",
    "DDJ" : "black",
    "DDI" : "black",
    "DDH" : "black",
    "DDO" : "black",
    "DDN" : "black",
    "DDM" : "black",
    "DDL" : "black",
    "DDC" : "black",
    "CST" : "black",
    "DDG" : "black",
    "DDF" : "black",
    "DDE" : "black",
    "DDD" : "black",
    "DD3_EVG" : "black",
    "DD3_DVD" : "black",
    "PC2" : "black",
    "MOR" : "black",
    "INV" : "black",
    "pFNM" : "black",
    "AVR" : "black",
    "BRB" : "white",
    "BTD" : "white",
    "MPS" : "black",
    "LRW" : "black",
    "CM1" : "black",
    "TMP" : "black",
    "pELP" : "black",
    "MM3" : "black",
    "MM2" : "black",
    "CON" : "black",
    "ME4" : "black",
    "AKH" : "black",
    "ME3" : "black",
    "ME2" : "black",
    "SOM" : "black",
    "ISD" : "black",
    "RAV" : "black",
    "pALP" : "black",
    "PD3" : "black",
    "PD2" : "black",
    "SHM" : "black",
    "5ED" : "white",
    "S99" : "white",
    "CMD" : "black",
    "FRF" : "black",
    "MGB" : "black",
    "pLPA" : "black",
    "pHHO" : "silver",
    "9ED" : "white",
    "EVE" : "black",
    "UNH" : "silver",
    "2ED" : "white",
    "EVG" : "black",
    "5DN" : "black",
    "ODY" : "black",
    "NPH" : "black",
    "MED" : "black",
    "LEB" : "black",
    "pGPX" : "black",
    "PLS" : "black",
    "NMS" : "black",
    "LEG" : "black",
    "S00" : "white",
    "ZEN" : "black",
    "VMA" : "black",
    "M11" : "black",
    "M10" : "black",
    "M13" : "black",
    "M12" : "black",
    "PLC" : "black",
    "M14" : "black",
    "ORI" : "black",
    "MMA" : "black",
    "OGW" : "black",
    "ITP" : "white",
    "USG" : "black",
    "pSUS" : "black",
    "TOR" : "black",
    "4ED" : "white",
    "GTC" : "black",
    "pGRU" : "black",
    "FUT" : "black",
    "DPA" : "black",
    "C13" : "black",
    "pSUM" : "black",
    "C15" : "black",
    "C14" : "black",
    "CN2" : "black",
    "SOI" : "black",
    "SOK" : "black",
    "V09" : "black",
    "7ED" : "white",
    "C16" : "black",
    "6ED" : "white",
    "EMN" : "black",
    "ONS" : "black",
    "DIS" : "black",
    "MBS" : "black",
    "KLD" : "black",
    "FEM" : "black",
    "CNS" : "black",
    "PO2" : "black",
    "ICE" : "black",
    "E01" : "black",
    "HOU" : "black",
    "HOP" : "black",
    "KTK" : "black",
    "ULG" : "black",
    "DKM" : "white",
    "UDS" : "black",
    "CHK" : "black",
    "LGN" : "black",
    "V12" : "black",
    "V13" : "black",
    "V10" : "black",
    "V11" : "black",
    "V16" : "black",
    "pPOD" : "black",
    "V14" : "black",
    "V15" : "black",
    "FRF_UGIN" : "black",
    "ARB" : "black",
    "ARC" : "black",
    "EXO" : "black",
    "WWK" : "black",
    "DD3_JVC" : "black",
    "ARN" : "black"   
}

foil_lookup = {
    "ATH" : "N",
    "CPK" : "Y",
    "p2HG" : "Y",
    "GPT" : "Y",
    "DRK" : "N",
    "BOK" : "Y",
    "EXP" : "Y",
    "DKA" : "Y",
    "pWOR" : "Y",
    "pWOS" : "Y",
    "DRB" : "Y",
    "HML" : "N",
    "MD1" : "Y",
    "JOU" : "Y",
    "AER" : "Y",
    "pMGD" : "Y",
    "ATQ" : "N",
    "pPRE" : "N",
    "WTH" : "N",
    "STH" : "N",
    "pPRO" : "Y",
    "8ED" : "Y",
    "pREL" : "Y",
    "pMPR" : "Y",
    "VAN" : "N",
    "LEA" : "N",
    "pCMP" : "Y",
    "POR" : "N",
    "THS" : "Y",
    "ALL" : "N",
    "CHR" : "N",
    "TPR" : "Y",
    "MRD" : "Y",
    "BFZ" : "Y",
    "BNG" : "Y",
    "pARL" : "N",
    "pGTW" : "Y",
    "DGM" : "Y",
    "RQS" : "N",
    "W17" : "Y",
    "W16" : "Y",
    "VIS" : "N",
    "APC" : "Y",
    "pCEL" : "N",
    "ALA" : "Y",
    "DTK" : "Y",
    "H09" : "Y",
    "PCY" : "Y",
    "EMA" : "Y",
    "pWPN" : "Y",
    "MMQ" : "Y",
    "pWCQ" : "Y",
    "TSB" : "Y",
    "pDRC" : "N",
    "CMA" : "Y",
    "pJGP" : "N",
    "3ED" : "N",
    "PCA" : "Y",
    "TSP" : "Y",
    "CED" : "N",
    "PTK" : "Y",
    "JUD" : "Y",
    "UGL" : "N",
    "DD2" : "Y",
    "SCG" : "Y",
    "ROE" : "Y",
    "CEI" : "N",
    "10E" : "Y",
    "pLGM" : "N",
    "DD3_GVL" : "Y",
    "MPS_AKH" : "Y",
    "RTR" : "Y",
    "M15" : "Y",
    "pMEI" : "N",
    "DST" : "Y",
    "MIR" : "N",
    "CSP" : "Y",
    "p15A" : "Y",
    "DDS" : "Y",
    "DDR" : "Y",
    "DDQ" : "Y",
    "DDP" : "Y",
    "DDK" : "Y",
    "DDJ" : "Y",
    "DDI" : "Y",
    "DDH" : "Y",
    "DDO" : "Y",
    "DDN" : "Y",
    "DDM" : "Y",
    "DDL" : "Y",
    "DDC" : "Y",
    "CST" : "Y",
    "DDG" : "Y",
    "DDF" : "Y",
    "DDE" : "Y",
    "DDD" : "Y",
    "DD3_EVG" : "Y",
    "DD3_DVD" : "Y",
    "PC2" : "Y",
    "MOR" : "Y",
    "INV" : "Y",
    "pFNM" : "Y",
    "AVR" : "Y",
    "BRB" : "Y",
    "BTD" : "Y",
    "MPS" : "Y",
    "LRW" : "Y",
    "CM1" : "Y",
    "TMP" : "N",
    "pELP" : "Y",
    "MM3" : "Y",
    "MM2" : "Y",
    "CON" : "Y",
    "ME4" : "Y",
    "AKH" : "Y",
    "ME3" : "Y",
    "ME2" : "Y",
    "SOM" : "Y",
    "ISD" : "Y",
    "RAV" : "Y",
    "pALP" : "N",
    "PD3" : "Y",
    "PD2" : "Y",
    "SHM" : "Y",
    "5ED" : "N",
    "S99" : "Y",
    "CMD" : "Y",
    "FRF" : "Y",
    "MGB" : "N",
    "pLPA" : "Y",
    "pHHO" : "Y",
    "9ED" : "Y",
    "EVE" : "Y",
    "UNH" : "Y",
    "2ED" : "N",
    "EVG" : "Y",
    "5DN" : "Y",
    "ODY" : "Y",
    "NPH" : "Y",
    "MED" : "Y",
    "LEB" : "N",
    "pGPX" : "Y",
    "PLS" : "Y",
    "NMS" : "Y",
    "LEG" : "N",
    "S00" : "Y",
    "ZEN" : "Y",
    "VMA" : "Y",
    "M11" : "Y",
    "M10" : "Y",
    "M13" : "Y",
    "M12" : "Y",
    "PLC" : "Y",
    "M14" : "Y",
    "ORI" : "Y",
    "MMA" : "Y",
    "OGW" : "Y",
    "ITP" : "N",
    "USG" : "N",
    "pSUS" : "Y",
    "TOR" : "Y",
    "4ED" : "N",
    "GTC" : "Y",
    "pGRU" : "Y",
    "FUT" : "Y",
    "DPA" : "Y",
    "C13" : "Y",
    "pSUM" : "Y",
    "C15" : "Y",
    "C14" : "Y",
    "CN2" : "Y",
    "SOI" : "Y",
    "SOK" : "Y",
    "V09" : "Y",
    "7ED" : "Y",
    "C16" : "Y",
    "6ED" : "Y",
    "EMN" : "Y",
    "ONS" : "Y",
    "DIS" : "Y",
    "MBS" : "Y",
    "KLD" : "Y",
    "FEM" : "N",
    "CNS" : "Y",
    "PO2" : "N",
    "ICE" : "N",
    "E01" : "Y",
    "HOU" : "Y",
    "HOP" : "Y",
    "KTK" : "Y",
    "ULG" : "Y",
    "DKM" : "Y",
    "UDS" : "Y",
    "CHK" : "Y",
    "LGN" : "Y",
    "V12" : "Y",
    "V13" : "Y",
    "V10" : "Y",
    "V11" : "Y",
    "V16" : "Y",
    "pPOD" : "N",
    "V14" : "Y",
    "V15" : "Y",
    "FRF_UGIN" : "Y",
    "ARB" : "Y",
    "ARC" : "Y",
    "EXO" : "N",
    "WWK" : "Y",
    "DD3_JVC" : "Y",
    "ARN" : "N"
}

card_frame_lookup = {
    "ATH" : "Old",
    "CPK" : "M15",
    "p2HG" : "Modern",
    "GPT" : "Modern",
    "DRK" : "Old",
    "BOK" : "Modern",
    "EXP" : "M15",
    "DKA" : "Modern",
    "pWOR" : "Old",
    "pWOS" : "Old",
    "DRB" : "Modern",
    "HML" : "Old",
    "MD1" : "Modern",
    "JOU" : "Modern",
    "AER" : "M15",
    "pMGD" : "Modern",
    "ATQ" : "Old",
    "pPRE" : "Old",
    "WTH" : "Old",
    "STH" : "Old",
    "pPRO" : "Modern",
    "8ED" : "Modern",
    "pREL" : "Old",
    "pMPR" : "Old",
    "VAN" : "Old",
    "LEA" : "Old",
    "pCMP" : "Modern",
    "POR" : "Old",
    "THS" : "Modern",
    "ALL" : "Old",
    "CHR" : "Old",
    "TPR" : "M15",
    "MRD" : "Modern",
    "BFZ" : "M15",
    "BNG" : "Modern",
    "pARL" : "Old",
    "pGTW" : "Modern",
    "DGM" : "Modern",
    "RQS" : "Old",
    "W17" : "M15",
    "W16" : "M15",
    "VIS" : "Old",
    "APC" : "Old",
    "pCEL" : "Old",
    "ALA" : "Modern",
    "DTK" : "M15",
    "H09" : "Modern",
    "PCY" : "Old",
    "EMA" : "M15",
    "pWPN" : "Modern",
    "MMQ" : "Old",
    "pWCQ" : "Modern",
    "TSB" : "Modern",
    "pDRC" : "Old",
    "CMA" : "M15",
    "pJGP" : "Old",
    "3ED" : "Old",
    "PCA" : "M15",
    "TSP" : "Modern",
    "CED" : "Old",
    "PTK" : "Old",
    "JUD" : "Old",
    "UGL" : "Old",
    "DD2" : "Modern",
    "SCG" : "Old",
    "ROE" : "Modern",
    "CEI" : "Old",
    "10E" : "Modern",
    "pLGM" : "Old",
    "DD3_GVL" : "M15",
    "MPS_AKH" : "M15",
    "RTR" : "Modern",
    "M15" : "M15",
    "pMEI" : "Old",
    "DST" : "Modern",
    "MIR" : "Old",
    "CSP" : "Modern",
    "p15A" : "Modern",
    "DDS" : "M15",
    "DDR" : "M15",
    "DDQ" : "M15",
    "DDP" : "M15",
    "DDK" : "Modern",
    "DDJ" : "Modern",
    "DDI" : "Modern",
    "DDH" : "Modern",
    "DDO" : "M15",
    "DDN" : "M15",
    "DDM" : "Modern",
    "DDL" : "Modern",
    "DDC" : "Modern",
    "CST" : "Modern",
    "DDG" : "Modern",
    "DDF" : "Modern",
    "DDE" : "Modern",
    "DDD" : "Modern",
    "DD3_EVG" : "M15",
    "DD3_DVD" : "M15",
    "PC2" : "Modern",
    "MOR" : "Modern",
    "INV" : "Old",
    "pFNM" : "Old",
    "AVR" : "Modern",
    "BRB" : "Old",
    "BTD" : "Old",
    "MPS" : "M15",
    "LRW" : "Modern",
    "CM1" : "Modern",
    "TMP" : "Old",
    "pELP" : "Old",
    "MM3" : "M15",
    "MM2" : "M15",
    "CON" : "Modern",
    "ME4" : "Modern",
    "AKH" : "M15",
    "ME3" : "Modern",
    "ME2" : "Modern",
    "SOM" : "Modern",
    "ISD" : "Modern",
    "RAV" : "Modern",
    "pALP" : "Old",
    "PD3" : "Modern",
    "PD2" : "Modern",
    "SHM" : "Modern",
    "5ED" : "Old",
    "S99" : "Old",
    "CMD" : "Modern",
    "FRF" : "M15",
    "MGB" : "Old",
    "pLPA" : "Modern",
    "pHHO" : "Modern",
    "9ED" : "Modern",
    "EVE" : "Modern",
    "UNH" : "Modern",
    "2ED" : "Old",
    "EVG" : "Modern",
    "5DN" : "Modern",
    "ODY" : "Old",
    "NPH" : "Modern",
    "MED" : "Modern",
    "LEB" : "Old",
    "pGPX" : "Modern",
    "PLS" : "Old",
    "NMS" : "Old",
    "LEG" : "Old",
    "S00" : "Old",
    "ZEN" : "Modern",
    "VMA" : "Modern",
    "M11" : "Modern",
    "M10" : "Modern",
    "M13" : "Modern",
    "M12" : "Modern",
    "PLC" : "Modern",
    "M14" : "Modern",
    "ORI" : "M15",
    "MMA" : "Modern",
    "OGW" : "M15",
    "ITP" : "Old",
    "USG" : "Old",
    "pSUS" : "Old",
    "TOR" : "Old",
    "4ED" : "Old",
    "GTC" : "Modern",
    "pGRU" : "Old",
    "FUT" : "Modern",
    "DPA" : "Modern",
    "C13" : "Modern",
    "pSUM" : "Modern",
    "C15" : "M15",
    "C14" : "M15",
    "CN2" : "M15",
    "SOI" : "M15",
    "SOK" : "Modern",
    "V09" : "Modern",
    "7ED" : "Old",
    "C16" : "M15",
    "6ED" : "Old",
    "EMN" : "M15",
    "ONS" : "Old",
    "DIS" : "Modern",
    "MBS" : "Modern",
    "KLD" : "M15",
    "FEM" : "Old",
    "CNS" : "Modern",
    "PO2" : "Old",
    "ICE" : "Old",
    "E01" : "M15",
    "HOU" : "M15",
    "HOP" : "Modern",
    "KTK" : "M15",
    "ULG" : "Old",
    "DKM" : "Old",
    "UDS" : "Old",
    "CHK" : "Modern",
    "LGN" : "Old",
    "V12" : "Modern",
    "V13" : "Modern",
    "V10" : "Modern",
    "V11" : "Modern",
    "V16" : "M15",
    "pPOD" : "Old",
    "V14" : "M15",
    "V15" : "M15",
    "FRF_UGIN" : "M15",
    "ARB" : "Modern",
    "ARC" : "Modern",
    "EXO" : "Old",
    "WWK" : "Modern",
    "DD3_JVC" : "M15",
    "ARN" : "Old"
}
