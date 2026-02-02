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
chmod +x setup.sh
./setup.sh
```

### 3. Configure environment variables
Edit `.env` file with your Google Cloud credentials:
```
CLOUD_PROJECT_ID=your-gcp-project-id
SERVICE_ACCOUNT_JSON=/path/to/service-account-key.json
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

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```

### API Status
```
GET /api/v1/status
```

### Check Service Account Authentication Status
```
GET /api/v1/auth/status
```

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
curl http://localhost:5000/health

# Check authentication status
curl http://localhost:5000/api/v1/auth/status

# API status
curl http://localhost:5000/api/v1/status
```

### Using Python requests
```python
import requests

# Check authentication
response = requests.get('http://localhost:5000/api/v1/auth/status')
print(response.json())
```

## Project Structure

```
server/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── auth.py                # Google Cloud authentication
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
