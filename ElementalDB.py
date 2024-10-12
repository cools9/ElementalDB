import os
import orjson
import random
import string
import cachetools

class ElementalDB:
    def __init__(self, db_dir="db", map_file="map.map"):
        self.db_dir = db_dir
        self.map_file = map_file
        self.shards = {}
        self.BTREE_DEGREE = 2
        self.btrees = {}
        # this attributes to handle unique ID generation
        self.data = []
        self.next_id = 1

        self.cache = cachetools.LRUCache(maxsize=100)

        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.shard_map = self.load_map()

    def load_map(self):
        if os.path.exists(self.map_file):
            with open(self.map_file, "rb") as file:
                return orjson.loads(file.read())
        return {}

    def save_map(self):
        with open(self.map_file, "wb") as file:
            file.write(orjson.dumps(self.shard_map))

    def get_shard(self, table_name):
        shard_id = hash(table_name) % 3 + 1
        shard_name = f"shard_{shard_id}.json"
        shard_path = os.path.join(self.db_dir, shard_name)

        if shard_name not in self.shards:
            self.shards[shard_name] = shard_path

        if not os.path.exists(shard_path):
            with open(shard_path, "wb") as f:
                f.write(orjson.dumps([]))

        return shard_path

    def create_table(self, table_name, schema=[]):
        self.shard_map[table_name] = schema
        self.save_map()

    async def add(self, table_name, data=[]):
        shard_path = self.get_shard(table_name)
        record = {}

        schema = self.shard_map.get(table_name)
        if not schema:
            print(f"No schema found for table {table_name}")
            return

        if isinstance(data, list) and len(data) == len(schema):
            record = {col[0]: data[i] for i, col in enumerate(schema)}

        if 'id' not in record:
            record_id = self.next_id
            record['id'] = record_id
            self.data.append(record)
            self.next_id += 1
            return record_id

        self.cache[f"{table_name}_{record['id']}"] = record

        with open(shard_path, "rb+") as file:
            try:
                records = orjson.loads(file.read())
            except orjson.JSONDecodeError:
                records = []

            records.append(record)
            file.seek(0)
            file.write(orjson.dumps(records))
            file.truncate()

    async def get(self, table_name, column_name, value):
        shard_path = self.get_shard(table_name)
        cache_key = f"{table_name}_{value}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        with open(shard_path, "rb") as file:
            try:
                records = orjson.loads(file.read())
            except orjson.JSONDecodeError:
                return None

            for record in records:
                if record.get(column_name) == value:
                    self.cache[cache_key] = record
                    return record
        return None

    async def update(self, table_name, record_id, updated_data):
        shard_path = self.get_shard(table_name)

        with open(shard_path, "rb+") as file:
            try:
                records = orjson.loads(file.read())
            except orjson.JSONDecodeError:
                return None

            record_found = False
            for record in records:
                if record.get('id') == record_id:
                    record_found = True
                    record.update(updated_data)
                    break

            if not record_found:
                print(f"Record with id {record_id} not found.")
                return None

            file.seek(0)
            file.write(orjson.dumps(records))
            file.truncate()

            cache_key = f"{table_name}_{record_id}"
            if cache_key in self.cache:
                self.cache[cache_key].update(updated_data)

            print(f"Record with id {record_id} updated.")

    async def delete(self, table_name, data):
        shard_path = self.get_shard(table_name)

        with open(shard_path, "rb+") as file:
            try:
                records = orjson.loads(file.read())
            except orjson.JSONDecodeError:
                return None

            # Get the schema columns (names only)
            schema_columns = [col[0] for col in self.shard_map[table_name]]

            # If data is a list (e.g., ['Alice', 30]), delete the matching records
            if isinstance(data, list):
                if len(data) != len(schema_columns):
                    print("Data list does not match schema length.")
                    return

                # Perform deletion based on matching column values
                records = [
                    record for record in records
                    if not all(record.get(col) == val for col, val in zip(schema_columns, data))
                ]
            elif isinstance(data, int):
                if 0 <= data < len(records):
                    del records[data]
                else:
                    print("Invalid row number")
                    return

            file.seek(0)
            file.write(orjson.dumps(records))
            file.truncate()

            print(f"Record {data} deleted from table '{table_name}'")

    def print_all(self, table_name):
        shard_path = self.get_shard(table_name)
        with open(shard_path, "rb") as file:
            try:
                records = orjson.loads(file.read())
                for record in records:
                    print(record)
            except orjson.JSONDecodeError:
                print(f"No records found for table {table_name}")
