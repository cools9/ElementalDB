add
===

**Syntax:**

.. code-block:: python

    add(table_name, records)

Adds records to the specified table.

**Parameters:**

- `table_name`: Name of the table (string).
- `records`: List of records to be added (list of lists, where each sublist is a row).

**Example:**

.. code-block:: python

    db = ElementalDB()
    await db.add("users", [["john_doe", "securepass", "john@example.com"],
                           ["jane_smith", "mypassword", "jane@example.com"]])
