#!/usr/bin/env python
"""Test script for creating a job using the MCP_cloudera create_job function"""

import os
import json
import dotenv
from src.functions.create_job import create_job

# Load environment variables from .env file
print("Loading environment variables from .env file...")
dotenv.load_dotenv()

# Get environment variables
host = os.environ.get("CLOUDERA_ML_HOST", "")
api_key = os.environ.get("CLOUDERA_ML_API_KEY", "")
project_id = os.environ.get("CLOUDERA_ML_PROJECT_ID", "9er0-ooi9-uopm-8i8o")  # Default from error message

print(f"Host URL: {host}")
print(f"Project ID: {project_id}")
print(f"API key is {'set' if api_key else 'not set'}")

# Configuration
config = {
    "host": host,
    "api_key": api_key,
    "project_id": project_id
}

# Test with minimal parameters (will use default runtime)
minimal_params = {
    "name": "Test Minimal Job",
    "script": "test.py"
}

# Test with a specific runtime
runtime_params = {
    "name": "Test Runtime Job",
    "script": "test.py",
    "runtime_identifier": "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-jupyterlab-python3.9-standard:2023.08.2-b8"
}

# Test with different runtime and resources
detailed_params = {
    "name": "Test Detailed Job",
    "script": "test.py",
    "kernel": "python3",
    "cpu": 2,
    "memory": 4,
    "nvidia_gpu": 0,
    "runtime_identifier": "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-jupyterlab-python3.9-cuda:2023.08.2-b8"
}

print("\n=== Testing create_job with minimal parameters (default runtime) ===")
result = create_job(config, minimal_params)
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
print(json.dumps(result, indent=2))
print("\n")

print("=== Testing create_job with specific runtime ===")
result = create_job(config, runtime_params)
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
print(json.dumps(result, indent=2))
print("\n")

print("=== Testing create_job with detailed parameters and CUDA runtime ===")
result = create_job(config, detailed_params)
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
print(json.dumps(result, indent=2)) 