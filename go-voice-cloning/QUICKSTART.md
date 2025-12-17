# Quick Start Guide

Get your voice cloning microservices up and running in minutes!

## Prerequisites

- Go 1.21 or higher
- Docker and Docker Compose
- PostgreSQL (or use Docker)

## Option 1: Using Docker (Recommended)

This is the easiest way to get started:

```bash
# Clone or navigate to the project directory
cd go-voice-cloning

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

All services will be available:
- API Gateway: http://localhost:8080
- Auth Service: http://localhost:8081
- Voice Service: http://localhost:8082
- Storage Service: http://localhost:8083
- User Service: http://localhost:8084

## Option 2: Local Development

### Step 1: Set up PostgreSQL

```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=voice_cloning \
  -p 5432:5432 \
  postgres:15-alpine

# Or install PostgreSQL locally
```

### Step 2: Build Shared Module

```bash
cd shared
go mod download
cd ..
```

### Step 3: Start Services

Open multiple terminals and run each service:

**Terminal 1 - Auth Service:**
```bash
cd auth-service
go mod download
go run main.go
```

**Terminal 2 - Voice Service:**
```bash
cd voice-service
go mod download
go run main.go
```

**Terminal 3 - Storage Service:**
```bash
cd storage-service
go mod download
go run main.go
```

**Terminal 4 - User Service:**
```bash
cd user-service
go mod download
go run main.go
```

**Terminal 5 - API Gateway:**
```bash
cd gateway
go mod download
go run main.go
```

### Step 4: Test the API

```bash
# Register a user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'

# Save the token from the response, then login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Use the token to create a voice clone
curl -X POST http://localhost:8080/api/voice/clones \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Voice Clone",
    "source_file": "audio/sample.wav"
  }'
```

## Running the Example Client

```bash
cd examples
go run client.go
```

## Troubleshooting

### Port Already in Use
If a port is already in use, you can change it by setting environment variables:
```bash
export PORT=8080
export AUTH_SERVICE_URL=http://localhost:8081
# etc.
```

### Database Connection Issues
Make sure PostgreSQL is running and accessible:
```bash
# Test connection
psql -h localhost -U postgres -d voice_cloning
```

### Service Not Starting
Check the logs:
```bash
# Docker
docker-compose logs <service-name>

# Local
# Check the terminal where you started the service
```

## Next Steps

1. Read the [Learning Guide](docs/LEARNING_GUIDE.md) for a structured learning path
2. Explore the [API Documentation](docs/API.md) for all endpoints
3. Modify services to add your own features
4. Add real voice cloning integration

## Development Tips

1. **Hot Reload**: Use tools like `air` or `realize` for auto-reloading during development
2. **Testing**: Run `go test ./...` in each service directory
3. **Linting**: Use `golangci-lint` for code quality
4. **Debugging**: Use `delve` debugger for Go debugging

Happy coding! 🚀


