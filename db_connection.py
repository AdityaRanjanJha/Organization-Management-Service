from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, ClassVar
from config import MONGODB_URL, MASTER_DB_NAME


class Database:
    client: ClassVar[Optional[AsyncIOMotorClient]] = None
    
    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(MONGODB_URL)
        print(f"Connected to MongoDB: {MONGODB_URL.split('@')[1] if '@' in MONGODB_URL else MONGODB_URL}")
    
    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        if not cls.client:
            raise Exception("Database not connected")
        return cls.client[MASTER_DB_NAME]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        db = cls.get_database()
        return db[collection_name]
    
    @classmethod
    def get_org_collection(cls, org_name: str):
        collection_name = f"org_{org_name.lower().replace(' ', '_')}"
        return cls.get_collection(collection_name)


def get_database():
    return Database.get_database()

def get_org_collection(org_name: str):
    return Database.get_org_collection(org_name)
