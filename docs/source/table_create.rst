table_create
============

**Syntax:**

.. code-block:: python

    table_create(name, columns, overwrite=False)

Creates a new table with the specified name and columns.

**Parameters:**

- `name`: Name of the table (string).
- `columns`: List of column names (list of strings).
- `overwrite`: Optional, whether to overwrite the table if it exists. Default is `False`.

**Example:**

.. code-block:: python

    db = ElementalDB()
    await db.table_create("users", columns=["username", "password", "email"], overwrite=True)
