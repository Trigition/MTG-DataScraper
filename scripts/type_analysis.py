#!/usr/bin/env python
import pandas as pd
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import pprint
from networkx.drawing.nx_agraph import graphviz_layout
from collections import OrderedDict

parser = argparse.ArgumentParser(description='This python script analyzes the type hierarchy')
parser.add_argument('inputs', help='Input CSV files', nargs='+')
args = parser.parse_args()

def get_data_frames():
    print "Grabbing csv files..."
    dataframes = [pd.DataFrame.from_csv(x) for x in args.inputs]
    all_cards = dataframes[0].append(dataframes[1:])
    print "Done loading data"
    return all_cards

def find_root_nodes(graph):
    roots = []
    for node in graph.nodes():
        if graph.in_degree(node) == 0:
            # Root node
            roots.append(node)
    return roots

def print_bfs_from_root(graph, root):
    queue = [(root, 0)]
    discovered = []
    while len(queue) > 0:
        cur_node, distance = queue.pop()
        print ('\t' * distance), cur_node
        for neighbor in graph.neighbors_iter(cur_node):
            if not neighbor in discovered:
                discovered.append(neighbor)
                queue.insert(0, (neighbor, distance+1) )


def print_dfs_from_dict(cur_dict, depth=0,delim='\t'):
    #if depth == 0:
    #    print '\n'
    if cur_dict != {}:
        for key, value in cur_dict.items():
            print (delim*depth), key.encode('utf8')
            print_dfs_from_dict(cur_dict[key], depth+1)

cards = get_data_frames()
supertypes = [string.encode('utf8') for string in cards['supertypes'].unique()]

paths = []

for index,row in cards.iterrows():
    supertype = row['supertypes'].encode('utf8')
    if type(row['subtypes']) is str:
        subtypes = [x for x in row['subtypes'].decode('utf8').split(' ')]
    else:
        subtypes = []
    paths.append( [supertype] + subtypes )


# CREATE GRAPH
graph = nx.DiGraph()
roots = []

hierarchy = {}

for path in paths:
    if len(path) == 1:
        hierarchy[path[0]] = {}
    else:
        prev = path[0]
        
        if not prev in hierarchy:
            hierarchy[prev] = {}
        
        cur_dict = hierarchy[prev]
        depth = 0
        for cur_type in path[1:]:
            if not cur_type in cur_dict:
                cur_dict[cur_type] = {}
            cur_dict = cur_dict[cur_type]

ordered_dict = OrderedDict(hierarchy)
#print_dfs_from_dict(hierarchy)
print_dfs_from_dict(ordered_dict)
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(hierarchy)
