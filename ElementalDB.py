import os
import json
import random
import string
import asyncio
import bisect

class ElementalDB:
    """
    A sharded, JSON-based database implementation with write-ahead logging and buffered writes.
    
    This database distributes data across multiple shards for better performance and scalability.
    It uses a write-ahead log (WAL) and buffered writes to optimize write operations, and
    binary search for efficient read operations.

    Attributes:
        db_dir (str): Directory where database files are stored
        map_file (str): File that stores the mapping of tables to shards
        shards (dict): In-memory cache of active shards
        buffered_records (dict): Buffers for each shard
        BATCH_SIZE (int): Number of records to accumulate before writing to disk
        WAL_BUFFER (dict): Write-ahead log buffer for crash recovery

    Args:
        db_dir (str, optional): Directory for database files. Defaults to "db".
        map_file (str, optional): Name of the mapping file. Defaults to "map.map".
    """

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

    def load_map(self):
        """
        Loads the shard mapping from disk.
        
        Returns:
            dict: A dictionary containing the table-to-shard mapping. If the map file
                  doesn't exist, returns an empty dictionary.
        """
        # Load the map file to track which shard stores what
        if os.path.exists(self.map_file):
            with open(self.map_file, "r") as file:
                return json.load(file)
        return {}

    def save_map(self):
        """
        Saves the current shard mapping to disk.
        
        This ensures persistence of the table-to-shard mapping between database sessions.
        """
        # Save the map back to the file
        with open(self.map_file, "w") as file:
            json.dump(self.shard_map, file)

    def get_shard(self, table_name):
        """
        Determines and returns the appropriate shard for a given table.
        
        Args:
            table_name (str): Name of the table to get the shard for.
            
        Returns:
            str: Path to the shard file for the given table.
            
        Note:
            If the shard doesn't exist, it will be created as an empty JSON file.
        """
        # Get the appropriate shard for a given table
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

    async def add(self, table_name: str, record: dict):
        """
        Adds a record to the specified table.
        
        This method uses buffering and write-ahead logging for efficient writes.
        Records are written to disk when the buffer reaches BATCH_SIZE.
        
        Args:
            table_name (str): Name of the table to add the record to.
            record (dict): The record to add. Should be a dictionary.
            
        Note:
            This method is asynchronous and may not write to disk immediately.
        """
        shard_path = self.get_shard(table_name)

        # Buffer records in memory first
        if shard_path not in self.buffered_records:
            self.buffered_records[shard_path] = []

        # Add record to the WAL (Write-ahead log) buffer
        self.WAL_BUFFER.setdefault(shard_path, []).append(record)

        # Flush the buffer to disk when it reaches batch size
        if len(self.WAL_BUFFER[shard_path]) >= self.BATCH_SIZE:
            await self.flush(shard_path)

    async def flush(self, shard_path):
        """
        Flushes buffered records to disk in sorted order.
        
        Args:
            shard_path (str): Path to the shard file to flush records to.
            
        Note:
            This method uses binary insertion sort to maintain sorted order of records.
            If a JSON decode error occurs, the shard file will be reset.
        """
        # Efficiently flush buffered records to disk in sorted order
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

    async def get(self, table_name: str, record_id: int):
        """
        Retrieves a record by ID from the specified table.
        
        Args:
            table_name (str): Name of the table to retrieve the record from.
            record_id (int): ID of the record to retrieve.
            
        Returns:
            dict: The requested record if found, None otherwise.
            
        Note:
            This method uses binary search for efficient retrieval.
        """
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

    async def update(self, table_name: str, record_id: int, updated_record: dict):
        """
        Updates a record by ID in the specified table.
        
        Args:
            table_name (str): Name of the table containing the record.
            record_id (int): ID of the record to update.
            updated_record (dict): New data for the record.
            
        Note:
            This method uses binary search to find the record to update.
        """
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

    async def delete(self, table_name: str, record_id: int):
        """
        Deletes a record by ID from the specified table.
        
        Args:
            table_name (str): Name of the table containing the record.
            record_id (int): ID of the record to delete.
            
        Note:
            This method uses binary search to find the record to delete.
        """
        shard_path = self.get_shard(table_name)

        with open(shard_path, "r+") as file:
            records = json.load(file)
            # Use binary search to find and remove the record
            index = bisect.bisect_left([record['id'] for record in records], record_id)
            if index < len(records) and records[index]['id'] == record_id:
                records.pop(index)
                file.seek(0)
                json.dump(records, file)

    def random_string(self, length=10):
        """
        Generates a random string of specified length.
        
        Args:
            length (int, optional): Length of the string to generate. Defaults to 10.
            
        Returns:
            str: A random string containing ASCII letters.
        """
        # Helper function: Generate a random string of fixed length
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))