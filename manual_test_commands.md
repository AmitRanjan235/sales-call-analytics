# 🧪 Manual API Testing Commands

## Prerequisites
1. Start the server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. Create sample data: `python create_sample_data.py`

## Method 1: Using curl (Command Line)

### Test 1: Get all calls
```bash
curl -X GET "http://localhost:8000/api/v1/calls" -H "accept: application/json"
```

### Test 2: Get calls with filters
```bash
curl -X GET "http://localhost:8000/api/v1/calls?limit=5&agent_id=agent_001" -H "accept: application/json"
```

### Test 3: Get specific call details
```bash
curl -X GET "http://localhost:8000/api/v1/calls/call_0001" -H "accept: application/json"
```

### Test 4: Get recommendations for a call
```bash
curl -X GET "http://localhost:8000/api/v1/calls/call_0001/recommendations" -H "accept: application/json"
```

### Test 5: Get agent analytics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/agents" -H "accept: application/json"
```

## Method 2: Using Python requests

### Quick test script:
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test 1: Get calls
response = requests.get(f"{BASE_URL}/calls")
print(f"GET /calls: {response.status_code}")
print(response.json())

# Test 2: Get analytics
response = requests.get(f"{BASE_URL}/analytics/agents")
print(f"GET /analytics/agents: {response.status_code}")
print(response.json())
```

## Method 3: Using Browser
- Open: http://localhost:8000/docs
- Interactive Swagger UI will load
- Click on any endpoint to test it
- Click "Try it out" button
- Fill parameters and click "Execute"

## Method 4: Using Postman
1. Import the OpenAPI spec from: http://localhost:8000/openapi.json
2. Or manually create requests:
   - GET http://localhost:8000/api/v1/calls
   - GET http://localhost:8000/api/v1/calls/call_0001
   - GET http://localhost:8000/api/v1/calls/call_0001/recommendations
   - GET http://localhost:8000/api/v1/analytics/agents

## Expected Status Codes
- ✅ 200: Success
- ❌ 404: Call not found
- ❌ 422: Validation error
- ❌ 500: Server error

## Test Data Available
- Calls: call_0001 to call_0020
- Agents: agent_001 to agent_005
- All calls have embeddings and can be used for recommendations
