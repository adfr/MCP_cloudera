"""List applications function for Cloudera ML MCP"""

import os
import json
import subprocess
from urllib.parse import urlparse
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
    # Check if project_id is in params or config
    if 'project_id' not in params and 'project_id' not in config:
        return {
            'success': False,
            'message': 'Project ID is required but not provided in parameters or configuration'
        }
    
    project_id = params.get('project_id', config.get('project_id', ''))
    
    # Format host URL
    host = config['host']
    parsed_url = urlparse(host)
    
    # Ensure the URL has the correct scheme
    if not parsed_url.scheme:
        host = f"https://{host}"
    elif host.startswith('https://https://'):
        host = host.replace('https://https://', 'https://')
    
    # Construct API URL
    api_url = f"{host}/api/v1/projects/{project_id}/applications"
    
    # Set up headers
    headers = [
        '-H', f'Authorization: ApiKey {config["api_key"]}',
        '-H', 'Content-Type: application/json'
    ]
    
    # Construct curl command
    curl_command = ['curl', '-s', '-X', 'GET']
    curl_command.extend(headers)
    curl_command.append(api_url)
    
    try:
        # Execute the curl command
        process = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if the command was successful
        if process.returncode != 0:
            return {
                'success': False,
                'message': f'Failed to list applications: {process.stderr}'
            }
        
        # Parse the response
        try:
            response = json.loads(process.stdout)
            return {
                'success': True,
                'data': response
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'message': f'Invalid JSON response: {process.stdout}'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error listing applications: {str(e)}'
        } 