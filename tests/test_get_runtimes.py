#!/usr/bin/env python
"""Test script for the get_runtimes function"""

import os
import json
import dotenv
from src.functions.get_runtimes import get_runtimes

# Load environment variables from .env file
print("Loading environment variables from .env file...")
dotenv.load_dotenv()

# Get environment variables
host = os.environ.get("CLOUDERA_ML_HOST", "")
api_key = os.environ.get("CLOUDERA_ML_API_KEY", "")

print(f"Host URL: {host}")
print(f"API key is {'set' if api_key else 'not set'}")

# Configuration
config = {
    "host": host,
    "api_key": api_key,
}

# Call the get_runtimes function
print("\n=== Retrieving available runtimes ===")
result = get_runtimes(config, {})

# Display results
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")

if result['success'] and 'runtimes' in result:
    print("\nAvailable runtimes:")
    for idx, runtime in enumerate(result['runtimes'], 1):
        print(f"\n{idx}. Runtime: {runtime.get('identifier')}")
        print(f"   Edition: {runtime.get('edition')}")
        print(f"   Type: {runtime.get('type')}")
        print(f"   Description: {runtime.get('description')}")
    
    print(f"\nTotal runtimes: {result.get('count', 0)}")
    
    if result.get('runtimes'):
        first_runtime = result['runtimes'][0]['identifier']
        print("\nExample for creating a job with the first runtime:")
        print(f'mcp.create_job("My Job", "script.py", runtime_identifier="{first_runtime}")')
else:
    print("\nError details:")
    print(json.dumps(result, indent=2)) 