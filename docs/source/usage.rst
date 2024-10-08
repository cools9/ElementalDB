Usage Examples
==============

This section shows how to use ElementalDb with code examples.

Basic Usage
-----------

The following example demonstrates how to create a table, insert data, search, update, and delete records.

.. code-block:: python

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

