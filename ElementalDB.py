import os
import bson
import time

class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.records = []
        self.indexed_data = {col: {} for col in columns}

    def add_records(self, records):
        for record in records:
            if len(record) != len(self.columns):
                raise ValueError("Record does not match the number of defined columns.")
            record_dict = dict(zip(self.columns, record))
            self.records.append(record_dict)
            for col, value in record_dict.items():
                if value not in self.indexed_data[col]:
                    self.indexed_data[col][value] = []
                self.indexed_data[col][value].append(record_dict)


        self.records.sort(key=lambda x: x[self.columns[0]])

    def binary_search(self, what, in_column):
        left, right = 0, len(self.records) - 1
        while left <= right:
            mid = (left + right) // 2
            mid_value = self.records[mid][in_column]
            if mid_value == what:
                return [self.records[mid]]
            elif mid_value < what:
                left = mid + 1
            else:
                right = mid - 1
        return []

    def update(self, row_number, data):
        if row_number < 1 or row_number > len(self.records):
            raise ValueError("Row number out of range.")
        if len(data) != len(self.columns):
            raise ValueError("Data does not match the number of columns.")


        old_record = self.records[row_number - 1]
        for col, value in old_record.items():
            self.indexed_data[col][value].remove(old_record)

        new_record = dict(zip(self.columns, data))
        self.records[row_number - 1] = new_record

        for col, value in new_record.items():
            if value not in self.indexed_data[col]:
                self.indexed_data[col][value] = []
            self.indexed_data[col][value].append(new_record)

    def delete(self, row_number):
        if row_number < 1 or row_number > len(self.records):
            raise ValueError("Row number out of range.")

        record_to_delete = self.records.pop(row_number - 1)
        for col, value in record_to_delete.items():
            self.indexed_data[col][value].remove(record_to_delete)
            if not self.indexed_data[col][value]:
                del self.indexed_data[col][value]

    def to_dict(self):
        return {'columns': self.columns, 'records': self.records}

    def from_dict(self, data):
        self.columns = data['columns']
        self.records = data['records']
        self.indexed_data = {col: {} for col in self.columns}
        for record in self.records:
            for col, value in record.items():
                if value not in self.indexed_data[col]:
                    self.indexed_data[col][value] = []
                self.indexed_data[col][value].append(record)


class ElementalDB:
    def __init__(self):
        self.tables = {}
        self.memory_cache = {}
        self.relations = {}

    def table_create(self, name, columns, overwrite=False):
        if name in self.tables and not overwrite:
            return self.tables[name]
        table = Table(name, columns)
        self.tables[name] = table
        return table

    def save_table(self, table_name):
        if table_name in self.tables:
            table = self.tables[table_name]
            file_path = f'database/{table_name}.bson'
            if not os.path.exists('database'):
                os.makedirs('database')
            with open(file_path, 'wb') as f:
                f.write(bson.encode(table.to_dict()))

    def load_table(self, table_name):
        file_path = f'database/{table_name}.bson'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = bson.decode(f.read())
                table = Table(table_name, data['columns'])
                table.from_dict(data)
                self.tables[table_name] = table
        else:
            self.tables[table_name] = Table(table_name)

    def search(self, table_name, what, in_column):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        table = self.tables[table_name]

        start_time = time.time()
        results = table.binary_search(what, in_column)
        query_time = time.time() - start_time

        print(f"Query time for '{what}' in '{table_name}': {query_time:.6f} seconds")
        return results

    def add(self, table_name, records):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        table = self.tables[table_name]
        table.add_records(records)
        self.memory_cache[table_name] = table.records
        self.save_table(table_name)

    def update(self, table_name, row_number, data):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        table = self.tables[table_name]
        table.update(row_number, data)
        self.memory_cache[table_name] = table.records
        self.save_table(table_name)

    def delete(self, table_name, row_number):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist.")
        table = self.tables[table_name]
        deleted_record = table.records[row_number - 1]
        table.delete(row_number)
        self.memory_cache[table_name] = table.records
        self.save_table(table_name)

        self.handle_relation_delete(table_name, deleted_record)

    def relate(self, from_table, to_table, on_change='restrict'):
        if from_table not in self.tables or to_table not in self.tables:
            raise ValueError("Both tables must exist to create a relation.")

        self.relations[from_table] = {
            'to_table': to_table,
            'on_change': on_change
        }

    def handle_relation_delete(self, from_table, deleted_record):
        if from_table in self.relations:
            relation = self.relations[from_table]
            to_table_name = relation['to_table']
            to_table = self.tables[to_table_name]

            if relation['on_change'] == 'cascade':
                to_table.records = [
                    record for record in to_table.records if record['username'] != deleted_record['username']
                ]
                self.save_table(to_table_name)

            elif relation['on_change'] == 'restrict':
                print(f"Restrict: Related records in '{to_table_name}' are not deleted.")
