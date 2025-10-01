import asyncio
from db.database import init_db

async def main():
    await init_db()
    print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(main())
