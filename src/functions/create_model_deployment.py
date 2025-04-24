"""
Create a new model deployment in Cloudera ML
"""
import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any

def create_model_deployment(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new model deployment in Cloudera ML
    
    Args:
        config: MCP configuration with host and api_key
        params: Parameters for the API call:
            - project_id: ID of the project (required)
            - model_id: ID of the model to deploy (required)
            - build_id: ID of the model build to deploy (required)
            - name: Name of the deployment (required)
            - cpu: CPU cores (optional, default: 1)
            - memory: Memory in GB (optional, default: 2)
            - replica_count: Number of replicas (optional, default: 1)
            - min_replica_count: Minimum number of replicas (optional)
            - max_replica_count: Maximum number of replicas (optional)
            - nvidia_gpu: Number of GPUs (optional, default: 0)
            - environment_variables: Dictionary of environment variables (optional)
            - enable_auth: Whether to enable authentication (optional, default: true)
            - target_node_selector: Target node selector for the deployment (optional)
    
    Returns:
        Dict with success flag, message, and model deployment data
    """
    # Validate required parameters
    required_params = ["project_id", "model_id", "build_id", "name"]
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
    
    api_key = config.get("api_key")
    if not api_key:
        return {"success": False, "message": "Missing api_key in configuration"}
    
    # Build the request data
    request_data = {
        "name": params["name"],
        "build_id": params["build_id"]
    }
    
    # Add optional parameters if provided
    optional_params = {
        "cpu": "cpu",
        "memory": "memory",
        "replica_count": "replica_count",
        "min_replica_count": "min_replica_count",
        "max_replica_count": "max_replica_count",
        "nvidia_gpu": "nvidia_gpu",
        "environment_variables": "environment_variables",
        "enable_auth": "enable_auth",
        "target_node_selector": "target_node_selector"
    }
    
    for param_key, request_key in optional_params.items():
        if param_key in params and params[param_key] is not None:
            request_data[request_key] = params[param_key]
    
    # Format request data as JSON
    request_data_json = json.dumps(request_data)
    
    # Debug print URLs
    project_id = params["project_id"]
    model_id = params["model_id"]
    api_url = f"{host}/api/v2/projects/{project_id}/models/{model_id}/deployments"
    print(f"Creating model deployment with URL: {api_url}")
    
    # Construct curl command for API request
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
        
        # Check if the curl command was successful
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to create model deployment: {result.stderr}"
            }
        
        # Parse the response
        try:
            response = json.loads(result.stdout)
            
            # Check if there's an error in the response
            if "error" in response:
                return {
                    "success": False, 
                    "message": f"API error: {response.get('error', {}).get('message', 'Unknown error')}",
                    "details": response.get("error", {})
                }
            
            return {
                "success": True,
                "message": f"Successfully created deployment '{params['name']}' for model '{model_id}'",
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
            "message": f"Error creating model deployment: {str(e)}"
        } 