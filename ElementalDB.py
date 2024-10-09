import os
import orjson  # Replaced json with orjson
import random
import string
import cachetools  # Import the cachetools library for caching

class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.children = []

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(leaf=True)
        self.t = t

    def search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node.keys[i]
        if node.leaf:
            return None
        return self.search(node.children[i], key)

    def insert(self, key):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            s = BTreeNode()
            s.children.append(root)
            self.split_child(s, 0)
            self.root = s
        self.insert_non_full(self.root, key)

    def insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self.insert_non_full(node.children[i], key)

    def split_child(self, node, i):
        t = self.t
        y = node.children[i]
        z = BTreeNode(leaf=y.leaf)
        node.children.insert(i + 1, z)
        node.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t:(2 * t - 1)]
        y.keys = y.keys[0:t - 1]

        if not y.leaf:
            z.children = y.children[t:(2 * t)]
            y.children = y.children[0:t]

class ElementalDB:
    def __init__(self, db_dir="db", map_file="map.map"):
        self.db_dir = db_dir
        self.map_file = map_file
        self.shards = {}
        self.WAL_BUFFER = {}
        self.BTREE_DEGREE = 2
        self.btrees = {}

        # Initialize the cache with a max size
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

    def get_btree(self, table_name):
        if table_name not in self.btrees:
            self.btrees[table_name] = BTree(t=self.BTREE_DEGREE)
        return self.btrees[table_name]

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

    async def add(self, table_name, record):
        shard_path = self.get_shard(table_name)
        btree = self.get_btree(table_name)
        btree.insert(record['id'])

        # Cache the record after adding it
        cache_key = f"{table_name}_{record['id']}"
        self.cache[cache_key] = record

        with open(shard_path, "rb+") as file:
            try:
                records = orjson.loads(file.read())
            except orjson.JSONDecodeError:
                records = []

            records.append(record)
            file.seek(0)
            file.write(orjson.dumps(records))
            file.truncate()

    async def get(self, table_name, record_id):
        # Check cache first
        cache_key = f"{table_name}_{record_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        shard_path = self.get_shard(table_name)
        btree = self.get_btree(table_name)
        result = btree.search(btree.root, record_id)

        if result is not None:
            with open(shard_path, "rb") as file:
                try:
                    records = orjson.loads(file.read())
                    for record in records:
                        if record['id'] == record_id:
                            # Cache the record for future access
                            self.cache[cache_key] = record
                            return record
                except orjson.JSONDecodeError:
                    return None
        return None

    async def update(self, table_name, record_id, updated_record):
        shard_path = self.get_shard(table_name)
        btree = self.get_btree(table_name)
        result = btree.search(btree.root, record_id)

        if result is not None:
            with open(shard_path, "rb+") as file:
                try:
                    records = orjson.loads(file.read())
                except orjson.JSONDecodeError:
                    records = []

                for i, record in enumerate(records):
                    if record['id'] == record_id:
                        records[i] = updated_record
                        file.seek(0)
                        file.write(orjson.dumps(records))
                        file.truncate()

                        # Update the cache with the new record
                        cache_key = f"{table_name}_{record_id}"
                        self.cache[cache_key] = updated_record
                        return
        print(f"Record {record_id} not found in table {table_name}")

    async def delete(self, table_name, record_id):
        shard_path = self.get_shard(table_name)
        btree = self.get_btree(table_name)
        result = btree.search(btree.root, record_id)

        if result is not None:
            with open(shard_path, "rb+") as file:
                try:
                    records = orjson.loads(file.read())
                    records = [record for record in records if record['id'] != record_id]
                    file.seek(0)
                    file.write(orjson.dumps(records))
                    file.truncate()

                    # Remove the record from cache
                    cache_key = f"{table_name}_{record_id}"
                    if cache_key in self.cache:
                        del self.cache[cache_key]

                except orjson.JSONDecodeError:
                    return None
