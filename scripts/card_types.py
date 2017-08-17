import pandas as pd
from collections import OrderedDict

def split_type(subtype_string):
    subtypes = [x for x in subtype_string.decode('utf8').split(' ')]
    return subtypes

def get_all_supertypes(data):
    supertypes = [string.encode('utf8') for string in data['supertypes'].unique()]
    return sorted(supertypes)

def get_subtypes(supertype, data):
    query = data[data['supertypes'] == supertype]
    query = query.dropna(subset=['subtypes'])

    all_subtypes = set()
    for index, row in query.iterrows():
        subtypes = split_type(row['subtypes'])
        #all_subtypes.add(subtypes)
        for subtype in subtypes:
            all_subtypes.add(subtype)

    return sorted( list(all_subtypes) )

def get_all_types(data, column):
    query = data.dropna(subset=[column])
    all_types = set()
    for index, row in query.iterrows():
        types = split_type(row[column])
        for cur_type in types:
            all_types.add(cur_type.encode('utf8'))

    return sorted( list(all_types) )

def get_join_table(cards, column):
    table = []
    for index, card in cards.iterrows():
        # Grab subtypes
        type_order = 1
        if type(card[column]) is not float:
            for subtype in split_type(card[column]):
                row = {}
                row['card_id'] = card['name']
                row['type_id'] = subtype
                row['type_order'] = str(type_order)

                table.append(row)

                type_order += 1
    return table
