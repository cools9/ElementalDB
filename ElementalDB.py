import os
import json
import random
import string
import asyncio
import bisect

class ElementalDB:
    def __init__(self, db_dir="db", map_file="map.map"):
        self.db_dir = db_dir
        self.map_file = map_file
        self.shards = {}  # In-memory cache of active shards
        self.buffered_records = {}  # Buffers for each shard
        self.BATCH_SIZE = 500  # Efficient batch size
        self.WAL_BUFFER = {}  # Write-ahead log buffer

        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Load the map
        self.shard_map = self.load_map()

    # Load the map file to track which shard stores what
    def load_map(self):
        if os.path.exists(self.map_file):
            with open(self.map_file, "r") as file:
                return json.load(file)
        return {}

    # Save the map back to the file
    def save_map(self):
        with open(self.map_file, "w") as file:
            json.dump(self.shard_map, file)

    # Get the appropriate shard for a given table
    def get_shard(self, table_name):
        shard_id = hash(table_name) % 3 + 1  # Using modulo to distribute across 3 shards
        shard_name = f"shard_{shard_id}.json"
        shard_path = os.path.join(self.db_dir, shard_name)

        if shard_name not in self.shards:
            self.shards[shard_name] = shard_path

        # Ensure the shard file exists
        if not os.path.exists(shard_path):
            with open(shard_path, "w") as f:
                json.dump([], f)  # Initialize an empty list

        return shard_path

    # Add a record to a table
    async def add(self, table_name: str, record: dict):
        shard_path = self.get_shard(table_name)

        # Buffer records in memory first
        if shard_path not in self.buffered_records:
            self.buffered_records[shard_path] = []

        # Add record to the WAL (Write-ahead log) buffer
        self.WAL_BUFFER.setdefault(shard_path, []).append(record)

        # Flush the buffer to disk when it reaches batch size
        if len(self.WAL_BUFFER[shard_path]) >= self.BATCH_SIZE:
            await self.flush(shard_path)

    # Efficiently flush buffered records to disk in sorted order
    async def flush(self, shard_path):
        if shard_path in self.WAL_BUFFER and len(self.WAL_BUFFER[shard_path]) > 0:
            records_to_write = self.WAL_BUFFER[shard_path]
            try:
                with open(shard_path, "r+") as file:
                    existing_records = json.load(file)

                    # Insert new records in sorted order using binary search
                    for record in records_to_write:
                        bisect.insort_left(existing_records, record, key=lambda x: x['id'])

                    file.seek(0)
                    json.dump(existing_records, file)

                # Clear the WAL buffer after successful flush
                self.WAL_BUFFER[shard_path] = []
            except json.JSONDecodeError:
                # In case of JSON decode error, clear the file and rewrite valid data
                with open(shard_path, "w") as file:
                    json.dump([], file)
                print(f"File {shard_path} was corrupted. Cleared and reset.")

    # Retrieve a record by ID
    async def get(self, table_name: str, record_id: int):
        shard_path = self.get_shard(table_name)

        try:
            with open(shard_path, "r") as file:
                records = json.load(file)
                # Use binary search to find the record
                index = bisect.bisect_left([record['id'] for record in records], record_id)
                if index < len(records) and records[index]['id'] == record_id:
                    return records[index]
        except json.JSONDecodeError:
            print(f"Error reading file {shard_path}. File might be corrupted.")
        return None

    # Update a record by ID
    async def update(self, table_name: str, record_id: int, updated_record: dict):
        shard_path = self.get_shard(table_name)

        with open(shard_path, "r+") as file:
            records = json.load(file)
            # Use binary search to find the record
            index = bisect.bisect_left([record['id'] for record in records], record_id)
            if index < len(records) and records[index]['id'] == record_id:
                records[index] = updated_record
                file.seek(0)
                json.dump(records, file)
                return
        print(f"Record {record_id} not found in table {table_name}")

    # Delete a record by ID
    async def delete(self, table_name: str, record_id: int):
        shard_path = self.get_shard(table_name)

        with open(shard_path, "r+") as file:
            records = json.load(file)
            # Use binary search to find and remove the record
            index = bisect.bisect_left([record['id'] for record in records], record_id)
            if index < len(records) and records[index]['id'] == record_id:
                records.pop(index)
                file.seek(0)
                json.dump(records, file)

    # Helper function: Generate a random string of fixed length
    def random_string(self, length=10):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
