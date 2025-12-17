# API Documentation

All API requests go through the API Gateway at `http://localhost:8080`.

## Authentication

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "user",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-01-01T12:00:00Z",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** Same as register

## Voice Cloning

All voice cloning endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

### Create Voice Clone
```http
POST /api/voice/clones
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Voice Clone",
  "source_file": "path/to/audio.wav"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "pending",
  "message": "Voice clone job created"
}
```

### Get Voice Clone
```http
GET /api/voice/clones/{id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "My Voice Clone",
  "status": "completed",
  "source_file": "path/to/audio.wav",
  "output_file": "output/clone_1.wav",
  "created_at": "2024-01-01T10:00:00Z",
  "completed_at": "2024-01-01T10:15:00Z"
}
```

### List Voice Clones
```http
GET /api/voice/clones
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "My Voice Clone",
    "status": "completed",
    ...
  }
]
```

### Get Clone Status
```http
GET /api/voice/clones/{id}/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "processing"
}
```

## Storage

### Upload File
```http
POST /api/storage/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "filename": "audio.wav",
  "size": 1024000,
  "path": "/storage/audio.wav",
  "message": "File uploaded successfully"
}
```

### Download File
```http
GET /api/storage/download/{filename}
Authorization: Bearer <token>
```

### List Files
```http
GET /api/storage/files
Authorization: Bearer <token>
```

### Delete File
```http
DELETE /api/storage/files/{filename}
Authorization: Bearer <token>
```

## User Profile

### Get Profile
```http
GET /api/user/profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Voice cloning enthusiast"
}
```

### Update Profile
```http
PUT /api/user/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Updated bio"
}
```

### Get User Stats
```http
GET /api/user/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_clones": 10,
  "completed_clones": 8,
  "pending_clones": 1,
  "processing_clones": 1
}
```

## Health Checks

All services have a health check endpoint:
```http
GET /health
```


