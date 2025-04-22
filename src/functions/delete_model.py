"""Delete model function for Cloudera ML MCP"""

import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any


def delete_model(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a model by ID
    
    Args:
        config: MCP configuration with host and api_key
        params: Function parameters
            - model_id: ID of the model to delete
            - project_id: ID of the project containing the model (optional if in config)
        
    Returns:
        Delete operation results
    """
    # Validate required parameters
    model_id = params.get("model_id")
    if not model_id:
        return {"success": False, "message": "Missing required parameter: model_id"}
    
    # Get project_id from params or config
    project_id = params.get("project_id") or config.get("project_id")
    if not project_id:
        return {"success": False, "message": "Missing project_id in configuration or parameters"}
    
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
    
    # First, try to get the model details to include in the response
    model_url = f"{host}/api/v2/projects/{project_id}/models/{model_id}"
    print(f"Getting model details from: {model_url}")
    
    # Construct curl command for getting model details
    get_model_cmd = [
        "curl", "-s",
        "-H", f"Authorization: Bearer {api_key}",
        model_url
    ]
    
    model_name = f"Model ID {model_id}"
    try:
        # Execute curl command to get model details
        model_result = subprocess.run(get_model_cmd, capture_output=True, text=True)
        
        # If successful, parse the model name
        if model_result.returncode == 0 and model_result.stdout.strip():
            try:
                model_info = json.loads(model_result.stdout)
                model_name = model_info.get("name", model_name)
            except json.JSONDecodeError:
                # If we can't parse the response, continue with deletion anyway
                pass
    except Exception:
        # If we can't get the model details, continue with deletion anyway
        pass
    
    # Build the URL for the delete request
    delete_url = f"{host}/api/v2/projects/{project_id}/models/{model_id}"
    print(f"Deleting model with URL: {delete_url}")
    
    # Construct curl command for deletion
    curl_cmd = [
        "curl", "-s", "-X", "DELETE",
        "-H", f"Authorization: Bearer {api_key}",
        delete_url
    ]
    
    try:
        # Execute curl command
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Check if the curl command was successful
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to delete model: {result.stderr}"
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
                    "message": f"Successfully deleted model '{model_name}'",
                    "model_id": model_id,
                    "data": response
                }
            except json.JSONDecodeError:
                # If the response is not JSON, it might be empty for a successful deletion
                pass
        
        # If we got here, the deletion was likely successful but returned no content
        return {
            "success": True,
            "message": f"Successfully deleted model '{model_name}'",
            "model_id": model_id
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting model: {str(e)}"
        } 