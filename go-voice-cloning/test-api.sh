#!/bin/bash

# Simple API test script for Voice Cloning Microservices
# Make sure all services are running before executing this script

BASE_URL="http://localhost:8080"

echo "🧪 Testing Voice Cloning Microservices API"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo "1. Testing Gateway Health Check..."
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
if [ "$response" == "200" ]; then
    echo -e "${GREEN}✓ Gateway is healthy${NC}"
else
    echo -e "${RED}✗ Gateway health check failed (Status: $response)${NC}"
    exit 1
fi
echo ""

# Test 2: Register User
echo "2. Testing User Registration..."
register_response=$(curl -s -X POST $BASE_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }')

token=$(echo $register_response | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$token" ]; then
    echo -e "${RED}✗ Registration failed${NC}"
    echo "Response: $register_response"
    exit 1
else
    echo -e "${GREEN}✓ User registered successfully${NC}"
    echo "Token: ${token:0:50}..."
fi
echo ""

# Test 3: Login
echo "3. Testing User Login..."
login_response=$(curl -s -X POST $BASE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }')

login_token=$(echo $login_response | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$login_token" ]; then
    echo -e "${RED}✗ Login failed${NC}"
    echo "Response: $login_response"
    exit 1
else
    echo -e "${GREEN}✓ Login successful${NC}"
    token=$login_token
fi
echo ""

# Test 4: Create Voice Clone
echo "4. Testing Voice Clone Creation..."
clone_response=$(curl -s -X POST $BASE_URL/api/voice/clones \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Voice Clone",
    "source_file": "test/audio.wav"
  }')

clone_id=$(echo $clone_response | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$clone_id" ]; then
    echo -e "${RED}✗ Voice clone creation failed${NC}"
    echo "Response: $clone_response"
    exit 1
else
    echo -e "${GREEN}✓ Voice clone created (ID: $clone_id)${NC}"
fi
echo ""

# Test 5: Get Clone Status
echo "5. Testing Clone Status Check..."
status_response=$(curl -s -X GET $BASE_URL/api/voice/clones/$clone_id/status \
  -H "Authorization: Bearer $token")

status=$(echo $status_response | grep -o '"status":"[^"]*' | cut -d'"' -f4)

if [ -z "$status" ]; then
    echo -e "${RED}✗ Status check failed${NC}"
    echo "Response: $status_response"
    exit 1
else
    echo -e "${GREEN}✓ Clone status: $status${NC}"
fi
echo ""

# Test 6: List Clones
echo "6. Testing Clone List..."
list_response=$(curl -s -X GET $BASE_URL/api/voice/clones \
  -H "Authorization: Bearer $token")

if echo "$list_response" | grep -q "Test Voice Clone"; then
    echo -e "${GREEN}✓ Clone list retrieved${NC}"
else
    echo -e "${RED}✗ Clone list failed${NC}"
    echo "Response: $list_response"
    exit 1
fi
echo ""

# Test 7: Get User Profile
echo "7. Testing User Profile..."
profile_response=$(curl -s -X GET $BASE_URL/api/user/profile \
  -H "Authorization: Bearer $token")

if echo "$profile_response" | grep -q "testuser"; then
    echo -e "${GREEN}✓ User profile retrieved${NC}"
else
    echo -e "${RED}✗ Profile retrieval failed${NC}"
    echo "Response: $profile_response"
    exit 1
fi
echo ""

# Test 8: Get User Stats
echo "8. Testing User Stats..."
stats_response=$(curl -s -X GET $BASE_URL/api/user/stats \
  -H "Authorization: Bearer $token")

if echo "$stats_response" | grep -q "total_clones"; then
    echo -e "${GREEN}✓ User stats retrieved${NC}"
else
    echo -e "${RED}✗ Stats retrieval failed${NC}"
    echo "Response: $stats_response"
    exit 1
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""


