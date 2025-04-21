"""Function to update an application in a Cloudera ML project."""

import json
import os
import subprocess
from urllib.parse import urlparse


def update_application(config, params=None):
    """
    Update an application in a Cloudera ML project.

    Args:
        config (dict): MCP configuration.
        params (dict, optional): Parameters for the API call. Default is None.
            - project_id (str, optional): ID of the project.
                If not provided, it will be taken from the configuration.
            - application_id (str): ID of the application to update.
            - name (str, optional): New name for the application.
            - description (str, optional): New description for the application.
            - cpu (int, optional): New CPU cores allocation.
            - memory (int, optional): New memory allocation in GB.
            - nvidia_gpu (int, optional): New GPU allocation.
            - environment_variables (dict, optional): New environment variables.
            - runtime_identifier (str, optional): New runtime identifier.

    Returns:
        dict: Response with the following structure:
            {
                "success": bool,
                "message": str,
                "data": dict  # Result data if successful, otherwise None
            }
    """
    params = params or {}
    project_id = params.get('project_id') or config.get('project_id')
    application_id = params.get('application_id')

    if not project_id:
        return {
            "success": False,
            "message": "project_id is required either in config or params",
            "data": None
        }

    if not application_id:
        return {
            "success": False,
            "message": "application_id is required in params",
            "data": None
        }

    # Format host URL
    host = config.get('host', '')
    if not host:
        return {
            "success": False,
            "message": "host is required in config",
            "data": None
        }

    # Ensure the host has the correct scheme and no trailing slash
    parsed_url = urlparse(host)
    if not parsed_url.scheme:
        host = 'https://' + host
    elif host.startswith('http://'):
        host = 'https://' + host[7:]

    host = host.rstrip('/')

    # Build the API URL
    url = f"{host}/api/v2/projects/{project_id}/applications/{application_id}"
    
    print(f"Accessing: {url}")

    # Prepare request data
    request_data = {}
    
    # Add optional parameters to request data
    for key in ['name', 'description', 'cpu', 'memory', 'nvidia_gpu', 'environment_variables', 'runtime_identifier']:
        if params.get(key) is not None:
            request_data[key] = params[key]
    
    # Prepare the curl command
    curl_command = [
        'curl', '-s',
        '-X', 'PATCH',
        '-H', f"Authorization: Bearer {config.get('api_key', '')}",
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(request_data),
        url
    ]

    # Execute the curl command
    try:
        response = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=False
        )

        if response.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to execute curl command: {response.stderr}",
                "data": None
            }

        try:
            data = json.loads(response.stdout)
            return {
                "success": True,
                "message": f"Successfully updated application {application_id}",
                "data": data
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": f"Failed to parse response as JSON: {response.stdout}",
                "data": None
            }
    except subprocess.SubprocessError as e:
        return {
            "success": False,
            "message": f"Failed to execute curl command: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}",
            "data": None
        } 