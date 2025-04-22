"""Get experiment run function for Cloudera ML MCP"""

import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any


def get_experiment_run(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details of a specific experiment run from a Cloudera ML project
    
    Args:
        config: MCP configuration with host and api_key
        params: Function parameters
            - experiment_id: ID of the experiment containing the run
            - run_id: ID of the experiment run to get details for 
            - project_id: ID of the project (optional if in config)
        
    Returns:
        Experiment run details
    """
    # Validate required parameters
    if not params.get("experiment_id"):
        return {"success": False, "message": "experiment_id is required"}
    
    if not params.get("run_id"):
        return {"success": False, "message": "run_id is required"}
    
    if not params.get("project_id"):
        if not config.get("project_id"):
            return {"success": False, "message": "project_id is required either in config or params"}
        params["project_id"] = config.get("project_id")
    
    # Format host URL
    host = config.get("host", "")
    parsed_url = urlparse(host)
    
    # Ensure the host has the correct scheme
    if not parsed_url.scheme:
        host = f"https://{host}"
    elif "https://" in parsed_url.netloc:
        # Handle cases where the host already contains https:// in the netloc
        host = f"{parsed_url.scheme}://{parsed_url.netloc.replace('https://', '')}{parsed_url.path}"
    
    # Construct API URL
    url = f"{host}/api/v2/projects/{params['project_id']}/experiments/{params['experiment_id']}/runs/{params['run_id']}"
    
    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.get('api_key', '')}"
    }
    
    # Construct curl command
    curl_command = [
        "curl", "-s", "-X", "GET",
        "-H", f"Content-Type: {headers['Content-Type']}",
        "-H", f"Authorization: {headers['Authorization']}",
        url
    ]
    
    print(f"DEBUG: Accessing URL: {url}")
    
    try:
        # Execute curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)
        
        # Check if the command was successful
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                return {
                    "success": True,
                    "data": response_data
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "message": "Failed to parse API response",
                    "raw_response": result.stdout
                }
        else:
            return {
                "success": False,
                "message": f"API request failed with status code {result.returncode}",
                "error": result.stderr
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error executing request: {str(e)}"
        } 