"""Get model function for Cloudera ML MCP"""

import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any


def get_model(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details of a model from Cloudera ML
    
    Args:
        config (dict): MCP configuration containing host and api_key
        params (dict): Parameters for API call
            - model_id (str): ID of the model to retrieve
            - project_id (str): ID of the project containing the model
    
    Returns:
        dict: Response containing model details or error message
    """
    # Validate parameters
    if 'model_id' not in params:
        return {
            'success': False,
            'message': 'Model ID is required'
        }
    
    model_id = params['model_id']
    
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
    api_url = f"{host}/api/v1/projects/{project_id}/models/{model_id}"
    
    # Set up headers
    headers = [
        '-H', f'Authorization: Bearer {config["api_key"]}',
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
                'message': f'Failed to get model: {process.stderr}'
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
            'message': f'Error getting model: {str(e)}'
        } 