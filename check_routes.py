#!/usr/bin/env python
"""
Script to check registered routes in the backend application
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_routes():
    try:
        # Import the main app
        from backend.main import app
        print("Registered routes:")
        
        # Print all routes
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                print(f"  {route.methods} {route.path}")
            else:
                print(f"  {route}")
        
        print("\nSearching specifically for beidan-filter routes:")
        for route in app.routes:
            if hasattr(route, 'path') and 'beidan-filter' in route.path:
                print(f"  {route.methods} {route.path}")
                
    except Exception as e:
        print(f"Error checking routes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_routes()