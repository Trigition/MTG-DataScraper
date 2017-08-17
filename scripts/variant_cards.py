#!/usr/bin/env python

import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="This python script generates a csv describing all the physical cards")
parser.add_argument('inputs', help='Input CSV files', nargs='+')
parser.add_argument('output', help='Optional output csv filename, defaults to "variants_join_table.csv"', nargs='?', default="variants_joins_table.csv")

args = parser.parse_args()

def get_data_frames():
    print "Grabbing csv files..."
    dataframes = [pd.read_csv(x) for x in args.inputs]
    if len(dataframes) > 1:
        all_cards = dataframes[0].append(dataframes[1:], ignore_index=True)
    else:
        all_cards = dataframes[0]
    return all_cards

all_cards = get_data_frames()
cards_seen = []
variants = []

for name, group in all_cards.groupby(['name']):
    if len(group) > 1:
        if name not in cards_seen:
            for variant in group['gatherer_id']:
                cur_variant = {}
                cur_variant['name'] = name
                cur_variant['variant'] = variant
                variants.append(cur_variant)
            cards_seen.append(name)
        
print "Writing file"
print pd.DataFrame(variants)
pd.DataFrame(variants).to_csv(args.output, index=False)
print "Done"
