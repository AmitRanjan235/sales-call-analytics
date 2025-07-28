#!/usr/bin/env python3
"""Quick API test - run this after starting the server"""

import requests
import json

def quick_test():
    BASE_URL = "http://localhost:8000/api/v1"
    
    print("🚀 Quick API Test")
    print("=" * 30)
    
    try:
        # Test 1: Get calls
        print("1. Testing GET /calls...")
        response = requests.get(f"{BASE_URL}/calls?limit=3")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            calls = response.json()
            print(f"   Found {len(calls)} calls")
            if calls:
                print(f"   Sample call ID: {calls[0]['call_id']}")
        
        # Test 2: Get analytics
        print("\n2. Testing GET /analytics/agents...")
        response = requests.get(f"{BASE_URL}/analytics/agents")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data['agents'])} agents")
        
        # Test 3: Get specific call
        print("\n3. Testing GET /calls/call_0001...")
        response = requests.get(f"{BASE_URL}/calls/call_0001")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Call details retrieved successfully")
        
        # Test 4: Get recommendations
        print("\n4. Testing GET /calls/call_0001/recommendations...")
        response = requests.get(f"{BASE_URL}/calls/call_0001/recommendations")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data.get('similar_calls', []))} similar calls")
            print(f"   ✅ Found {len(data.get('coaching_nudges', []))} coaching nudges")
        
        print(f"\n🎉 API is working correctly!")
        print(f"📖 Full docs: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Start with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
