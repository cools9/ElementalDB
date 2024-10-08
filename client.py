import requests
from typing import Any

class ElementalDBClient:
    """
    A client for interacting with the ElementalDB FastAPI server.

    Provides methods to perform CRUD operations (Create, Read, Update, Delete) 
    on tables stored in the ElementalDB backend.

    Attributes:
        base_url (str): The base URL of the ElementalDB API server.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initializes the ElementalDBClient with the specified base URL.

        Args:
            base_url (str): The base URL of the ElementalDB API server.
        """
        self.base_url = base_url

    def add_item(self, table_name: str, columns: list[str], values: dict[str, Any]):
        """
        Adds a new item to the specified table in the database.

        Args:
            table_name (str): Name of the table where the item should be added.
            columns (list[str]): List of column names for the table.
            values (dict[str, Any]): Dictionary mapping columns to their respective values.

        Returns:
            dict: The response from the server containing the status or result of the addition.
        """
        response = requests.post(f"{self.base_url}/add", json={
            "table_name": table_name,
            "columns": columns,
            "values": values
        })
        return response.json()

    def get_items(self, table_name: str):
        """
        Retrieves all items from the specified table in the database.

        Args:
            table_name (str): Name of the table to fetch items from.

        Returns:
            dict: The response from the server containing a list of items in the table.
        """
        response = requests.get(f"{self.base_url}/get/{table_name}")
        return response.json()

    def delete_item(self, table_name: str, id: int):
        """
        Deletes an item from the specified table based on its ID.

        Args:
            table_name (str): Name of the table from which the item should be deleted.
            id (int): ID of the item to delete.

        Returns:
            dict: The response from the server confirming the deletion.
        """
        response = requests.delete(f"{self.base_url}/delete/{table_name}/{id}")
        return response.json()

    def update_item(self, table_name: str, row_id: int, updates: dict[str, Any]):
        """
        Updates an existing item in the specified table based on its ID.

        Args:
            table_name (str): Name of the table to update the item in.
            row_id (int): ID of the item to update.
            updates (dict[str, Any]): Dictionary containing the columns and their new values.

        Returns:
            dict: The response from the server confirming the update.
        """
        response = requests.put(f"{self.base_url}/update", json={
            "table_name": table_name,
            "row_id": row_id,
            "updates": updates
        })
        return response.json()

if __name__ == "__main__":
    """
    Demonstrates the usage of the ElementalDBClient by performing example CRUD operations.

    Measures the time taken for each operation and prints the results for verification.
    """
    import time

    start = time.time()
    client = ElementalDBClient("http://127.0.0.1:8000")
    
    # Example Usage
    print("Adding item to 'users' table...")
    print(client.add_item('users', ['username', 'password'], ['john_doe', 'secret']))

    print("Getting items from 'users' table...")
    print(client.get_items('users'))

    print("Updating item in 'users' table with ID 1...")
    print(client.update_item('users', 1, {'password': 'new_secret'}))

    print("Deleting item from 'users' table with ID 1...")
    print(client.delete_item('users', 1))

    end = time.time()
    print(f"Time taken for operations: {end - start} seconds")
