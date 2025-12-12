# API Testing Guide

Test all endpoints using Postman.

## 1. Create Organization

`POST http://localhost:8000/org/create`

**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "organization_name": "MyCompany",
  "email": "admin@mycompany.com",
  "password": "test123"
}
```

---

## 2. Admin Login

`POST http://localhost:8000/admin/login`

**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "email": "admin@mycompany.com",
  "password": "test123"
}
```

**Response includes `access_token` - copy it for protected endpoints.**

---

## 3. Get Organization

`GET http://localhost:8000/org/get?organization_name=MyCompany`
---

## 4. Update Organization

`PUT http://localhost:8000/org/update`

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer YOUR_ACCESS_TOKEN`

**Body:**
```json
{
  "organization_name": "MyCompany",
  "new_organization_name": "MyCompanyRenamed",
  "email": "newemail@mycompany.com"
}
```

---

## 5. Delete Organization

`DELETE http://localhost:8000/org/delete?organization_name=MyCompanyRenamed`

**Headers:** `Authorization: Bearer YOUR_ACCESS_TOKEN`

---

## Quick Reference

| Endpoint | Method | Auth | Body Type |
|----------|--------|------|-----------|
| `/org/create` | POST | No | JSON |
| `/admin/login` | POST | No | JSON |
| `/org/get` | GET | No | Query Params |
| `/org/update` | PUT | Yes | JSON |
| `/org/delete` | DELETE | Yes | Query Params |

---

## Common Issues

- **422 Error:** Use JSON body for POST/PUT, add `Content-Type: application/json`
- **401 Error:** Add `Authorization: Bearer TOKEN` header
- **400 Already exists:** Use different organization name
