# Android Management API Server

Flask-based RESTful API server for managing Android devices via Google Cloud Android Management API.

## Features

- ✅ Flask-based RESTful API
- ✅ JWT-based authentication and authorization
- ✅ bcrypt password hashing
- ✅ Google Cloud service account authentication
- ✅ Android Management API integration
- ✅ Local SQLite database for user credentials
- ✅ CORS enabled for frontend integration (http://localhost:3000)
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
JWT_SECRET_KEY=your-random-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24
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

## API Documentation

For complete API documentation including all endpoints, request/response examples, and testing instructions, see [API_DOC.md](API_DOC.md).

### Quick API Overview

**Public Endpoints (No Auth Required):**
- `GET /health` - Health check
- `GET /api/v1/status` - API status
- `POST /api/v1/register` - Register new user
- `POST /api/v1/login` - Login and get JWT token

**Protected Endpoints (Require JWT):**
- `POST /api/v1/enterprise/login` - Check enterprise registration
- `GET /api/v1/auth/status` - Verify service account auth
- `POST /api/v1/enterprise/register` - Register new enterprise
- `GET/POST/DELETE /api/v1/policies` - Policy management
- `GET/POST/DELETE /api/v1/devices` - Device management
- `POST /api/v1/devices/enrollment-token` - Generate enrollment token

See [API_DOC.md](API_DOC.md) for detailed documentation.

## CORS Configuration

The server is configured to accept requests from frontend development server running on `http://localhost:3000`.

**CORS Settings:**
- **Origin:** `http://localhost:3000`
- **Methods:** GET, POST, PUT, DELETE, OPTIONS
- **Headers:** Content-Type, Authorization

To modify CORS settings for production, update the `CORS()` configuration in `app.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://your-frontend-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
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
