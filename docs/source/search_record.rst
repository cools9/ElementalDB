search
======

**Syntax:**

.. code-block:: python

    search(table_name, what, in_column)

Searches for a specific value in the given column.

**Parameters:**

- `table_name`: Name of the table (string).
- `what`: The value to search for (string).
- `in_column`: The column to search in (string).

**Example:**

.. code-block:: python

    db = ElementalDB()
    results = await db.search("users", "john_doe", "username")
    print(results)
