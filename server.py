from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from ElementalDB import ElementalDB

app = FastAPI()
db = ElementalDB('database', auth=True)  # Set auth=True if authentication is needed

class Item(BaseModel):
    """
    Schema for adding an item to a table in the database.

    Attributes:
        table_name (str): The name of the table to which the item will be added.
        columns (list): The list of column names corresponding to the values.
        values (list): The list of values to be added to the specified columns.
    """
    table_name: str
    columns: list
    values: list

class UpdateItem(BaseModel):
    """
    Schema for updating an existing item in a table.

    Attributes:
        table_name (str): The name of the table where the item resides.
        row_id (int): The unique identifier of the row to be updated.
        updates (dict): A dictionary of column-value pairs representing the updates.
    """
    table_name: str
    row_id: int
    updates: dict

@app.post("/add")
async def add_item(item: Item):
    """
    Add a new item to a specified table in the database.

    Args:
        item (Item): The item to be added, containing table name, columns, and values.

    Returns:
        dict: A success message if the item is added successfully.

    Raises:
        HTTPException: If there is an error during the addition of the item.
    """
    try:
        await db.add(item.table_name, item.columns, item.values)
        return {"message": "Item added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get/{table_name}")
async def get_items(table_name: str):
    """
    Retrieve all items from a specified table in the database.

    Args:
        table_name (str): The name of the table from which to retrieve items.

    Returns:
        list: A list of items in the specified table.

    Raises:
        HTTPException: If the table does not exist or if an error occurs during retrieval.
    """
    try:
        items = await db.get(table_name)
        return items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/delete/{table_name}/{id}")
async def delete_item(table_name: str, id: int):
    """
    Delete a specific item from a table by its ID.

    Args:
        table_name (str): The name of the table from which to delete the item.
        id (int): The unique identifier of the item to be deleted.

    Returns:
        dict: A success message if the item is deleted successfully.

    Raises:
        HTTPException: If the item does not exist or if an error occurs during deletion.
    """
    try:
        await db.delete(table_name, id)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/update")
async def update_item(update_item: UpdateItem):
    """
    Update a specific item in a table by its ID.

    Args:
        update_item (UpdateItem): The item update information containing table name, row ID, and updates.

    Returns:
        dict: A success message if the item is updated successfully.

    Raises:
        HTTPException: If the item does not exist, the column does not exist, or an error occurs during the update.
    """
    try:
        await db.update(update_item.table_name, update_item.row_id, update_item.updates)
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
