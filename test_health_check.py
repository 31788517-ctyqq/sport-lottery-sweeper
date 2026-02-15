#!/usr/bin/env python3
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health_check(source_id=1):
    """Test data source health check endpoint"""
    url = f"{BASE_URL}/api/v1/admin/sources/{source_id}/health"
    print(f"Testing health check at: {url}")
    
    # Try both GET and POST
    for method in ["GET", "POST"]:
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, timeout=10)
            
            print(f"\n{method} Response:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                print(f"  JSON Response: {data}")
                
                # Check structure
                if "success" in data:
                    print(f"  success: {data['success']}")
                if "data" in data:
                    print(f"  data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else type(data['data'])}")
                    if isinstance(data['data'], dict):
                        print(f"    status: {data['data'].get('status')}")
                        print(f"    message: {data['data'].get('message')}")
                        print(f"    response_time_ms: {data['data'].get('response_time_ms')}")
                
            except ValueError:
                print(f"  Response is not JSON: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"\n{method} Timeout after 10 seconds")
        except requests.exceptions.ConnectionError:
            print(f"\n{method} Connection Error - service may not be running")
            break
        except Exception as e:
            print(f"\n{method} Error: {e}")

if __name__ == "__main__":
    source_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    test_health_check(source_id)