"""List applications function for Cloudera ML MCP"""

import requests
from typing import Dict, Any


def list_applications(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List applications in a Cloudera ML project
    
    Args:
        config (dict): MCP configuration containing host and api_key
        params (dict): Parameters for API call
            - project_id (str): ID of the project to list applications from
    
    Returns:
        dict: Response containing list of applications or error message
    """
    try:
        # Check if project_id is in params or config
        if 'project_id' not in params and 'project_id' not in config:
            return {
                'success': False,
                'message': 'Project ID is required but not provided in parameters or configuration'
            }
        
        project_id = params.get('project_id', config.get('project_id', ''))
        
        # Format host URL correctly
        host = config['host'].strip()
        # Remove duplicate https:// if present
        if host.startswith("https://https://"):
            host = host.replace("https://https://", "https://")
        # Ensure URL has a scheme
        if not host.startswith(("http://", "https://")):
            host = "https://" + host
        # Remove trailing slash if present
        host = host.rstrip("/")
        
        # Construct API URL - using v2 API instead of v1
        api_url = f"{host}/api/v2/projects/{project_id}/applications"
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        print(f"Making request to: {api_url}")  # Debug output
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        applications_data = response.json()
        applications = applications_data.get("applications", [])
        
        return {
            'success': True,
            'message': f"Found {len(applications)} applications",
            'applications': applications,
            'count': len(applications)
        }
    
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'API request error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error listing applications: {str(e)}'
        } 