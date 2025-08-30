#!/usr/bin/env python3
"""
Test script to verify the full system functionality
"""
import requests
import json

def test_health():
    """Test backend health endpoint"""
    try:
        response = requests.get('http://localhost:5001/health')
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

def test_parse():
    """Test document parsing endpoint"""
    try:
        # Test with a simple text file upload simulation
        with open('/Users/minhphongle/Downloads/tokative/toktative-techjam/test_sample.txt', 'rb') as f:
            files = {'file': ('test_sample.txt', f, 'text/plain')}
            response = requests.post('http://localhost:5001/api/parse', files=files)
        
        print(f"Parse Status: {response.status_code}")
        print(f"Parse Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Parse test failed: {e}")
        return False

def test_analyze():
    """Test analysis endpoint"""
    try:
        response = requests.post('http://localhost:5001/api/analyze', 
                               json={
                                   'title': 'Test Document',
                                   'description': 'This is a test document about data processing and user privacy.'
                               })
        print(f"Analyze Status: {response.status_code}")
        print(f"Analyze Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Analyze test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Backend System ===")
    
    print("\n1. Testing Health Endpoint...")
    health_ok = test_health()
    
    print("\n2. Testing Parse Endpoint...")
    parse_ok = test_parse()
    
    print("\n3. Testing Analyze Endpoint...")
    analyze_ok = test_analyze()
    
    print("\n=== Summary ===")
    print(f"Health: {'✅' if health_ok else '❌'}")
    print(f"Parse: {'✅' if parse_ok else '❌'}")
    print(f"Analyze: {'✅' if analyze_ok else '❌'}")
    
    if all([health_ok, parse_ok, analyze_ok]):
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
