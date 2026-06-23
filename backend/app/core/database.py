from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI

_db_client: AsyncIOMotorClient = None
_database = None

async def connect_db():
    """Connect to MongoDB."""
    global _db_client, _database
    _db_client = AsyncIOMotorClient(MONGO_URI)
    _database = _db_client.get_default_database()
    print(f"✔ Connected to MongoDB: {_database.name}")

async def close_db():
    """Close MongoDB connection."""
    global _db_client
    if _db_client:
        _db_client.close()
        print("✔ MongoDB connection closed.")

def get_database():
    """Returns the MongoDB database instance. Used by routes and middleware."""
    return _database
