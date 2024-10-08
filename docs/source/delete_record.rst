delete
======

**Syntax:**

.. code-block:: python

    delete(table_name, row_number)

Deletes a specific row from the table.

**Parameters:**

- `table_name`: Name of the table (string).
- `row_number`: The row number to delete (integer).

**Example:**

.. code-block:: python

    db = ElementalDB()
    await db.delete("users", row_number=1)
