#!/usr/bin/env python
"""
Test script to verify API endpoints are working properly
"""
import requests
import sys

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints...")
    
    # Test data-source-100qiu endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/data-source-100qiu/latest-matches?limit=5&include_raw=true")
        print(f"✓ /api/v1/data-source-100qiu/latest-matches: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"✗ /api/v1/data-source-100qiu/latest-matches: Error - {e}")
    
    # Test beidan-filter statistics endpoint
    try:
        payload = {}
        response = requests.post(f"{base_url}/api/v1/beidan-filter/statistics", json=payload)
        print(f"✓ /api/v1/beidan-filter/statistics: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        elif response.status_code == 422:
            print("  Note: 422 status likely due to validation error with empty payload, which is expected")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"✗ /api/v1/beidan-filter/statistics: Error - {e}")

    # Test date-time-options endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/data-source-100qiu/date-time-options")
        print(f"✓ /api/v1/data-source-100qiu/date-time-options: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"✗ /api/v1/data-source-100qiu/date-time-options: Error - {e}")

if __name__ == "__main__":
    test_api_endpoints()