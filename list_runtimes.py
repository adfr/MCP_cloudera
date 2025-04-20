#!/usr/bin/env python
"""Script to list available runtimes for Cloudera ML"""

import os
import json
import requests
import dotenv
from urllib.parse import urlparse

# Load environment variables
dotenv.load_dotenv()

# Get credentials
host = os.environ.get("CLOUDERA_ML_HOST", "")
api_key = os.environ.get("CLOUDERA_ML_API_KEY", "")

if not host or not api_key:
    print("Error: Missing host or API key. Please set CLOUDERA_ML_HOST and CLOUDERA_ML_API_KEY in .env file.")
    exit(1)

# Properly format the host URL
host = host.strip()
parsed_url = urlparse(host)
if not parsed_url.scheme:
    host = f"https://{host}"
if host.startswith("https://https://"):
    host = host.replace("https://https://", "https://")
host = host.rstrip("/")

print(f"Using host: {host}")

# Setup headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    # Try v2 API first
    url = f"{host}/api/v2/runtimes"
    print(f"Getting runtimes from: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 404:
        # Try fallback to v1 API
        url = f"{host}/api/v1/runtimes"
        print(f"V2 API not found, trying: {url}")
        response = requests.get(url, headers=headers)
    
    response.raise_for_status()
    runtimes = response.json()
    
    # Format and print runtimes
    if "runtimes" in runtimes:
        runtimes_list = runtimes["runtimes"]
        print(f"\nFound {len(runtimes_list)} runtimes:")
        for idx, runtime in enumerate(runtimes_list, 1):
            identifier = runtime.get("image_identifier") or runtime.get("runtime_identifier")
            edition = runtime.get("edition", "Unknown")
            r_type = runtime.get("image_type", "Unknown")
            desc = runtime.get("short_description", "No description")
            
            print(f"\n{idx}. Runtime: {identifier}")
            print(f"   Edition: {edition}")
            print(f"   Type: {r_type}")
            print(f"   Description: {desc}")
            
        print("\n\nExample runtime identifier to use in create_job:")
        if runtimes_list:
            example = runtimes_list[0].get("image_identifier") or runtimes_list[0].get("runtime_identifier")
            print(f'runtime_identifier="{example}"')
    else:
        print("No runtimes found in response:")
        print(json.dumps(runtimes, indent=2))
    
except requests.exceptions.RequestException as e:
    print(f"Error making request: {str(e)}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_details = e.response.json()
            print(f"Error details: {json.dumps(error_details, indent=2)}")
        except:
            print(f"Status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
except Exception as e:
    print(f"Unexpected error: {str(e)}") 