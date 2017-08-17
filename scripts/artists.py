#!/usr/bin/env python
import pandas as pd
import codecs

def split_artists(row):
    artist_string = row['artist'].decode('utf8')

    # Attempt to split by & and 'and'
    # Replace & and 'and' with similar delimiter
    # delimiters are assumed to be surrounded by spaces
    sanitized_artists = artist_string.replace(' & ', '$').replace(' and ', '$')
    artists = [artist.strip() for artist in sanitized_artists.split('$')]

    return artists

def load_artist_correction_dict(filename):
    corrections = {}
    for line in codecs.open(filename, 'r', encoding='utf8').readlines():
        # If line begins with '#' ignore
        if line[0].strip() == '#' or len(line.strip()) == 0:
            continue
        bad_name, corrected_name = line.split(' -> ')
        # Clean up names
        bad_name = bad_name.strip()
        corrected_name = corrected_name.strip()

        corrections[bad_name] = corrected_name

    return corrections

def artist_card(raw_card, new_card_id, artist_table, args, correction_dict={}):

    card_artists_table = []
    card_id = new_card_id

    for referenced_artist in split_artists(raw_card):
        # Check to see if referenced artist needs to be corrected
        if referenced_artist in correction_dict:
            # Artist name needs to be corrected
            cur_artist = correction_dict[referenced_artist]
            print "Correcting: %s to %s" % (referenced_artist, cur_artist)
        else:
            # No correcition necessary
            cur_artist = referenced_artist

        # Grab id of artist and create reference
        artist_id = artist_table.get_id(cur_artist, 'artist')
        card_artists_table.append( {args.card_id_column : new_card_id,
                                    args.artist_id_column : artist_id} )
    return card_artists_table
