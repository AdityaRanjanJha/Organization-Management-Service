from typing import Optional, Dict, Any
from datetime import datetime
from db_connection import Database

ORGANIZATIONS_COLLECTION = "organizations"
ADMINS_COLLECTION = "admins"


async def org_exists(org_name: str) -> bool:
    collection = Database.get_collection(ORGANIZATIONS_COLLECTION)
    count = await collection.count_documents({"organization_name": org_name})
    return count > 0


async def get_org_by_name(org_name: str) -> Optional[Dict[str, Any]]:
    collection = Database.get_collection(ORGANIZATIONS_COLLECTION)
    return await collection.find_one({"organization_name": org_name})


async def create_org(org_data: Dict[str, Any]) -> str:
    collection = Database.get_collection(ORGANIZATIONS_COLLECTION)
    result = await collection.insert_one(org_data)
    return str(result.inserted_id)


async def update_org(org_id: str, update_data: Dict[str, Any]):
    from bson import ObjectId
    collection = Database.get_collection(ORGANIZATIONS_COLLECTION)
    await collection.update_one(
        {"_id": ObjectId(org_id)},
        {"$set": update_data}
    )


async def delete_org(org_id: str):
    from bson import ObjectId
    collection = Database.get_collection(ORGANIZATIONS_COLLECTION)
    await collection.delete_one({"_id": ObjectId(org_id)})


async def get_admin_by_email(email: str) -> Optional[Dict[str, Any]]:
    collection = Database.get_collection(ADMINS_COLLECTION)
    return await collection.find_one({"email": email})


async def create_admin(admin_data: Dict[str, Any]) -> str:
    collection = Database.get_collection(ADMINS_COLLECTION)
    result = await collection.insert_one(admin_data)
    return str(result.inserted_id)


async def update_admin(admin_id: str, update_data: Dict[str, Any]):
    from bson import ObjectId
    collection = Database.get_collection(ADMINS_COLLECTION)
    await collection.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": update_data}
    )


async def delete_admin(admin_id: str):
    from bson import ObjectId
    collection = Database.get_collection(ADMINS_COLLECTION)
    await collection.delete_one({"_id": ObjectId(admin_id)})


async def initialize_indexes():
    orgs_collection = Database.get_collection(ORGANIZATIONS_COLLECTION)
    await orgs_collection.create_index("organization_name", unique=True)
    await orgs_collection.create_index("collection_name", unique=True)
    
    admins_collection = Database.get_collection(ADMINS_COLLECTION)
    await admins_collection.create_index("email", unique=True)
    await admins_collection.create_index("organization_id")
    
    print("Database indexes created")
