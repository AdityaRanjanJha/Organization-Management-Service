from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
from bson import ObjectId
from db_connection import Database, get_database, get_org_collection
from db_models import *
from schemas import CreateOrgRequest, LoginRequest, UpdateOrgRequest, DeleteOrgRequest
import utils

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect()
    await initialize_indexes()
    yield
    await Database.disconnect()

app = FastAPI(
    title="Organization Management Service",
    description="Multi-tenant organization management with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_admin(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = utils.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/org/create")
async def create_organization(request: CreateOrgRequest):
    if await org_exists(request.organization_name):
        raise HTTPException(status_code=400, detail="Organization already exists")
    
    try:
        collection_name = f"org_{request.organization_name.lower().replace(' ', '_')}"
        org_doc = {
            "organization_name": request.organization_name,
            "collection_name": collection_name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        org_id = await create_org(org_doc)
        
        admin_doc = {
            "email": request.email,
            "hashed_password": utils.hash_password(request.password),
            "organization_id": org_id,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        admin_id = await create_admin(admin_doc)
        
        await update_org(org_id, {"admin_id": admin_id})
        
        org_collection = get_org_collection(request.organization_name)
        await org_collection.insert_one({
            "initialized": True,
            "created_at": datetime.utcnow()
        })
        
        return {
            "id": org_id,
            "organization_name": request.organization_name,
            "collection_name": collection_name,
            "admin_id": admin_id,
            "message": "Organization created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating organization: {str(e)}")

@app.get("/org/get")
async def get_organization(organization_name: str):
    org = await get_org_by_name(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return {
        "id": str(org["_id"]),
        "organization_name": org["organization_name"],
        "collection_name": org["collection_name"],
        "admin_id": org.get("admin_id"),
        "created_at": org["created_at"].isoformat(),
        "updated_at": org["updated_at"].isoformat()
    }

@app.put("/org/update")
async def update_organization(
    request: UpdateOrgRequest,
    admin: dict = Depends(get_current_admin)
):
    org = await get_org_by_name(request.organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    try:
        if request.new_organization_name and request.new_organization_name != request.organization_name:
            if await org_exists(request.new_organization_name):
                raise HTTPException(status_code=400, detail="New organization name already exists")
            
            old_collection = get_org_collection(request.organization_name)
            new_collection = get_org_collection(request.new_organization_name)
            
            documents = await old_collection.find().to_list(length=None)
            if documents:
                await new_collection.insert_many(documents)
            
            await old_collection.drop()
            
            new_collection_name = f"org_{request.new_organization_name.lower().replace(' ', '_')}"
            await update_org(str(org["_id"]), {
                "organization_name": request.new_organization_name,
                "collection_name": new_collection_name,
                "updated_at": datetime.utcnow()
            })
        
        if request.email or request.password:
            update_fields = {"updated_at": datetime.utcnow()}
            if request.email:
                update_fields["email"] = request.email
            if request.password:
                update_fields["hashed_password"] = utils.hash_password(request.password)
            
            await update_admin(org["admin_id"], update_fields)
        
        return {"message": "Organization updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating organization: {str(e)}")

@app.delete("/org/delete")
async def delete_organization(
    organization_name: str,
    admin: dict = Depends(get_current_admin)
):
    org = await get_org_by_name(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if org["admin_id"] != admin["admin_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        org_collection = get_org_collection(organization_name)
        await org_collection.drop()
        await delete_admin(org["admin_id"])
        await delete_org(str(org["_id"]))
        
        return {"message": f"Organization '{organization_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting organization: {str(e)}")

@app.post("/admin/login")
async def admin_login(request: LoginRequest):
    admin = await get_admin_by_email(request.email)
    if not admin or not utils.verify_password(request.password, admin["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not admin.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account inactive")
    
    token = utils.create_access_token({
        "admin_id": str(admin["_id"]),
        "organization_id": admin["organization_id"],
        "email": admin["email"]
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin_id": str(admin["_id"]),
        "organization_id": admin["organization_id"],
        "email": admin["email"]
    }

@app.get("/")
async def root():
    return {
        "message": "Organization Management Service",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    try:
        db = get_database()
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except:
        return {"status": "unhealthy", "database": "disconnected"}
