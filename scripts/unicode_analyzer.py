#!/usr/bin/env python
import pandas as pd
import argparse
import string
from collections import Counter

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser(description="This python script finds rogue Unicode characters in MTG CSV datasets\
                                              it will print the card name and appropriate set and the field which\
                                              is in violation")

parser.add_argument("inputs", help="Input CSV files", nargs='+')
args = parser.parse_args()
dataframes = []

# Keep Track of Unicode Characters
unicode_occurances = Counter()

def is_ascii(card_string):
    if not type(card_string) is str:
        return True
    try:
        card_string.encode('ascii')
        card_string.decode('ascii')
    except UnicodeEncodeError:
        return False
    except UnicodeDecodeError:
        return False

    return True

def get_non_ascii_indexes(card_string):
    indexes = [i for i,j in enumerate(card_string.decode('utf8')) if j not in string.printable]
    return indexes

def update_occurances(card_string):
    decoded = card_string.decode('utf8')
    indexes = get_non_ascii_indexes(card_string)
    for index in indexes:
        unicode_occurances[decoded[index]] += 1

def highlight_string(card_string, bad_indexes):
    highlight_str = ''
    for index, char in enumerate(card_string.decode('utf8')):
        if index in bad_indexes:
            highlight_str += bcolors.FAIL
            highlight_str += char
            highlight_str += bcolors.ENDC
        else:
            highlight_str += char
    return highlight_str

def search_row(row):
    for key,value in row.iteritems():
        if not is_ascii(value):
            print "Bad Column: %s, %s %s" % (key, row['name'], row['gatherer_id'])
            print value
            print highlight_string(value, get_non_ascii_indexes(value)), '\n'
            update_occurances(value)
            return True
    return False

# Load in DataFrames
for csv_file in args.inputs:
    print "Loading CSV:", csv_file
    dataframes.append(pd.DataFrame.from_csv(csv_file))

# Combine DataFrames
all_cards = dataframes[0].append(dataframes[1:])
filtered = all_cards[all_cards.apply(lambda row: search_row(row), axis=1)]

output = open('unicode_histogram.csv', 'w')
output.write('Character,Occurances,Unicode\n')
for key,value in unicode_occurances.items():
    print key, value, key.encode('unicode-escape')
    output.write(key.encode('utf8'))
    output.write(',')
    output.write(str(value))
    output.write(',')
    output.write(key.encode('unicode-escape'))
    output.write('\n')
