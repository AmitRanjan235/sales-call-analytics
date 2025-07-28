#!/usr/bin/env python3
"""
Comprehensive test script to verify API endpoints work correctly.
Run this with the server running to test all endpoints.
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000/api/v1"
SERVER_URL = "http://localhost:8000"

def test_calls_endpoint():
    """Test GET /api/v1/calls"""
    print("Testing GET /api/v1/calls...")
    
    # Test basic call
    response = requests.get(f"{BASE_URL}/calls")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
    
    # Test with query parameters
    params = {
        "limit": 5,
        "offset": 0,
        "min_sentiment": -1.0,
        "max_sentiment": 1.0
    }
    response = requests.get(f"{BASE_URL}/calls", params=params)
    print(f"With params - Status: {response.status_code}")
    print()

def test_call_detail_endpoint():
    """Test GET /api/v1/calls/{call_id}"""
    print("Testing GET /api/v1/calls/{call_id}...")
    
    # First get a call ID from the calls endpoint
    response = requests.get(f"{BASE_URL}/calls?limit=1")
    if response.status_code == 200 and response.json():
        call_id = response.json()[0]["call_id"]
        
        detail_response = requests.get(f"{BASE_URL}/calls/{call_id}")
        print(f"Status: {detail_response.status_code}")
        if detail_response.status_code == 200:
            print("✓ Call detail retrieved successfully")
        else:
            print(f"Error: {detail_response.json()}")
    else:
        print("No calls found to test with")
    print()

def test_recommendations_endpoint():
    """Test GET /api/v1/calls/{call_id}/recommendations"""
    print("Testing GET /api/v1/calls/{call_id}/recommendations...")
    
    # First get a call ID from the calls endpoint
    response = requests.get(f"{BASE_URL}/calls?limit=1")
    if response.status_code == 200 and response.json():
        call_id = response.json()[0]["call_id"]
        
        rec_response = requests.get(f"{BASE_URL}/calls/{call_id}/recommendations")
        print(f"Status: {rec_response.status_code}")
        if rec_response.status_code == 200:
            data = rec_response.json()
            print(f"✓ Found {len(data.get('similar_calls', []))} similar calls")
            print(f"✓ Found {len(data.get('coaching_nudges', []))} coaching nudges")
        else:
            print(f"Error: {rec_response.json()}")
    else:
        print("No calls found to test with")
    print()

def test_analytics_endpoint():
    """Test GET /api/v1/analytics/agents"""
    print("Testing GET /api/v1/analytics/agents...")
    
    response = requests.get(f"{BASE_URL}/analytics/agents")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found analytics for {len(data.get('agents', []))} agents")
        if data.get('agents'):
            agent = data['agents'][0]
            print(f"Sample agent: {agent['agent_id']}")
            print(f"  - Avg sentiment: {agent.get('avg_sentiment')}")
            print(f"  - Avg talk ratio: {agent.get('avg_talk_ratio')}")
            print(f"  - Total calls: {agent.get('total_calls')}")
    else:
        print(f"Error: {response.json()}")
    print()

def test_server_health():
    """Test server health and basic connectivity"""
    print("🏥 Testing Server Health...")
    
    try:
        # Test root endpoint
        response = requests.get(SERVER_URL, timeout=5)
        print(f"Root endpoint: {response.status_code}")
        
        # Test docs endpoint
        response = requests.get(f"{SERVER_URL}/docs", timeout=5)
        print(f"Docs endpoint: {response.status_code}")
        
        # Test OpenAPI schema
        response = requests.get(f"{SERVER_URL}/openapi.json", timeout=5)
        print(f"OpenAPI schema: {response.status_code}")
        
        print("✅ Server is healthy and accessible\n")
        return True
        
    except requests.exceptions.ConnectTimeout:
        print("❌ Server connection timeout - is it running?")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_error_handling():
    """Test API error handling"""
    print("🚨 Testing Error Handling...")
    
    # Test 404 for non-existent call
    response = requests.get(f"{BASE_URL}/calls/non_existent_call")
    print(f"Non-existent call: {response.status_code} (expected: 404)")
    
    if response.status_code == 404:
        error_data = response.json()
        print(f"✓ Proper error response: {error_data.get('detail')}")
    
    # Test invalid query parameters 
    response = requests.get(f"{BASE_URL}/calls?limit=999")  # Over max limit
    print(f"Invalid limit: {response.status_code}")
    
    # Test invalid sentiment range
    response = requests.get(f"{BASE_URL}/calls?min_sentiment=2.0")  # Over max
    print(f"Invalid sentiment: {response.status_code}")
    
    print("✅ Error handling tests completed\n")

def test_performance():
    """Test API performance"""
    print("⚡ Testing API Performance...")
    
    # Test response time for calls endpoint
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/calls?limit=10")
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000  # Convert to ms
    print(f"Calls endpoint response time: {response_time:.2f}ms")
    
    if response_time < 1000:  # Less than 1 second
        print("✅ Good response time")
    else:
        print("⚠️ Slow response time")
    
    print("✅ Performance tests completed\n")

def run_comprehensive_tests():
    """Run comprehensive API tests"""
    print("🧪 COMPREHENSIVE API TESTING")
    print("=" * 60)
    
    # Check server health first
    if not test_server_health():
        return False
    
    # Test all endpoints
    test_calls_endpoint()
    test_call_detail_endpoint()
    test_recommendations_endpoint()
    test_analytics_endpoint()
    
    # Test error handling
    test_error_handling()
    
    # Test performance
    test_performance()
    
    print("🎉 COMPREHENSIVE TESTING COMPLETED!")
    return True

def main():
    """Main testing function"""
    if not run_comprehensive_tests():
        print("\n❌ Some tests failed. Check the server and try again.")
        return
    
    print("\n🎯 QUICK TESTING GUIDE:")
    print("1. Start server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Create test data: python create_sample_data.py")
    print("3. Run tests: python test_api.py")
    print("4. View docs: http://localhost:8000/docs")
    print("5. Manual testing: Use browser or Postman with the endpoints above")

if __name__ == "__main__":
    main()
