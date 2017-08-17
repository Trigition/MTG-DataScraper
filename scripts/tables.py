import pandas as pd

class Table:
    
    def __init__(self, id_column_name, table_filename=None, columns=[]):
        if table_filename is not None:
            self.table = pd.read_csv(table_filename)
            self.lowest_free_id = self.table[id_column_name].max() + 1
        else:
            self.table = None
            self.lowest_free_id = 1
        
        self.id_column_name = id_column_name

        columns = [self.id_column_name] + columns
        self.new_rows = pd.DataFrame(columns=columns)

    def get_next_id(self):
        min_id = self.lowest_free_id
        self.lowest_free_id += 1

        return min_id

    def get_new_row(self, item, column_name):
        new_row = {}
        new_row[self.id_column_name] = self.get_next_id()
        new_row[column_name] = item
        self.new_rows = self.new_rows.append([new_row], ignore_index=True)
        return new_row

    def is_item_defined(self, item, column_name):
        #current_items = pd.DataFrame(self.new_rows)
        #if len(self.new_rows) > 0 and item in current_items[column_name]:
        #if len(self.new_rows) > 0 and any(row[column_name] == item for row in self.new_rows):
            #return current_items[current_items[column_name] == item][self.id_column_name]
        #    return True

        #if self.table is not None and item in self.table[column_name]:
            #return self.table[table[column_name] == item][self.id_column_name]
        #    return True
        #return False
        return item in self.new_rows[column_name].values

    def get_id(self, item, column_name):
        #if self.is_item_defined(item, column_name):
        #    #current_items = pd.DataFrame(self.new_rows)
        #    found_item = current_items.loc[current_items[column_name] == item][self.id_column_name]
        #    return found_item.index.values[0]
        #    #return is_item_defined(item, column_name)
        ## Item is not defined, create new row
        #new_item = self.get_new_row()
        #new_item[column_name] = item
        #return new_item[self.id_column_name]
        if self.is_item_defined(item, column_name):
            return self.new_rows.loc[self.new_rows[column_name] == item][self.id_column_name]
        
        new_item = self.get_new_row(item, column_name)
        return new_item[self.id_column_name]
