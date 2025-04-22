"""
Delete an application in Cloudera ML
"""
import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any

def delete_application(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete an application in Cloudera ML
    
    Args:
        config: MCP configuration with host and api_key
        params: Parameters for the API call:
            - project_id: ID of the project (required)
            - application_id: ID of the application to delete (required)
    
    Returns:
        Dict with success flag and message
    """
    # Validate required parameters
    required_params = ["project_id", "application_id"]
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
    
    # Build the URL for the delete request
    project_id = params["project_id"]
    application_id = params["application_id"]
    api_url = f"{host}/api/v2/projects/{project_id}/applications/{application_id}"
    print(f"Deleting application with URL: {api_url}")
    
    # Construct curl command
    curl_cmd = [
        "curl", "-s", "-X", "DELETE",
        "-H", f"Authorization: Bearer {api_key}",
        api_url
    ]
    
    try:
        # Execute curl command
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Check if the curl command was successful
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to delete application: {result.stderr}"
            }
        
        # Parse the response if there is any content
        if result.stdout.strip():
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
                    "message": f"Successfully deleted application '{application_id}'",
                    "data": response
                }
            except json.JSONDecodeError:
                # If the response is not JSON, it might be empty for a successful deletion
                pass
        
        # If we got here, the deletion was likely successful but returned no content
        return {
            "success": True,
            "message": f"Successfully deleted application '{application_id}'"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting application: {str(e)}"
        } 