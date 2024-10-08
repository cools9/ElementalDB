from ElementalDB import ElementalDB
import asyncio

async def main():
    db = ElementalDB()

    table_name = "test_table"

    # Add records to the database
    print("Adding records to the table...")
    for i in range(10):
        record = {"id": i + 1, "data": db.random_string()}
        await db.add(table_name, record)

    # Retrieve and display a record
    print("Retrieving record with ID 5...")
    record = await db.get(table_name, 5)
    if record:
        print(f"Found record: {record}")
    else:
        print("Record not found.")

    # Update a record with ID 5
    print("Updating record with ID 5...")
    updated_record = {"id": 5, "data": "Updated Data"}
    await db.update(table_name, 5, updated_record)

    # Retrieve and display the updated record
    record = await db.get(table_name, 5)
    print(f"Updated record: {record}")

    # Delete a record with ID 5
    print("Deleting record with ID 5...")
    await db.delete(table_name, 5)

    # Try to retrieve the deleted record
    record = await db.get(table_name, 5)
    if record:
        print(f"Record found: {record}")
    else:
        print("Record deleted successfully.")

# Run the example
if __name__ == "__main__":
    import time
    start=time.time()
    asyncio.run(main())
    end=time.time()
    print(end-start)
