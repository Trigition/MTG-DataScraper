#!/usr/bin/env python

import pandas as pd
import argparse
import networkx as nx

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
    defined_abilities = [line.strip() for line in open(ability_filename, 'r').readlines()]
    return defined_abilities

def load_abilities(abilities, graph):
    for ability in abilities:
        graph.add_node(ability)

def which_abilities_in_text(abilities, oracle_text):
    found_abilities = []
    for ability in abilities:
        try:
            if ability.lower() in oracle_text.lower():
                found_abilities.append(ability)
        except AttributeError:
            return []
    return found_abilities

def find_abilities(data, ability_filename="all_abilities.txt"):
    graph = nx.DiGraph()
    abilities = get_defined_abilities(ability_filename)
    load_abilities(abilities, graph)

    for index, row in data.iterrows():
        oracle_text = row['oracle_text']
        found_abilities = which_abilities_in_text(abilities, oracle_text)
        if len(found_abilities) > 0:
            print '%s [%s] has abilities:' % (row['name'], row['gatherer_id']), found_abilities
            graph.add_node(row['name'], label=row['name'], color=row['colors'])
                

find_abilities( get_data_frames() )
