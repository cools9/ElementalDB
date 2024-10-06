from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from ElementalDB import ElementalDB

app = FastAPI()
db = ElementalDB('database', auth=True)  # Set auth=True if authentication is needed

class Item(BaseModel):
    table_name: str
    columns: list
    values: list

class UpdateItem(BaseModel):
    table_name: str
    row_id: int
    updates: dict

@app.post("/add")
async def add_item(item: Item):
    try:
        await db.add(item.table_name, item.columns, item.values)
        return {"message": "Item added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get/{table_name}")
async def get_items(table_name: str):
    try:
        items = await db.get(table_name)
        return items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/delete/{table_name}/{id}")
async def delete_item(table_name: str, id: int):
    try:
        await db.delete(table_name, id)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/update")
async def update_item(update_item: UpdateItem):
    try:
        await db.update(update_item.table_name, update_item.row_id, update_item.updates)
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
