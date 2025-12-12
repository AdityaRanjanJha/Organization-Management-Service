from pydantic import BaseModel, EmailStr
from typing import Optional


class CreateOrgRequest(BaseModel):
    organization_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UpdateOrgRequest(BaseModel):
    organization_name: str
    new_organization_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class DeleteOrgRequest(BaseModel):
    organization_name: str
