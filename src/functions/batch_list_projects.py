"""
Return a list of projects given a list of project IDs
"""
import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any, List

def batch_list_projects(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a list of projects given a list of project IDs
    
    Args:
        config: MCP configuration with host and api_key
        params: Parameters for the API call:
            - ids: List of project IDs to retrieve (required)
    
    Returns:
        Dict with success flag, message, and projects data
    """
    # Validate required parameters
    if "ids" not in params or not params["ids"]:
        return {"success": False, "message": "Missing required parameter: ids"}
    
    if not isinstance(params["ids"], list):
        return {"success": False, "message": "Parameter 'ids' must be a list of project IDs"}
    
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
    request_data = {"ids": params["ids"]}
    
    # Format request data as JSON
    request_data_json = json.dumps(request_data)
    
    # Debug print URLs
    api_url = f"{host}/api/v2/projects/batchList"
    print(f"Batch listing projects with URL: {api_url}")
    
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
        
        # Check if the curl command was successful
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to retrieve projects: {result.stderr}"
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
                "message": f"Successfully retrieved {len(response.get('projects', []))} projects",
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
            "message": f"Error retrieving projects: {str(e)}"
        } 