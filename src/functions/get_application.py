"""Get application function for Cloudera ML MCP"""

import requests
from typing import Dict, Any


def get_application(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details of a specific application from a Cloudera ML project
    
    Args:
        config: MCP configuration with host and api_key
        params: Function parameters
            - application_id: ID of the application to get details for
            - project_id: ID of the project (optional if in config)
        
    Returns:
        Application details
    """
    try:
        # Validate required parameters
        application_id = params.get("application_id")
        if not application_id:
            return {"success": False, "message": "Missing required parameter: application_id"}
        
        # Get project_id from params or config
        project_id = params.get("project_id") or config.get("project_id")
        if not project_id:
            return {"success": False, "message": "Missing project_id in configuration or parameters"}
        
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
        
        # Build the URL for the GET request
        app_url = f"{host}/api/v2/projects/{project_id}/applications/{application_id}"
        print(f"Getting application details from: {app_url}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Make the request
        response = requests.get(app_url, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        application_data = response.json()
        
        return {
            "success": True,
            "message": f"Successfully retrieved application '{application_id}'",
            "application_id": application_id,
            "data": application_data
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"API request error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting application details: {str(e)}"
        } 