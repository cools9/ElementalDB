from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import uvicorn
from ElementalDB import ElementalDB
from pydantic import BaseModel
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    User,
    get_current_user
)
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, Depends, oauth2
from http import HTTPStatus
# Initialize FastAPI and the ElementalDB instance
app = FastAPI()
auth_enabled = True
db = ElementalDB('database', auth=auth_enabled)  # Initialize the database

@app.post("/signup")
async def signup(user: User):
    """
    Create a new user account.

    Args:
        user (UserCreate): The user information containing username and password.

    Returns:
        UserResponse: The created user information.

    Raises:
        HTTPException: If the username already exists or if there is a database error.
    """

    # Checks if user already exists
    existing_users = await db.get("USERS", filters={"username": user.username})
    if existing_users:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    user_record = {
        "username": user.username,
        "password": hashed_password,
        "role": "user"
    }

    try: 
        await db.add("USERS", user_record)
        created_users = await db.get("USERS", filters={"username": user.username})
        if not created_users:
            raise HTTPException(status_code=400, detail="Error retrieving created user")

        created_user = created_users[0]

        return User(id=created_user['id'], username=created_user['username'], role=created_user['role'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_enabled: bool = True):
    """
    Authenticate a user and return a JWT token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
        Token: The access token and token type.

    Raises:
        HTTPException: If authentication fails.
    """
    if auth_enabled:
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, 
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@app.post("/add")
async def add_item(table_name: str, columns: List[str], values: List[str], token: str = Depends(oauth2_scheme), auth_enabled: bool = True):
                                                                                # Error here   ∧∧∧∧∧∧∧∧∧∧∧∧∧
    """
    Add a new item to a specified table in the database.

    Args:
        table_name (str): The name of the table to add the item.
        columns (list): The list of column names corresponding to the values.
        values (list): The list of values to be added to the specified columns.

    Returns:
        dict: A success message if the item is added successfully.

    Raises:
        HTTPException: If there is an error during the addition of the item.
    """
    if len(columns) != len(values):
        raise HTTPException(status_code=422, detail="Columns and values length must match.")

    # Authorization checks
    if auth_enabled:
        user = await get_current_user(token)

    try:
        # Prepare a dictionary of column-value pairs
        record = dict(zip(columns, values))
        await db.add(table_name, record)  # Pass the record to the DB
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
        if not items:
            raise HTTPException(status_code=404, detail="Table not found or is empty")
        return items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/delete/{table_name}/{id}")
async def delete_item(table_name: str, id: int, token: str = Depends(oauth2_scheme), auth_enabled: bool = auth_enabled):
    #                                                  # Error here  ∧∧∧∧∧∧∧∧∧∧∧∧
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
    # Authorization checks
    if auth_enabled:
        user = await get_current_user(token)

    try:
        await db.delete(table_name, id)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/update")
async def update_item(table_name: str, row_id: int, updates: Dict[str, str], token: str = Depends(oauth2_scheme), auth_enabled: bool = auth_enabled):
    #                                                                               # Error Here  ∧∧∧∧∧∧∧∧∧∧∧∧
    """
    Update a specific item in a table by its ID.

    Args:
        table_name (str): The name of the table where the item resides.
        row_id (int): The unique identifier of the row to be updated.
        updates (dict): A dictionary of column-value pairs representing the updates.

    Returns:
        dict: A success message if the item is updated successfully.

    Raises:
        HTTPException: If the item does not exist, or if an error occurs during the update.
    """
    # Authorization checks
    if auth_enabled:
        user = await get_current_user(token)

    try:
        await db.update(table_name, row_id, updates)
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
