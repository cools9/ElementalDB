import asyncio
from ElementalDB import ElementalDB

async def main():
    db = ElementalDB('database', auth=True)

    # Create the users table before adding users
    if 'users' not in db.tables:
        db.create_table('users', ['username', 'password'])

    # Signup
    try:
        db.signup('john_doe', 'secret')
        db.signup('jane_doe', 'password123')
    except ValueError as e:
        print(e)

    # Authenticate
    if db.authenticate('john_doe', 'secret'):
        print("Authentication successful for john_doe")

        # Add users only if they don't already exist
        users = await db.get('users')
        usernames = [user['username'] for user in users]

        if 'john_doe' not in usernames:
            await db.add('users', ['username', 'password'], ['john_doe', 'secret'])

        if 'jane_doe' not in usernames:
            await db.add('users', ['username', 'password'], ['jane_doe', 'password123'])

        print("Users:", await db.get('users'))
    else:
        print("Authentication failed for john_doe")

import time
start=time.time()
asyncio.run(main())
end=time.time()
print(end-start)
