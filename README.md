# Organization Management API

FastAPI backend for multi-tenant organization management with MongoDB.

## Features

- Organization CRUD operations
- Multi-tenant architecture with dynamic collections
- JWT authentication
- Admin account management
- Automatic data migration on organization rename  

---

## Setup

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname
MASTER_DB_NAME=master_organization_db
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=525600
DEBUG=True
```

### Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

---

## Project Structure

```
backend/
├── main.py              # FastAPI application and routes
├── config.py            # Configuration settings
├── db_connection.py     # Database connection manager
├── db_models.py         # Database operations (CRUD)
├── schemas.py           # Pydantic request/response models
├── utils.py             # JWT and password utilities
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── TESTING.md           # API testing guide
└── README.md            # This file
```

---

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/org/create` | POST | No | Create new organization |
| `/admin/login` | POST | No | Login and get JWT token |
| `/org/get` | GET | No | Get organization details |
| `/org/update` | PUT | Yes | Update organization |
| `/org/delete` | DELETE | Yes | Delete organization |
| `/health` | GET | No | Health check |

---

## Usage Examples

### Create Organization
```bash
curl -X POST http://localhost:8000/org/create \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "MyCompany",
    "email": "admin@mycompany.com",
    "password": "secure123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@mycompany.com",
    "password": "secure123"
  }'
```

### Update Organization (requires token)
```bash
curl -X PUT http://localhost:8000/org/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "organization_name": "MyCompany",
    "new_organization_name": "MyNewCompany"
  }'
```

See [TESTING.md](TESTING.md) for detailed testing steps.

---

## Troubleshooting

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Database connection failed:**
- Check MongoDB URL in `.env`
- Verify network access in MongoDB Atlas

**422 Error:**
- Use JSON body (not query params) for POST/PUT
- Add `Content-Type: application/json` header
