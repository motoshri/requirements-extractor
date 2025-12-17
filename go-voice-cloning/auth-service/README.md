# Authentication Service

Handles user registration, login, and JWT token validation.

## Endpoints

- `POST /register` - Register a new user
- `POST /login` - Login and get JWT token
- `POST /validate` - Validate a JWT token
- `GET /health` - Health check

## Environment Variables

- `PORT` - Service port (default: 8081)
- `DATABASE_URL` - PostgreSQL connection string

## Example Usage

```bash
# Register
curl -X POST http://localhost:8081/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"password123"}'

# Login
curl -X POST http://localhost:8081/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```


