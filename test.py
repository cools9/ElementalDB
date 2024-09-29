from ElementalDB import *
import time
db = ElementalDB()

start=time.time()

# Create tables for users and favorite numbers
users = db.table_create("users", columns=["username", "password", "email"])
favorite_number = db.table_create("favorite_number", columns=["username", "fav_num"])

# Add some records to both tables
db.add('users', [["john_doe", "securepass", "john@example.com"],
                  ["jane_smith", "mypassword", "jane@example.com"]])

db.add('favorite_number', [["john_doe", 7],
                            ["jane_smith", 42]])

# Relate users and favorite_number with cascade behavior
db.relate(from_table="users", to_table="favorite_number", on_change='cascade')

# Check initial records
print("Initial records in 'users':", db.tables['users'].records)
print("Initial records in 'favorite_number':", db.tables['favorite_number'].records)

# Update a user's email
db.update('users', row_number=1, data=["john_doe", "new_securepass", "john_new@example.com"])
print("Updated records in 'users':", db.tables['users'].records)

# Delete a user and cascade the deletion in 'favorite_number'
db.delete('users', row_number=1)

# Check the favorite_number table after the cascade deletion
print("Records in 'favorite_number' after deleting 'john_doe':", db.tables['favorite_number'].records)

# Now, let's relate the users with restrict behavior
db.relate(from_table="users", to_table="favorite_number", on_change='restrict')

# Add 'john_doe' back into the 'users' table
db.add('users', [["john_doe", "securepass", "john@example.com"]])

# Attempt to delete 'john_doe' and check the related 'favorite_number'
db.delete('users', row_number=1)

# Check the favorite_number table after the restrict deletion
print("Records in 'favorite_number' after attempting to delete 'john_doe' with restrict:", db.tables['favorite_number'].records)

end=time.time()

print(f"Total execution time: {end - start:.6f} seconds")
