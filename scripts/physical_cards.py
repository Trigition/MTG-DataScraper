#!/usr/bin/env python
import pandas as pd
import argparse
physical_cards = []

def physical_card_join(cards, physical_table):
    physical_card_joins = []

    for gatherer_id, group in cards.groupby(['gatherer_id']):
        side = 0
        physical_id = physical_table.get_id(gatherer_id, 'gatherer_id')
        print 'Determining physicals for: %s' % gatherer_id
        for card in group['card_id']:
            cur_physical_card = {}
            cur_physical_card['physical_id'] = physical_id
            cur_physical_card['card_id'] = card
            cur_physical_card['side'] = side

            side += 1
            physical_card_joins.append(cur_physical_card)

    return physical_card_joins

#for gatherer_id, group in all_cards.groupby(['gatherer_id']):
#    side = 0
#    for card in group['name']:
#        cur_physical_card = {}
#        cur_physical_card['gatherer_id'] = gatherer_id
#        cur_physical_card['card_id'] = card
#        cur_physical_card['side'] = str(side)
#
#        side += 1
#
#        physical_cards.append(cur_physical_card)
#
#
