# API Documentation

Complete API reference for Android Management API Server.

## Table of Contents

1. [Public Endpoints](#public-endpoints-no-authentication-required)
2. [Protected Endpoints](#protected-endpoints-require-jwt-token)
3. [Policy Management](#policy-management)
4. [Device Management](#device-management)
5. [Testing](#testing)

## Public Endpoints (No Authentication Required)

### Health Check
```
GET /health
```

Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Android Management API server is running"
}
```

---

### API Status
```
GET /api/v1/status
```

Returns API status information.

---

### Register New User
```
POST /api/v1/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-secure-password"
}
```

Creates a new user account with hashed password.

**Response:**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "email": "user@example.com"
}
```

**Errors:**
- 400: User already exists
- 500: Registration failed

---

### Login
```
POST /api/v1/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-secure-password"
}
```

Authenticates user and returns JWT token.

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "email": "user@example.com"
}
```

**Errors:**
- 401: Invalid email or password
- 500: Login failed

---

## Protected Endpoints (Require JWT Token)

All protected endpoints require the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

---

### Check Enterprise Registration
```
POST /api/v1/enterprise/login
Content-Type: application/json
Authorization: Bearer <token>

{
  "callback_url": "https://your-domain.com/callback"
}
```

Checks if user has an associated enterprise.

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

---

### Check Service Account Authentication Status
```
GET /api/v1/auth/status
Authorization: Bearer <token>
```

Verifies Google Cloud service account authentication.

**Response (Success):**
```json
{
  "status": "success",
  "authenticated": true,
  "message": "Service account authenticated successfully",
  "service_account_email": "service-account@project.iam.gserviceaccount.com",
  "project_id": "your-project-id",
  "details": {
    "scopes": ["https://www.googleapis.com/auth/androidmanagement"]
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

---

### Map Email to Enterprise
```
POST /api/v1/enterprise/map
Content-Type: application/json
Authorization: Bearer <token>

{
  "email": "user@example.com",
  "enterprise_name": "enterprises/LC037onrpk"
}
```

Maps an email address to an enterprise.

**Response:**
```json
{
  "status": "success",
  "message": "Email mapped to enterprise successfully"
}
```

---

### List Email-Enterprise Mappings
```
GET /api/v1/enterprise/mappings
Authorization: Bearer <token>
```

Retrieves all email-to-enterprise mappings.

**Response:**
```json
{
  "status": "success",
  "message": "Mappings retrieved successfully",
  "mappings": [
    {
      "email": "user@example.com",
      "enterprise_name": "enterprises/LC..."
    }
  ],
  "count": 1
}
```

---

### Register New Enterprise
```
POST /api/v1/enterprise/register
Authorization: Bearer <token>
Content-Type: application/json

{
  "signup_url_name": "signupUrls/LC...",
  "enterprise_token": "token-from-signup-completion",
  "email": "user@example.com"
}
```

Creates and registers a new enterprise.

**Response:**
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

---

## Policy Management

### List Policies
```
GET /api/v1/policies?enterprise_name=enterprises/LC...
Authorization: Bearer <token>
```

Lists all policies for an enterprise.

**Response:**
```json
{
  "status": "success",
  "message": "Policies retrieved successfully",
  "enterprise_name": "enterprises/LC...",
  "policies": [
    {
      "name": "enterprises/LC.../policies/my-policy",
      "policy_id": "my-policy",
      "version": "1",
      "applications": []
    }
  ],
  "count": 1
}
```

---

### Create or Update Policy
```
POST /api/v1/policies
Content-Type: application/json
Authorization: Bearer <token>

{
  "enterprise_name": "enterprises/LC...",
  "policy_name": "my-policy",
  "policy_body": {
    "applications": [
      {
        "packageName": "com.example.app",
        "installType": "FORCE_INSTALLED"
      }
    ]
  }
}
```

Creates a new policy or updates an existing one.

**Response:**
```json
{
  "status": "success",
  "message": "Policy created/updated successfully",
  "policy": {
    "name": "enterprises/LC.../policies/my-policy",
    "policy_id": "my-policy",
    "version": "1",
    "applications": [...]
  }
}
```

---

### Delete Policy
```
DELETE /api/v1/policies?enterprise_name=enterprises/LC...&policy_name=my-policy
Authorization: Bearer <token>
```

Deletes a policy from an enterprise.

**Response:**
```json
{
  "status": "success",
  "message": "Policy my-policy deleted successfully"
}
```

---

## Device Management

### List Devices
```
GET /api/v1/devices?enterprise_name=enterprises/LC...
Authorization: Bearer <token>
```

Lists all devices in an enterprise.

**Response:**
```json
{
  "status": "success",
  "message": "Devices retrieved successfully",
  "enterprise_name": "enterprises/LC...",
  "devices": [
    {
      "name": "enterprises/LC.../devices/device123",
      "device_id": "device123",
      "state": "ACTIVE",
      "appliedPolicyName": "enterprises/LC.../policies/my-policy",
      "appliedState": "ACTIVE",
      "hardwareInfo": {...},
      "policyName": "enterprises/LC.../policies/my-policy"
    }
  ],
  "count": 1
}
```

---

### Get Single Device
```
GET /api/v1/devices/{device_id}?enterprise_name=enterprises/LC...
Authorization: Bearer <token>
```

Retrieves detailed information about a specific device.

**Response:**
```json
{
  "status": "success",
  "message": "Device retrieved successfully",
  "device": {
    "name": "enterprises/LC.../devices/device123",
    "device_id": "device123",
    "state": "ACTIVE",
    "appliedPolicyName": "enterprises/LC.../policies/my-policy",
    "hardwareInfo": {...},
    "softwareInfo": {...},
    "memoryInfo": {...},
    "networkInfo": {...},
    "enrollmentTime": "2026-01-01T00:00:00Z",
    "lastStatusReportTime": "2026-02-02T12:00:00Z"
  }
}
```

---

### Create Enrollment Token (Provision Device)
```
POST /api/v1/devices/enrollment-token
Content-Type: application/json
Authorization: Bearer <token>

{
  "enterprise_name": "enterprises/LC...",
  "policy_name": "my-policy"
}
```

Generates an enrollment token for device provisioning.

**Response:**
```json
{
  "status": "success",
  "message": "Enrollment token created successfully",
  "enrollment_token": {
    "name": "enterprises/LC.../enrollmentTokens/token123",
    "value": "ABC123TOKEN",
    "qrCode": "data:image/png;base64,...",
    "policyName": "enterprises/LC.../policies/my-policy",
    "expirationTimestamp": "2026-02-09T12:00:00Z"
  }
}
```

---

### Delete Device
```
DELETE /api/v1/devices/{device_id}?enterprise_name=enterprises/LC...
Authorization: Bearer <token>
```

Deletes a device from an enterprise.

**Response:**
```json
{
  "status": "success",
  "message": "Device device123 deleted successfully"
}
```

---

## Testing

### Authentication Flow Example

1. **Register a new user:**
```bash
curl -X POST http://localhost:8088/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

2. **Login to get JWT token:**
```bash
curl -X POST http://localhost:8088/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

Response:
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "email": "user@example.com"
}
```

3. **Use JWT token in subsequent requests:**
```bash
# Save token to variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Check enterprise registration
curl -X POST http://localhost:8088/api/v1/enterprise/login \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"callback_url": "https://your-domain.com/callback"}'
```

---

### Using curl

**Public endpoints:**
```bash
# Health check
curl http://localhost:8088/health

# API status
curl http://localhost:8088/api/v1/status

# Register user
curl -X POST http://localhost:8088/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8088/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

**Protected endpoints (replace YOUR_JWT_TOKEN):**
```bash
# Check authentication status
curl http://localhost:8088/api/v1/auth/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Check enterprise registration
curl -X POST http://localhost:8088/api/v1/enterprise/login \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"callback_url": "https://your-domain.com/callback"}'

# Map email to enterprise
curl -X POST http://localhost:8088/api/v1/enterprise/map \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"email": "user@example.com", "enterprise_name": "enterprises/LC037onrpk"}'

# List mappings
curl http://localhost:8088/api/v1/enterprise/mappings \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Register new enterprise
curl -X POST http://localhost:8088/api/v1/enterprise/register \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"signup_url_name": "signupUrls/LC...", "enterprise_token": "token-value", "email": "user@example.com"}'

# List policies
curl "http://localhost:8088/api/v1/policies?enterprise_name=enterprises/LC037onrpk" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create or update policy
curl -X POST http://localhost:8088/api/v1/policies \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "enterprise_name": "enterprises/LC037onrpk",
    "policy_name": "my-policy",
    "policy_body": {
      "applications": [
        {
          "packageName": "com.example.app",
          "installType": "FORCE_INSTALLED"
        }
      ]
    }
  }'

# Delete policy
curl -X DELETE "http://localhost:8088/api/v1/policies?enterprise_name=enterprises/LC037onrpk&policy_name=my-policy" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# List devices
curl "http://localhost:8088/api/v1/devices?enterprise_name=enterprises/LC037onrpk" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get single device
curl "http://localhost:8088/api/v1/devices/device123?enterprise_name=enterprises/LC037onrpk" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create enrollment token for device provisioning
curl -X POST http://localhost:8088/api/v1/devices/enrollment-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "enterprise_name": "enterprises/LC037onrpk",
    "policy_name": "my-policy"
  }'

# Delete device
curl -X DELETE "http://localhost:8088/api/v1/devices/device123?enterprise_name=enterprises/LC037onrpk" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Using Python test script
```bash
python test_jwt_flow.py
```

### Using Python requests library

```python
import requests

# Register
response = requests.post(
    'http://localhost:8088/api/v1/register',
    json={"email": "user@example.com", "password": "password123"}
)
print(response.json())

# Login
response = requests.post(
    'http://localhost:8088/api/v1/login',
    json={"email": "user@example.com", "password": "password123"}
)
token = response.json().get('token')

# Use token for protected endpoints
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:8088/api/v1/auth/status',
    headers=headers
)
print(response.json())
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized (Auth failed, missing/invalid token) |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Authentication Header Format

All protected endpoints require:
```
Authorization: Bearer <jwt-token>
```

The JWT token is obtained from the `/api/v1/login` endpoint and is valid for 24 hours by default (configurable via `JWT_EXPIRATION_HOURS`).
