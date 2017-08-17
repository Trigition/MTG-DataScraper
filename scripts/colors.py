#!/usr/bin/env python
import pandas as pd

defined_colors = []

abbr_column_name = 'color_abbreviation'
color_column_name = 'color_name'
color_icon_class = 'color_icon_class'
color_id_name = 'color_id'

defined_colors.append(
    {abbr_column_name : 'w',
    color_column_name : 'white',
    color_icon_class : 'w',
    color_id_name : 1}
    )
defined_colors.append(
        {abbr_column_name : 'u',
        color_column_name : 'blue',
        color_icon_class : 'w',
        color_id_name : 2}
    )
defined_colors.append(
        {abbr_column_name : 'b',
        color_column_name : 'black',
        color_icon_class : 'b',
        color_id_name : 3}
    )
defined_colors.append(
        {abbr_column_name : 'r',
            color_column_name : 'red',
            color_icon_class : 'r',
            color_id_name : 4}
        )
defined_colors.append(
        {abbr_column_name : 'g',
            color_column_name : 'green',
            color_icon_class : 'g',
            color_id_name : 5})
defined_colors.append(
        {abbr_column_name : 'c',
            color_column_name : 'colorless',
            color_icon_class : '',
            color_id_name : 6})

colors = pd.DataFrame(defined_colors)

colors.to_csv('color_definitions.csv', encoding='utf8', index=False)

def get_color_ids(color_str):
    #if (type(color_str)) is float:
    #    return [color_id['c']]
    #return [color_id[c] for c in color_str]
    if (type(color_str)) is float:
        return colors.loc[colors[abbr_column_name] == 'c'][color_id_name].index.values
    color_ids = []
    for color_char in color_str:
        color_ids.append( colors.loc[colors[abbr_column_name] == color_char][color_id_name].index.values[0])
    return color_ids
