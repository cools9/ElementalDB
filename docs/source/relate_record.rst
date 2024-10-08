relate
======

**Syntax:**

.. code-block:: python

    relate(from_table, to_table, on_change='restrict')

Creates a relation between two tables with options for cascading or restricting deletes.

**Parameters:**

- `from_table`: The table from which the relation starts (string).
- `to_table`: The table to which the relation goes (string).
- `on_change`: Specifies behavior when rows are deleted. Default is `'restrict'`, options are `'cascade'` and `'restrict'`.

**Example:**

.. code-block:: python

    db = ElementalDB()
    await db.relate("users", "orders", on_change="cascade")
