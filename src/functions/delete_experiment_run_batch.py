"""
Delete multiple experiment runs in Cloudera ML
"""
import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any, List

def delete_experiment_run_batch(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete multiple experiment runs in Cloudera ML
    
    Args:
        config: MCP configuration with host and api_key
        params: Parameters for the API call:
            - project_id: ID of the project (required)
            - experiment_id: ID of the experiment (required)
            - run_ids: List of run IDs to delete (required)
    
    Returns:
        Dict with success flag, message, and deletion results
    """
    # Validate required parameters
    required_params = ["project_id", "experiment_id", "run_ids"]
    missing_params = [p for p in required_params if p not in params or not params[p]]
    if missing_params:
        return {"success": False, "message": f"Missing required parameters: {', '.join(missing_params)}"}
    
    # Make sure run_ids is a list
    run_ids = params["run_ids"]
    if not isinstance(run_ids, list) or not run_ids:
        return {"success": False, "message": "run_ids must be a non-empty list of experiment run IDs"}
    
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
    experiment_id = params["experiment_id"]
    api_url = f"{host}/api/v2/projects/{project_id}/experiments/{experiment_id}/runs-batch"
    print(f"Deleting experiment runs batch with URL: {api_url}")
    
    # Prepare the JSON payload with run IDs
    request_data = {
        "ids": run_ids
    }
    
    # Construct curl command for deletion
    curl_cmd = [
        "curl", "-s", "-X", "DELETE",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(request_data),
        api_url
    ]
    
    try:
        # Execute curl command
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Check if the curl command was successful
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to delete experiment runs: {result.stderr}"
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
                    "message": f"Successfully deleted {len(run_ids)} experiment runs",
                    "data": response
                }
            except json.JSONDecodeError:
                # If the response is not JSON, it might be empty for a successful deletion
                pass
        
        # If we got here, the deletion was likely successful but returned no content
        return {
            "success": True,
            "message": f"Successfully deleted {len(run_ids)} experiment runs"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting experiment runs: {str(e)}"
        } 