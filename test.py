from ElementalDB import ElementalDB

async def example_usage():
    db = ElementalDB()

    record1 = {"id": 1, "name": "Alice", "age": 25}
    record2 = {"id": 2, "name": "Bob", "age": 30}
    record3 = {"id": 3, "name": "Charlie", "age": 35}

    await db.add("test_table", record1)
    await db.add("test_table", record2)
    await db.add("test_table", record3)

    record = await db.get("test_table", 2)
    print(f"Retrieved record: {record}")

    updated_record = {"id": 2, "name": "Bob", "age": 31}
    await db.update("test_table", 2, updated_record)
    print(f"Updated record: {await db.get('test_table', 2)}")

    await db.delete("test_table", 1)
    print(f"Record 1 after deletion: {await db.get('test_table', 1)}")

# Run the example
import asyncio
import time
start=time.time()
asyncio.run(example_usage())
print(time.time()-start)
