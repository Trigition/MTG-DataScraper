#!/usr/bin/env python
import pandas as pd
import argparse
import codecs
import artists
import card_types
import colors
import physical_cards as physicals
from tables import Table

def parse_args():
    
    parser = argparse.ArgumentParser(
            description="This python script generates a csv describing all the physical cards")

    parser.add_argument(
            '-c',
            '--correction_file',
            default='artist_correction_dictionary.txt',
            help='Dictionary file containing artist name corrections',
            nargs='?')

    parser.add_argument(
            '--cards_table',
            help='CSV file representing cards already in the database, this is to avoid ID collision',
            nargs='?')

    parser.add_argument(
            '--card_id_column',
            help='The field label for card ids, defaults to \'card_id\'',
            default='card_id',
            nargs='?')

    parser.add_argument(
            '--artists_table',
            help='The current artist database dump',
            nargs='?')

    parser.add_argument(
            '--artist_id_column',
            help='The artist id column name, defaults to \'artist_id\'',
            default='artist_id',
            nargs='?')

    parser.add_argument(
            '--types_table',
            help='The current type database dump',
            nargs='?')

    parser.add_argument(
            '--type_id_column',
            help='The type id column name, defaults to \'artist_id\'',
            default='type_id',
            nargs='?')

    parser.add_argument(
            '--physical_cards_table',
            help='The current physical card database dump',
            nargs='?')

    parser.add_argument(
            '--physical_card_id_column',
            help='The physical id column name, defaults to \'physical_card_id\'',
            default='physical_card_id',
            nargs='?')

    parser.add_argument(
            '--sets_table',
            help='The current sets in the database',
            nargs='?')

    parser.add_argument(
            '--set_id_column',
            help='The set id column name, defaults to \'set_id\'',
            default='set_id',
            nargs='?')

    parser.add_argument('inputs', help='Input CSV files', nargs='+')

    args = parser.parse_args()

    return args

def get_data_frames(csv_files):
    print "Grabbing csv files..."
    dataframes = [pd.read_csv(x) for x in csv_files]
    if len(dataframes) > 1:
        all_cards = dataframes[0].append(dataframes[1:], ignore_index=True)
    else:
        all_cards = dataframes[0]
    return all_cards

def get_occupied_ids(active_data, id_column_name):
    active_cards = pd.read_csv(active_data)
    ids = active_cards[id_column_name]
    return ids

def get_free_min_id(csv_table_filename, id_column_name):
    
    if csv_table_filename is None:
        return 1

    table = pd.read_csv(csv_table_filename)

    occupied_ids = table[id_column_name]
    min_unoccupied_id= occupied_ids.max() + 1

    return min_unoccupied_id

def assign_ids(new_cards, id_column_name, occupied_ids=None, inplace=False):
    
    # Get max ID
    if occupied_ids is not None:
        min_unused_id = occupied_ids.max() + 1
    else:
        min_unused_id = 1

    max_needed_id = len(new_cards) + min_unused_id
    new_ids = pd.Series(range(min_unused_id, max_needed_id))

    # Assign list of new ids to card_dataframe
    assigned_cards = new_cards.assign(ids=new_ids.values)
    assigned_cards = assigned_cards.rename(columns = {'ids' : id_column_name })

    if inplace:
        new_cards = assigned_cards
    else:
        return assigned_cards

def generate_new_card(row, cur_new_card_id, new_card_id_column):
    new_card = {}

    # Generate fields which can be immediately known now
    # Joins tables or references to other models will be 
    # populated once we know that information
    new_card[new_card_id_column] = cur_new_card_id
    new_card['card_name'] = row['card_name']
    new_card['gatherer_id'] = row['gatherer_id']
    new_card['flavor_text'] = row['flavor_text']
    new_card['printed_text'] = row['printed_text']
    new_card['oracle_text'] = row['oracle_text']
    new_card['mana_cost'] = row['mana_cost']
    new_card['converted_mana_cost'] = row['converted_mana_cost']
    new_card['power'] = row['power']
    new_card['toughness'] = row['toughness']
    new_card['loyalty'] = row['loyalty']
    new_card['rarity'] = row['rarity']
    new_card['collectors_number'] = row['collectors_number']
    new_card['border_type'] = row['border_type']
    new_card['foil'] = row['foil']
    new_card['frame_type'] = row['frame_type']

    return new_card

def write_table(table_array, filename):
    dataframe = pd.DataFrame(table_array)
    #dataframe.to_csv(filename, mode='w', encoding='utf8', index=False)
    write_dataframe(dataframe, filename)

def write_dataframe(dataframe, filename):
    dataframe.to_csv(filename, mode='w', encoding='utf8', index=False)

# Check to see if we are running this file
if __name__ == "__main__":
   
    ### ID calculation and assignment phase
    ### Occupied IDs are determined and free IDs are assigned
    ### to new values

    min_free_ids = {}
    args = parse_args()
    all_cards = get_data_frames(args.inputs)

    # Obtain first free_id
    min_free_ids['card_id'] = get_free_min_id(args.cards_table, args.card_id_column)

    new_cards = []
    physical_cards = []
    color_table = []
    current_artists = Table(args.artist_id_column, args.artists_table, columns=['artist'])
    current_types = Table(args.type_id_column, args.types_table, columns=['type'])
    current_physicals = Table(args.physical_card_id_column, args.physical_cards_table, columns=['gatherer_id'])
    current_sets = Table(args.set_id_column, args.sets_table, columns=['set'])

    joins_artists_table = []
    joins_types_table = []
    
    corrections = artists.load_artist_correction_dict(args.correction_file)

    # Begin to parse new cards to generate new database import tables
    for index, raw_card in all_cards.iterrows():
        print 'Processing: %s' % raw_card['card_name']
        new_card_id = index + min_free_ids['card_id']
        new_card = generate_new_card(raw_card, new_card_id, args.card_id_column)

        raw_artist = raw_card['artist']
        raw_supertype = raw_card['supertypes']
        raw_subtype = raw_card['subtypes']

        # Define set for new card

        set_id = current_sets.get_id(raw_card['set_name'], 'set')
        new_card[args.set_id_column] = set_id

        joins_artists_table += artists.artist_card(raw_card,
                                                   new_card_id,
                                                   current_artists,
                                                   args,
                                                   corrections)

        ## Get Types
        # For Supertypes
        type_order = 1
        for supertype in card_types.split_type(raw_card['supertypes']):
            type_id = current_types.get_id(supertype, 'type')
            joins_types_table.append( { args.card_id_column : new_card_id,
                                        args.type_id_column : type_id,
                                        'type_order' : type_order} )
            type_order += 1
        # For Subtypes
        if type(raw_card['subtypes']) is not float:
            type_order = 1
            for subtype in card_types.split_type(raw_card['subtypes']):
                type_id = current_types.get_id(subtype, 'type')
                joins_types_table.append( { args.card_id_column : new_card_id,
                                            args.type_id_column : type_id,
                                            'type_order' : type_order } )
                type_order += 1

        # Generate color joins table
        color_ids = colors.get_color_ids(raw_card['colors'])
        
        for color_id in color_ids:
            color_row = {}
            color_row['color_id'] = color_id
            color_row['card_id'] = new_card_id

            color_table.append(color_row)

        new_cards.append(new_card)

    cards = pd.DataFrame(new_cards)

    # Final calculation phase, generate physical and set information
    print 'Calculating physical card table'
    physical_cards = physicals.physical_card_join(cards, current_physicals)

    ## Write tables to files
    write_dataframe(current_artists.new_rows, 'new_artist_table.csv')
    write_dataframe(current_types.new_rows, 'new_types.csv')
    write_dataframe(current_physicals.new_rows, 'new_physicals.csv')
    write_dataframe(current_sets.new_rows, 'new_sets.csv')
    write_table(joins_artists_table, 'artists_joins_cards_table.csv')
    write_table(joins_types_table, 'types_joins_cards_table.csv')
    write_table(physical_cards, 'physical_joins_cards.csv')
    write_table(color_table, 'colors_joins_cards_table.csv')

    # One of the Gotcha's of working with Pandas is that NaN is treated as a float
    # Set NaN to be 0. There shouldn't be floating point converted mana costs
    cards['converted_mana_cost'] = cards['converted_mana_cost'].fillna(0).astype(int)
    cards.to_csv('new_cards.csv', encoding='utf8', index=False)
