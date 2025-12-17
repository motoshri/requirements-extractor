# Voice Cloning Microservices - Go Learning Project

A comprehensive microservices architecture built with Go for learning and implementing a voice cloning application.

## 🎯 Learning Objectives

1. **Microservices Architecture**: Understand service decomposition, communication patterns, and scalability
2. **Go Programming**: Learn Go idioms, concurrency, HTTP servers, and best practices
3. **Service Communication**: REST APIs, gRPC, message queues
4. **Containerization**: Docker and Docker Compose for multi-service deployment
5. **Service Discovery**: How services find and communicate with each other
6. **Authentication & Authorization**: JWT-based security across services
7. **Database Design**: Service-specific databases (polyglot persistence)

## 🏗️ Architecture Overview

```
┌─────────────┐
│   Client    │
│  (Web/API)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  API Gateway    │  ← Entry point, routing, rate limiting
│   (Port 8080)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────────┐
    │         │          │             │
    ▼         ▼          ▼             ▼
┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│  Auth  │ │  Voice  │ │ Storage  │ │  User    │
│ Service│ │ Service │ │ Service  │ │ Service  │
│ :8081  │ │ :8082   │ │ :8083    │ │ :8084    │
└────────┘ └─────────┘ └──────────┘ └──────────┘
    │         │          │             │
    └─────────┴──────────┴─────────────┘
                    │
            ┌───────┴───────┐
            │   PostgreSQL  │
            │   (Shared DB) │
            └───────────────┘
```

## 📦 Services

### 1. **API Gateway** (`gateway/`)
- Entry point for all client requests
- Request routing to appropriate services
- Rate limiting and request validation
- Load balancing (future)

### 2. **Authentication Service** (`auth-service/`)
- User registration and login
- JWT token generation and validation
- Password hashing (bcrypt)
- Token refresh mechanism

### 3. **Voice Processing Service** (`voice-service/`)
- Audio file upload handling
- Voice cloning processing (integration ready)
- Audio format validation
- Processing queue management

### 4. **Storage Service** (`storage-service/`)
- File upload/download
- File metadata management
- Storage abstraction (local/S3 ready)

### 5. **User Service** (`user-service/`)
- User profile management
- User preferences
- Usage statistics

## 🚀 Getting Started

### Prerequisites
- Go 1.21+ installed
- Docker and Docker Compose
- PostgreSQL (or use Docker)

### Quick Start

```bash
# Start all services
docker-compose up -d

# Or run individually for development
cd gateway && go run main.go
cd auth-service && go run main.go
# ... etc
```

## 📚 Learning Path

### Week 1: Basics
- [ ] Set up Go project structure
- [ ] Create simple HTTP server
- [ ] Understand Go modules and dependencies
- [ ] Basic REST API implementation

### Week 2: Services
- [ ] Build each microservice
- [ ] Implement service-to-service communication
- [ ] Add database connections
- [ ] Error handling and logging

### Week 3: Integration
- [ ] Service discovery
- [ ] API Gateway implementation
- [ ] Authentication flow
- [ ] Docker containerization

### Week 4: Advanced
- [ ] Message queues (RabbitMQ/Kafka)
- [ ] gRPC for inter-service communication
- [ ] Monitoring and observability
- [ ] Testing strategies

## 🛠️ Tech Stack

- **Language**: Go 1.21+
- **Web Framework**: Standard `net/http` (learning) + `gorilla/mux` (routing)
- **Database**: PostgreSQL
- **Authentication**: JWT (golang-jwt/jwt)
- **Containerization**: Docker, Docker Compose
- **Testing**: Go testing package, testify

## 📖 Project Structure

```
go-voice-cloning/
├── gateway/              # API Gateway service
├── auth-service/         # Authentication service
├── voice-service/        # Voice processing service
├── storage-service/      # File storage service
├── user-service/         # User management service
├── shared/               # Shared utilities and types
├── docker-compose.yml    # Multi-service orchestration
├── Makefile             # Common commands
└── README.md            # This file
```

## 🔐 Environment Variables

Each service has its own `.env` file. See individual service READMEs for details.

## 📝 API Documentation

See `docs/API.md` for detailed API documentation.

## 🧪 Testing

```bash
# Run all tests
make test

# Run tests for specific service
cd auth-service && go test ./...
```

## 📚 Resources

- [Go by Example](https://gobyexample.com/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Microservices Patterns](https://microservices.io/patterns/)


