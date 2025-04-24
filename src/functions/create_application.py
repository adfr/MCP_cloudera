"""Create application function for Cloudera ML MCP"""

import requests
import json
from typing import Dict, Any


def create_application(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new application in a Cloudera ML project
    
    Args:
        config: MCP configuration with host and api_key
        params: Function parameters
            - project_id: ID of the project (required)
            - name: Name of the application (required)
            - description: Description of the application (optional)
            - script: Script to run in the application (required)
            - cpu: CPU cores (optional, default: 1)
            - memory: Memory in GB (optional, default: 1)
            - nvidia_gpu: Number of GPUs (optional, default: 0)
            - runtime_identifier: Runtime identifier (optional)
            - environment_variables: Environment variables as dict (optional)
        
    Returns:
        Application creation results
    """
    try:
        # Validate required parameters
        required_params = ["project_id", "name", "script"]
        missing_params = [p for p in required_params if p not in params or not params[p]]
        if missing_params:
            return {"success": False, "message": f"Missing required parameters: {', '.join(missing_params)}"}
            
        # Format host URL correctly
        host = config.get("host", "").strip()
        # Remove duplicate https:// if present
        if host.startswith("https://https://"):
            host = host.replace("https://https://", "https://")
        # Ensure URL has a scheme
        if not host.startswith(("http://", "https://")):
            host = "https://" + host
        # Remove trailing slash if present
        host = host.rstrip("/")
        
        api_key = config.get("api_key")
        if not api_key:
            return {"success": False, "message": "Missing api_key in configuration"}
            
        # Prepare request payload
        payload = {
            "name": params["name"],
            "script": params["script"]
        }
        
        # Add optional parameters
        if "description" in params:
            payload["description"] = params["description"]
        
        if "cpu" in params:
            payload["cpu"] = params["cpu"]
        else:
            payload["cpu"] = 1
            
        if "memory" in params:
            payload["memory"] = params["memory"]
        else:
            payload["memory"] = 1
            
        if "nvidia_gpu" in params:
            payload["nvidia_gpu"] = params["nvidia_gpu"]
        else:
            payload["nvidia_gpu"] = 0
            
        if "runtime_identifier" in params:
            payload["runtime_identifier"] = params["runtime_identifier"]
            
        if "environment_variables" in params and params["environment_variables"]:
            payload["environment_variables"] = params["environment_variables"]
            
        # Build the URL for the POST request
        project_id = params["project_id"]
        api_url = f"{host}/api/v2/projects/{project_id}/applications"
        print(f"Creating application with URL: {api_url}")
        print(f"Application payload: {json.dumps(payload, indent=2)}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Make the request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse the response
        application_data = response.json()
        
        return {
            "success": True,
            "message": f"Successfully created application '{params['name']}'",
            "data": application_data
        }
        
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        response_body = ""
        if hasattr(e, 'response') and e.response is not None:
            try:
                response_body = e.response.json()
                error_message = f"{error_message} - {json.dumps(response_body)}"
            except:
                if hasattr(e.response, 'text'):
                    response_body = e.response.text
                    error_message = f"{error_message} - {response_body}"
        
        return {
            "success": False,
            "message": f"API request error: {error_message}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating application: {str(e)}"
        } 