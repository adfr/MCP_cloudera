"""
Create a run for an existing job in Cloudera ML
"""
import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any

def create_job_run(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a run for an existing job in Cloudera ML
    
    Args:
        config: MCP configuration with host and api_key
        params: Parameters for the API call:
            - project_id: ID of the project (required)
            - job_id: ID of the job to run (required)
            - runtime_identifier: Runtime identifier (optional)
            - environment_variables: Dictionary of environment variables (optional)
            - override_config: Dictionary with configuration overrides (optional)
    
    Returns:
        Dict with success flag, message, and job run data
    """
    # Debug prints
    print(f"config type: {type(config)}")
    print(f"config contents: {config}")
    print(f"params type: {type(params)}")
    print(f"params contents: {params}")
    
    # Validate required parameters
    required_params = ["project_id", "job_id"]
    missing_params = [p for p in required_params if p not in params or not params[p]]
    if missing_params:
        return {"success": False, "message": f"Missing required parameters: {', '.join(missing_params)}"}
    
    # Format host URL correctly
    host = config.get("host", "")
    if not host:
        return {"success": False, "message": "Missing host in configuration"}
    
    # Make sure host has the correct scheme
    parsed_url = urlparse(host)
    if not parsed_url.scheme:
        host = "https://" + host
    elif parsed_url.scheme and "://" in host[len(parsed_url.scheme)+3:]:
        # Fix potential double https:// in the URL
        host = parsed_url.scheme + "://" + host.split("://")[-1]
    
    # Remove trailing slash if present
    if host.endswith('/'):
        host = host[:-1]
    
    api_key = config.get("api_key")
    if not api_key:
        return {"success": False, "message": "Missing api_key in configuration"}
    
    # Build the request data
    request_data = {}
    
    # Add optional parameters if provided
    optional_params = {
        "runtime_identifier": "runtime_identifier",
        "environment_variables": "environment_variables",
        "override_config": "override_config"
    }
    
    for param_key, request_key in optional_params.items():
        if param_key in params and params[param_key] is not None:
            request_data[request_key] = params[param_key]
    
    # Format request data as JSON
    request_data_json = json.dumps(request_data)
    
    # Debug print URLs
    project_id = params["project_id"]
    job_id = params["job_id"]
    api_url = f"{host}/api/v2/projects/{project_id}/jobs/{job_id}/runs"
    print(f"Creating job run with URL: {api_url}")
    
    # Construct curl command
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", request_data_json,
        api_url
    ]
    
    try:
        # Execute curl command
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Debug the result
        print(f"curl result type: {type(result)}")
        print(f"curl returncode: {result.returncode}")
        print(f"curl stdout type: {type(result.stdout)}")
        print(f"curl stdout (first 200 chars): {result.stdout[:200]}")
        
        # Check if the curl command was successful
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to create job run: {result.stderr}"
            }
        
        # Parse the response
        try:
            print("Attempting to parse JSON response...")
            response = json.loads(result.stdout)
            print(f"Response parsed successfully. Type: {type(response)}")
            
            # Check if there's an error in the response
            if "error" in response:
                return {
                    "success": False, 
                    "message": f"API error: {response.get('error', {}).get('message', 'Unknown error')}",
                    "details": response.get("error", {})
                }
            
            return {
                "success": True,
                "message": f"Successfully created run for job '{job_id}'",
                "data": response
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": f"Failed to parse response: {result.stdout}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating job run: {str(e)}"
        } 