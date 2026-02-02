# Android Management API Server

Flask-based RESTful API server for managing Android devices via Google Cloud Android Management API.

## Features

- ✅ Flask-based RESTful API
- ✅ Google Cloud service account authentication
- ✅ Android Management API integration
- ✅ Environment-based configuration
- ✅ Health check and status endpoints

## Prerequisites

- Python 3.8+
- Google Cloud Project with Android Management API enabled
- Service account with Android Management permissions

## Installation

### 1. Clone or navigate to project directory
```bash
cd /Users/thinhnn/Desktop/endpoint-mobile/server
```

### 2. Run setup script
```bash
# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
```

### 3. Configure environment variables
Edit `.env` file with your Google Cloud credentials:
```
CLOUD_PROJECT_ID=your-gcp-project-id
SERVICE_ACCOUNT_JSON=/path/to/service-account-key.json
SQLITE_DB_PATH=local.db
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### 4. Get Google Cloud Service Account Key
1. Go to Google Cloud Console
2. Navigate to Service Accounts
3. Create a new service account with Android Management permissions
4. Download the JSON key file
5. Update `SERVICE_ACCOUNT_JSON` path in `.env`

## Running the Server

### Activate virtual environment
```bash
source venv/bin/activate
```

### Start the server
```bash
python app.py
```

The server will start on `http://localhost:8088`

## API Endpoints

### Health Check
```
GET /health
```

### API Status
```
GET /api/v1/status
```

### Login - Check Enterprise Registration
```
POST /api/v1/login
Content-Type: application/json

{
  "email": "user@example.com",
  "callback_url": "https://your-domain.com/callback"
}
```

**Response (Enterprise Found):**
```json
{
  "status": "success",
  "enterprise_found": true,
  "message": "Enterprise found for this email",
  "email": "user@example.com",
  "enterprise": {
    "name": "enterprises/LC...",
    "display_name": "Company Name",
    "enterprise_id": "LC..."
  }
}
```

**Response (Enterprise Not Found - Signup URL):**
```json
{
  "status": "success",
  "enterprise_found": false,
  "message": "No enterprise found. Please sign up.",
  "email": "user@example.com",
  "signup_url": "https://enterprise.google.com/android/enroll?et=..."
}
```

### Check Service Account Authentication Status
```
GET /api/v1/auth/status
```

### Map Email to Enterprise
```
POST /api/v1/enterprise/map
Content-Type: application/json

{
  "email": "user@example.com",
  "enterprise_name": "enterprises/LC037onrpk"
}
```

### List Email-Enterprise Mappings
```
GET /api/v1/enterprise/mappings
```

### Register New Enterprise
```
POST /api/v1/enterprise/register
Content-Type: application/json

{
  "signup_url_name": "signupUrls/LC...",
  "enterprise_token": "token-from-signup-completion",
  "email": "user@example.com"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Enterprise registered successfully",
  "email": "user@example.com",
  "enterprise_name": "enterprises/LC...",
  "enterprise": {
    "name": "enterprises/LC...",
    "display_name": "Enterprise",
    "enterprise_id": "LC..."
  }
}
```

### Authentication Status

**Response (Success):**
```json
{
  "status": "success",
  "authenticated": true,
  "message": "Service account authenticated successfully",
  "service_account_email": "service-account@project.iam.gserviceaccount.com",
  "project_id": "your-project-id",
  "details": {
    "scopes": ["https://www.googleapis.com/auth/androidmanagement", "..."]
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "authenticated": false,
  "message": "Authentication check failed: ...",
  "error_type": "Exception"
}
```

## Testing API

### Using curl
```bash
# Health check
curl http://localhost:8088/health

# Check authentication status
curl http://localhost:8088/api/v1/auth/status

# API status
curl http://localhost:8088/api/v1/status

# Login with email
curl -X POST http://localhost:8088/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "callback_url": "https://your-domain.com/callback"}'

# Map email to enterprise
curl -X POST http://localhost:8088/api/v1/enterprise/map \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "enterprise_name": "enterprises/LC037onrpk"}'

# List mappings
curl http://localhost:8088/api/v1/enterprise/mappings

# Register new enterprise
curl -X POST http://localhost:8088/api/v1/enterprise/register \
  -H "Content-Type: application/json" \
  -d '{"signup_url_name": "signupUrls/LC...", "enterprise_token": "token-value", "email": "user@example.com"}'
```

### Using Python test script
```bash
python test_api.py
```

### Using Python requests
```python
import requests

# Check authentication
response = requests.get('http://localhost:8088/api/v1/auth/status')
print(response.json())

# Login with email
response = requests.post(
    'http://localhost:8088/api/v1/login',
    json={"email": "user@example.com"}
)
print(response.json())
```

## Project Structure

```
server/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── auth.py                # Google Cloud authentication
├── db.py                  # Local SQLite storage
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── setup.sh               # Setup script
└── README.md              # This file
```

## Environment Variables

- `CLOUD_PROJECT_ID`: Your Google Cloud Project ID
- `SERVICE_ACCOUNT_JSON`: Path to service account JSON key file
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable Flask debug mode
- `PORT`: Server port (default: 5000)

## Error Handling

The API includes comprehensive error handling:
- 400: Bad Request
- 401: Unauthorized (Auth failed)
- 404: Not Found
- 500: Internal Server Error
- 503: Service Unavailable

## Future Enhancements

- [ ] Device management endpoints
- [ ] Policy management endpoints
- [ ] User management endpoints
- [ ] Database integration
- [ ] Request logging and monitoring
- [ ] Rate limiting
- [ ] API authentication (JWT)
- [ ] Comprehensive testing suite

## License

MIT
