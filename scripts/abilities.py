#!/usr/bin/env python

import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="This python scripts attempts to recognize abilities in card text")
parser.add_argument('inputs', help='Input CSV files', nargs='+')
args = parser.parse_args()

def get_data_frames():
    print "Grabbing csv files..."
    dataframes = [pd.DataFrame.from_csv(x) for x in args.inputs]
    if len(dataframes) > 1:
        all_cards = dataframes[0].append(dataframes[1:])
    else:
        all_cards = dataframes[0]
    return all_cards

def get_defined_abilities(ability_filename):
    defined_abilities = [line.strip().lower() for line in open(ability_filename, 'r').readlines()]
    return defined_abilities

all_abilities = get_defined_abilities('all_abilities.txt')
all_cards = get_data_frames()
all_cards = all_cards.dropna(subset=['oracle_text'])

ability_joins_table = []

for index, card in all_cards.iterrows():
    for ability in all_abilities:
        if ability in card['oracle_text'].lower():
            row = {}
            row['card_id'] = card['name']
            row['ability_id'] = ability
            
            ability_joins_table.append(row)

print pd.DataFrame(ability_joins_table)
