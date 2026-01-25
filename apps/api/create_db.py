import asyncio
import asyncpg
import os

async def create_db():
    try:
        # Use postgres user/pass for initial connection
        conn = await asyncpg.connect(user='postgres', password='postgres', database='postgres', host='localhost')
        try:
            await conn.execute('CREATE DATABASE trading')
            print("Database 'trading' created successfully.")
        except asyncpg.DuplicateDatabaseError:
            print("Database 'trading' already exists.")
        finally:
            await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_db())
