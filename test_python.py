#!/usr/bin/env python3
import sys
print("Python test script")
print("Version:", sys.version)
print("Path:", sys.path)
try:
    import fastapi
    print("fastapi imported successfully")
except ImportError as e:
    print("fastapi import failed:", e)