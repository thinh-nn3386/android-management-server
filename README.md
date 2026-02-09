# Android Management API Server

Flask-based RESTful API server for managing Android devices via Google Cloud Android Management API with clean architecture and modular design.

## Features

- ✅ **Clean Architecture** - Separated layers (Routes, Services, Repositories, Database)
- ✅ **Flask Blueprints** - Modular route organization
- ✅ **JWT Authentication** - Secure token-based auth with bcrypt password hashing
- ✅ **Google Android Management API** - Full EMM integration
- ✅ **Repository Pattern** - Database abstraction for easy switching
- ✅ **Reusable Decorators** - DRY principle with shared decorators
- ✅ **Type Hints** - Better IDE support and code quality
- ✅ **SQLite/Cloud Database** - Flexible storage options
- ✅ **CORS Enabled** - Frontend integration ready
- ✅ **Environment-based Configuration** - Secure config management
- ✅ **Comprehensive Documentation** - API docs and architecture guides

## Prerequisites

- **Python 3.8+** (tested on Python 3.14)
- **Google Cloud Project** with Android Management API enabled
- **Service Account** with Android Management permissions
- **SQLite** (included) or Cloud database

## Quick Start

### 1. Clone and Navigate
```bash
cd /Users/thinhnn/Desktop/endpoint-mobile/server
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file (or copy from `.env.example`):
```env
# Google Cloud Configuration
CLOUD_PROJECT_ID=your-gcp-project-id
SERVICE_ACCOUNT_JSON=./endpoint-agent-889491ab3ab5.json

# Database Configuration
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=local.db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### 5. Get Google Cloud Service Account Key
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **IAM & Admin > Service Accounts**
3. Create service account with **Android Management API** permissions
4. Download JSON key file
5. Place in project root and update `SERVICE_ACCOUNT_JSON` path

### 6. Run the Server
```bash
python main.py
```

Server starts on: `http://localhost:5000`

## Project Structure

```
server/
├── main.py                           # Application entry point
├── config.py                         # Configuration management
├── requirements.txt                  # Python dependencies
├── local.db                          # SQLite database (generated)
├── endpoint-agent-*.json             # Google service account key
│
├── app/
│   ├── __init__.py
│   ├── app.py                        # Flask app factory
│   │
│   ├── routes/                       # API Routes (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth_routes.py            # User authentication endpoints
│   │   └── android_management_routes.py  # Google EMM API endpoints
│   │
│   ├── utils/                        # Utilities Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Password hashing & JWT tokens
│   │   └── decorators.py             # Reusable decorators
│   │
│   ├── services/                     # Business Logic Layer
│   │   ├── __init__.py
│   │   └── google_android_management.py  # Google API client
│   │
│   ├── repositories/                 # Data Access Layer
│   │   ├── __init__.py
│   │   ├── user_repository.py        # User data operations
│   │   └── enterprise_repository.py  # Enterprise data operations
│   │
│   ├── database/                     # Database Layer
│   │   ├── __init__.py
│   │   ├── base.py                   # Abstract database interface
│   │   ├── local_sqlite_db.py        # SQLite implementation
│   │   └── cloud_db.py               # Cloud database implementation
│   │
│   └── model/                        # Data Models
│       └── __init__.py
│
├── tests/                            # Test Suite
│   ├── __init__.py
│   ├── test_api.py
│   └── test_jwt_flow.py
│
└── docs/                             # Documentation
    ├── API_DOC.md                    # API documentation
    ├── REFACTORING_SUMMARY.md        # Refactoring details
    ├── PROJECT_STRUCTURE.md          # Architecture diagrams
    ├── AUTH_UTILS_LOCATION.md        # Auth utilities guide
    ├── DECORATORS_REFACTORING.md     # Decorators guide
    └── COMPLETE_STRUCTURE.md         # Complete structure guide
```

## Architecture

The application follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────┐
│  Routes Layer (HTTP)                │  Flask Blueprints
│  ├─ auth_routes.py                  │  API endpoints
│  └─ android_management_routes.py    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Utils Layer (Cross-cutting)        │  Shared utilities
│  ├─ auth_service.py                 │  Password & JWT
│  └─ decorators.py                   │  Reusable decorators
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Services Layer (Business Logic)    │  External APIs
│  └─ google_android_management.py    │  Google EMM client
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Repositories Layer (Data Access)   │  Database operations
│  ├─ user_repository.py              │
│  └─ enterprise_repository.py        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Database Layer (Storage)           │  Data persistence
│  ├─ local_sqlite_db.py              │  SQLite
│  └─ cloud_db.py                     │  Cloud DB
└─────────────────────────────────────┘
```

## API Endpoints

### Authentication APIs (`/api/v1`)
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `GET /status` - API status check

### Enterprise Management APIs (`/api/v1/enterprise`)
- `POST /login` - Check user's enterprise registration
- `POST /signup-url` - Generate enterprise signup URL
- `POST /webtoken` - Create enterprise web token
- `POST /register` - Register new enterprise
- `GET /auth/status` - Check Google authentication status
- `DELETE /<enterprise_id>` - Delete enterprise

### Policy Management APIs (`/api/v1/policies`)
- `GET /<enterprise_name>/policies` - List all policies
- `GET /<enterprise_name>/policies/<policy_id>` - Get policy details
- `POST /<enterprise_name>/policies/<policy_id>` - Create/update policy
- `DELETE /<enterprise_name>/policies/<policy_id>` - Delete policy
- `POST /<policy_name>:modifyPolicyApplications` - Modify policy apps

### Device Management APIs (`/api/v1/devices`)
- `GET /<enterprise_name>/devices` - List all devices
- `GET /<enterprise_name>/devices/<device_id>` - Get device details
- `POST /<enterprise_name>/devices/enrollment-token` - Create enrollment token
- `DELETE /<enterprise_name>/devices/<device_id>` - Delete device
- `POST /<enterprise_name>/devices/<device_id>:issueCommand` - Issue device command

See [API_DOC.md](./API_DOC.md) for detailed documentation.

## Authentication Flow

1. **Register**: `POST /api/v1/register`
   ```json
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```

2. **Login**: `POST /api/v1/login`
   ```json
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```
   Returns JWT token: `{"token": "eyJhbG..."}`

3. **Use Protected Endpoints**: Include token in header
   ```
   Authorization: Bearer eyJhbG...
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLOUD_PROJECT_ID` | Google Cloud Project ID | - |
| `SERVICE_ACCOUNT_JSON` | Path to service account key | - |
| `DATABASE_TYPE` | Database type (sqlite/cloud) | `sqlite` |
| `SQLITE_DB_PATH` | SQLite database path | `local.db` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | - |
| `JWT_EXPIRATION_HOURS` | JWT token expiration | `24` |
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `PORT` | Server port | `5000` |

### CORS Settings

Configured for frontend development:
- **Allowed Origins**: `http://localhost:3000`
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, Authorization

## Key Features

### 1. Reusable Decorators

```python
from app.utils.decorators import (
    error_handler,
    require_jwt,
    require_client,
    require_authenticated_client
)

@enterprise_bp.route('/endpoint')
@require_authenticated_client  # Combines error + JWT + client check
def my_endpoint():
    pass
```

### 2. Repository Pattern

Easy to switch database implementations:
```python
# config.py
DATABASE_TYPE = "sqlite"  # or "cloud"

# Automatically uses correct implementation
from app.database import get_database
db = get_database()  # Returns SQLite or Cloud DB
```

### 3. Type Hints

Better IDE support and code clarity:
```python
from typing import Optional
from app.services.google_android_management import GoogleAndroidManagement

emm_client: Optional[GoogleAndroidManagement] = None
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Structure
- Follow **verb + resource** naming convention
- Use **type hints** for better IDE support
- Keep **decorators reusable** and in utils layer
- Maintain **single responsibility** per module

### Adding New Endpoints
1. Add route in appropriate blueprint (`app/routes/`)
2. Use decorators for auth and error handling
3. Call service/repository methods
4. Return standardized responses

## Error Handling

All endpoints return consistent error format:

```json
{
  "status": "error",
  "error": {
    "code": 400,
    "message": "Error description"
  }
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (auth failed)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

## Troubleshooting

### Common Issues

**1. Module import errors**
```bash
# Run as module, not script
python -m app.app  # ❌ Wrong
python main.py     # ✅ Correct
```

**2. Database initialization errors**
```bash
# Check database path in config.py
# Delete local.db and restart to recreate
rm local.db
python main.py
```

**3. Google API authentication errors**
```bash
# Verify service account key path
# Ensure API is enabled in Google Cloud Console
```

## Documentation

- **[API_DOC.md](./API_DOC.md)** - Complete API documentation
- **[REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md)** - Refactoring details
- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - Architecture diagrams
- **[COMPLETE_STRUCTURE.md](./COMPLETE_STRUCTURE.md)** - Complete structure guide

## Resources

- [Google Android Management API](https://developers.google.com/android/management/reference/rest)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [JWT Introduction](https://jwt.io/introduction)

## License

MIT

## Contributing

Contributions welcome! Please follow the existing code structure and naming conventions.

---

**Built with Flask • Clean Architecture • Google Android Management API**

