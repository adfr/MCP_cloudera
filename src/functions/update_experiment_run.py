"""Function to update an experiment run in a Cloudera ML project."""

import json
import os
import subprocess
from urllib.parse import urlparse


def update_experiment_run(config, params=None):
    """
    Update an experiment run in a Cloudera ML project.

    Args:
        config (dict): MCP configuration.
        params (dict, optional): Parameters for the API call. Default is None.
            - project_id (str, optional): ID of the project.
                If not provided, it will be taken from the configuration.
            - experiment_id (str): ID of the experiment containing the run.
            - run_id (str): ID of the experiment run to update.
            - name (str, optional): New name for the experiment run.
            - description (str, optional): New description for the experiment run.
            - metrics (dict, optional): New metrics to set for the experiment run.
            - parameters (dict, optional): New parameters to set for the experiment run.
            - tags (list, optional): New tags to set for the experiment run.

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
    experiment_id = params.get('experiment_id')
    run_id = params.get('run_id')

    if not project_id:
        return {
            "success": False,
            "message": "project_id is required either in config or params",
            "data": None
        }

    if not experiment_id:
        return {
            "success": False,
            "message": "experiment_id is required in params",
            "data": None
        }

    if not run_id:
        return {
            "success": False,
            "message": "run_id is required in params",
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
    url = f"{host}/api/v2/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}"
    
    print(f"Accessing: {url}")

    # Prepare request data
    request_data = {}
    
    # Add optional parameters to request data
    for key in ['name', 'description', 'metrics', 'parameters', 'tags']:
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
                "message": f"Successfully updated experiment run {run_id}",
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