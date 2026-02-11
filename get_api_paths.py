import urllib.request
import json

def get_api_paths():
    try:
        response = urllib.request.urlopen('http://localhost:8001/openapi.json', timeout=30)
        data = json.loads(response.read().decode('utf-8'))
        
        print("Available API paths:")
        for path in sorted(data['paths'].keys()):
            if 'log' in path.lower():
                print(f"  {path}")
                
    except Exception as e:
        print(f"Error fetching API paths: {e}")
        
if __name__ == "__main__":
    get_api_paths()