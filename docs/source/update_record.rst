update
======

**Syntax:**

.. code-block:: python

    update(table_name, row_number, data)

Updates a specific row in the table.

**Parameters:**

- `table_name`: Name of the table (string).
- `row_number`: The row number to update (integer).
- `data`: Updated data for the row (list of values).

**Example:**

.. code-block:: python

    db = ElementalDB()
    await db.update("users", row_number=1, data=["john_doe", "new_securepass", "john_new@example.com"])
