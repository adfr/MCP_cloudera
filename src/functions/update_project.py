"""Function to update a project in Cloudera ML."""

import json
import os
import subprocess
from urllib.parse import urlparse


def update_project(config, params=None):
    """
    Update a project in Cloudera ML.

    Args:
        config (dict): MCP configuration.
        params (dict, optional): Parameters for the API call. Default is None.
            - project_id (str, optional): ID of the project to update.
                If not provided, it will be taken from the configuration.
            - name (str, optional): New name for the project.
            - summary (str, optional): New summary for the project.
            - template (str, optional): New template for the project.
            - public (bool, optional): Whether the project should be public.
            - disable_git_repo (bool, optional): Whether to disable the Git repository.

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

    if not project_id:
        return {
            "success": False,
            "message": "project_id is required either in config or params",
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
    url = f"{host}/api/v2/projects/{project_id}"
    
    print(f"Accessing: {url}")

    # Prepare request data
    request_data = {}
    
    # Add optional parameters to request data
    for key in ['name', 'summary', 'template', 'public', 'disable_git_repo']:
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
                "message": f"Successfully updated project {project_id}",
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