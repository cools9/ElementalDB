# ElementalDB

![ElementalDB Diagram](ElementalDB.jpg)

**ElementalDB** is a lightweight, easy-to-use database management system implemented in Python. It supports basic functionalities for creating, reading, updating, and deleting (CRUD) tables and their records, along with relationships between tables.

## Features

- **Table Creation**: Create tables with specified columns.
- **Record Management**: Add, update, and delete records in tables.
- **Binary Search**: Efficient searching for records based on indexed columns.
- **Data Persistence**: Save and load tables to/from BSON files for persistent storage.
- **Relations**: Create relationships between tables with options for cascading or restricting actions on related records.

## Requirements

- Python 3.x
- `orjson` library (install using `pip install orjson`)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/cools9/ElementalDB
   ```

2. Navigate into the project directory:

   ```bash
   cd ElementalDB
   ```

3. Install the required dependencies:

   ```bash
   pip install orjson
   ```

## Usage

Here’s a basic example of how to use ElementalDB:

```python
import asyncio
from elementaldb import ElementalDB  # Make sure to import your ElementalDB class

async def main():
    db = ElementalDB()
    await db.table_create("users", columns=["username", "password", "email"])
    await db.add('users', [["john_doe", "securepass", "john@example.com"],
                            ["jane_smith", "mypassword", "jane@example.com"]])

    # Search for a user
    results = await db.search('users', 'john_doe', 'username')
    print(results)

    # Update a user's information
    await db.update('users', row_number=1, data=["john_doe", "new_securepass", "john_new@example.com"])

    # Delete a user
    await db.delete('users', row_number=1)

# Run the async main function
asyncio.run(main())
```

## Functions Overview

- **`table_create(name, columns, overwrite=False)`**: Creates a new table with the specified name and columns.
- **`add(table_name, records)`**: Adds records to the specified table.
- **`update(table_name, row_number, data)`**: Updates a specific row in the table.
- **`delete(table_name, row_number)`**: Deletes a specific row from the table.
- **`search(table_name, what, in_column)`**: Searches for a specific value in the given column.
- **`relate(from_table, to_table, on_change='restrict')`**: Creates a relation between two tables with options for cascading or restricting deletes.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
