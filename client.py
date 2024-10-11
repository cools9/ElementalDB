import requests
from typing import Any, List, Dict
import time
from auth import User

class ElementalDBClient:
    """
    A client for interacting with the ElementalDB FastAPI server.

    Provides methods to perform CRUD operations (Create, Read, Update, Delete)
    on tables stored in the ElementalDB backend.

    Attributes:
        base_url (str): The base URL of the ElementalDB API server.
        timeout (int): The default timeout for HTTP requests.
    """

    def __init__(self, base_url: str, timeout: int = 5) -> None:
        """
        Initializes the ElementalDBClient with the specified base URL.

        Args:
            base_url (str): The base URL of the ElementalDB API server.
            timeout (int, optional): The timeout for HTTP requests in seconds. Defaults to 5 seconds.
        """
        self.base_url = base_url
        self.timeout = timeout

    def add_item(self, table_name: str, columns: List[str], values: List[Any]) -> Dict:
        """
        Adds a new item to the specified table in the database.

        Args:
            table_name (str): Name of the table where the item should be added.
            columns (List[str]): List of column names for the table.
            values (List[Any]): List of values corresponding to the columns.

        Returns:
            Dict: The response from the server containing the status or result of the addition.
        """
        try:
            response = requests.post(f"{self.base_url}/add", json={
                "table_name": table_name,
                "columns": columns,
                "values": values  # Ensure values is a list, not a dictionary
            }, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_items(self, table_name: str) -> Dict:
        """
        Retrieves all items from the specified table in the database.

        Args:
            table_name (str): Name of the table to fetch items from.

        Returns:
            Dict: The response from the server containing a list of items in the table.
        """
        try:
            response = requests.get(f"{self.base_url}/get/{table_name}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_item(self, table_name: str, id: int) -> Dict:
        """
        Deletes an item from the specified table based on its ID.

        Args:
            table_name (str): Name of the table from which the item should be deleted.
            id (int): ID of the item to delete.

        Returns:
            Dict: The response from the server confirming the deletion.
        """
        try:
            response = requests.delete(f"{self.base_url}/delete/{table_name}/{id}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        
    def signup(self, username: str, password: str, role: str):
        """ Requests to make a new user by the given arguments """

        try:
            response = requests.post(f"{self.base_url}/signup", json={
                #"requesterUser": self.currentUser,
                #"newUser": User()
            })
        except:
            pass

    def update_item(self, table_name: str, row_id: int, updates: Dict[str, Any]) -> Dict:
        """
        Updates an existing item in the specified table based on its ID.

        Args:
            table_name (str): Name of the table to update the item in.
            row_id (int): ID of the item to update.
            updates (Dict[str, Any]): Dictionary containing the columns and their new values.

        Returns:
            Dict: The response from the server confirming the update.
        """
        try:
            response = requests.put(f"{self.base_url}/update", json={
                "table_name": table_name,
                "row_id": row_id,
                "updates": updates  # Ensure updates is a dictionary with column-value pairs
            }, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

if __name__ == "__main__":
    """
    Demonstrates the usage of the ElementalDBClient by performing example CRUD operations.
    Measures the time taken for each operation and prints the results for verification.
    """
    start = time.time()
    client = ElementalDBClient("http://127.0.0.1:8000")

    table_name = "users"
    columns = ["id", "name", "email"]
    values = [1, "John Doe", "john@example.com"]

    # Add item to the table
    print("Adding item to the table...")
    add_response = client.add_item(table_name, columns, values)
    print("Add Response:", add_response)

    # Retrieve items from the table
    print("\nRetrieving items from the table...")
    get_response = client.get_items(table_name)
    print("Get Response:", get_response)

    # Update an existing item by ID
    row_id = 1
    updates = {"name": "John Smith", "email": "john.smith@example.com"}
    print("\nUpdating item with ID 1...")
    update_response = client.update_item(table_name, row_id, updates)
    print("Update Response:", update_response)

    # Retrieve updated item
    print("\nRetrieving updated item with ID 1...")
    updated_item = client.get_items(table_name)
    print("Updated Item:", updated_item)

    # Delete item by ID
    print("\nDeleting item with ID 1...")
    delete_response = client.delete_item(table_name, row_id)
    print("Delete Response:", delete_response)

    # Retrieve items again after deletion
    print("\nRetrieving items after deletion...")
    final_get_response = client.get_items(table_name)
    print("Final Get Response:", final_get_response)

    end = time.time()
    print(f"\nTotal Time for CRUD Operations: {end - start:.4f} seconds")
