import requests

class ElementalDBClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def add_item(self, table_name, columns, values):
        response = requests.post(f"{self.base_url}/add", json={
            "table_name": table_name,
            "columns": columns,
            "values": values
        })
        return response.json()

    def get_items(self, table_name):
        response = requests.get(f"{self.base_url}/get/{table_name}")
        return response.json()

    def delete_item(self, table_name, id):
        response = requests.delete(f"{self.base_url}/delete/{table_name}/{id}")
        return response.json()

    def update_item(self, table_name, row_id, updates):
        response = requests.put(f"{self.base_url}/update", json={
            "table_name": table_name,
            "row_id": row_id,
            "updates": updates
        })
        return response.json()

if __name__ == "__main__":
    import time
    start=time.time()
    client = ElementalDBClient("http://127.0.0.1:8000")
    # Example Usage
    print(client.add_item('users', ['username', 'password'], ['john_doe', 'secret']))
    print(client.get_items('users'))
    print(client.update_item('users', 1, {'password': 'new_secret'}))
    print(client.delete_item('users', 1))
    end=time.time()
    print(end-start)
