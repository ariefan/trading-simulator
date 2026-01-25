import asyncio
import asyncpg

async def list_tables():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/trading')
    rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    print("Tables in 'trading' database:")
    for row in rows:
        print(f"- {row['table_name']}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(list_tables())
