import orjson
import os
import hashlib

class ElementalDB:
    def __init__(self, db_directory, auth=False):
        self.db_directory = db_directory
        self.tables = {}
        self.auth_enabled = auth
        self.load_tables()
        self.auth_file = os.path.join(self.db_directory, 'auth.auth')
        self.users = {}
        if self.auth_enabled:
            self.load_auth()

    def load_tables(self):
        if not os.path.exists(self.db_directory):
            os.makedirs(self.db_directory)

        for filename in os.listdir(self.db_directory):
            if filename.endswith('.json'):
                with open(os.path.join(self.db_directory, filename), 'rb') as f:
                    table_name = filename[:-5]
                    self.tables[table_name] = orjson.loads(f.read())

    def save_table(self, table_name):
        table = self.tables[table_name]
        fullpath = os.path.normpath(os.path.join(self.db_directory, f'{table_name}.json'))
        if not fullpath.startswith(self.db_directory):
            raise Exception("Invalid table name")
        with open(fullpath, 'wb') as f:
            f.write(orjson.dumps(table))

    def create_table(self, table_name, columns, foreign_keys=None):
        if table_name in self.tables:
            raise ValueError(f"Table {table_name} already exists")

        self.tables[table_name] = {
            'columns': columns,
            'rows': [],
            'foreign_keys': foreign_keys if foreign_keys else {}
        }
        self.save_table(table_name)  # Save the newly created table

    def load_auth(self):
        if os.path.exists(self.auth_file):
            with open(self.auth_file, 'rb') as f:
                self.users = orjson.loads(f.read())

    def save_auth(self):
        with open(self.auth_file, 'wb') as f:
            f.write(orjson.dumps(self.users))

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self, username, password):
        if username in self.users:
            raise ValueError(f"User {username} already exists")

        self.users[username] = self.hash_password(password)
        self.save_auth()

    def authenticate(self, username, password):
        hashed_password = self.hash_password(password)
        if username in self.users and self.users[username] == hashed_password:
            return True
        return False

    async def add(self, table_name, columns, values):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        table = self.tables[table_name]

        if len(columns) != len(values):
            raise ValueError("Columns and values must match in number")

        row_id = len(table['rows']) + 1
        new_row = {col: val for col, val in zip(columns, values)}
        new_row['id'] = row_id

        for fk_column, ref_table in table['foreign_keys'].items():
            if fk_column in columns:
                ref_value = new_row[fk_column]
                if not any(row['id'] == ref_value for row in self.tables[ref_table]['rows']):
                    raise ValueError(f"Foreign key constraint failed for {fk_column}: {ref_value} does not exist in {ref_table}")

        table['rows'].append(new_row)
        self.save_table(table_name)

    async def get(self, table_name):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        return self.tables[table_name]['rows']

    async def update(self, table_name, row_id, updates):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        table = self.tables[table_name]
        row = next((row for row in table['rows'] if row['id'] == row_id), None)

        if row is None:
            raise ValueError(f"Row with id {row_id} does not exist in {table_name}")

        for key, value in updates.items():
            if key in table['columns']:
                if key in table['foreign_keys']:
                    ref_table = table['foreign_keys'][key]
                    if not any(ref_row['id'] == value for ref_row in self.tables[ref_table]['rows']):
                        raise ValueError(f"Foreign key constraint failed for {key}: {value} does not exist in {ref_table}")
                row[key] = value
            else:
                raise ValueError(f"Column {key} does not exist in {table_name}")

        self.save_table(table_name)

    async def delete(self, table_name, row_id):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        table = self.tables[table_name]
        row = next((row for row in table['rows'] if row['id'] == row_id), None)

        if row is None:
            raise ValueError(f"Row with id {row_id} does not exist in {table_name}")

        for fk_col, ref_table in table['foreign_keys'].items():
            for ref_row in self.tables[ref_table]['rows']:
                if ref_row[fk_col] == row_id:
                    raise ValueError(f"Cannot delete row with id {row_id} in {table_name} because it is referenced in {ref_table}")

        table['rows'].remove(row)
        self.save_table(table_name)

    async def delete_cascade(self, table_name, column_name, value):
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")

        rows_to_delete = [row for row in self.tables[table_name]['rows'] if row[column_name] == value]
        for row in rows_to_delete:
            self.tables[table_name]['rows'].remove(row)

        for fk_col, ref_table in self.tables[table_name]['foreign_keys'].items():
            for ref_row in self.tables[ref_table]['rows']:
                if ref_row[fk_col] == value:
                    self.tables[ref_table]['rows'].remove(ref_row)

        self.save_table(table_name)
