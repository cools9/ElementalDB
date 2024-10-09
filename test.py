from ElementalDB import ElementalDB
import asyncio
import time

async def example_usage():
    # Initialize the database
    db = ElementalDB()

    # Create a new table 'test_table' with a schema: name (string), age (int)
    db.create_table("test_table", schema=[('name', 'string'), ('age', 'int')])

    # Add some records to the 'test_table'
    record1 = {"id": 1, "name": "Alice", "age": 25}
    record2 = {"id": 2, "name": "Bob", "age": 30}
    record3 = {"id": 3, "name": "Charlie", "age": 35}

    await db.add("test_table", data=[record1["name"], record1["age"]])
    await db.add("test_table", data=[record2["name"], record2["age"]])
    await db.add("test_table", data=[record3["name"], record3["age"]])

    # Retrieve a record with ID 2
    record = await db.get("test_table", "name", "Bob")
    print(f"Retrieved record: {record}")

    # Update the record where the ID is 2 (Bob)
    updated_record = {"id": 2, "name": "Bob", "age": 31}
    await db.update("test_table", 2, updated_record)
    print(f"Updated record: {await db.get('test_table', 'name', 'Bob')}")

    # Delete the record where the ID is 1 (Alice)
    await db.delete("test_table", data=[1])
    print(f"Record 1 after deletion: {await db.get('test_table', 'name', 'Alice')}")

# Measure time and run the example
start = time.time()
asyncio.run(example_usage())
print(f"Execution time: {time.time() - start:.4f} seconds")
