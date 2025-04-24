"""Function to log metrics and parameters for multiple experiment runs in a batch."""

import json
import os
import subprocess
from urllib.parse import urlparse


def log_experiment_run_batch(config, params=None):
    """
    Log metrics and parameters for multiple experiment runs in a batch.

    Args:
        config (dict): MCP configuration.
        params (dict, optional): Parameters for the API call. Default is None.
            - project_id (str, optional): ID of the project.
                If not provided, it will be taken from the configuration.
            - experiment_id (str): ID of the experiment containing the runs.
            - run_updates (list): List of run update objects, each containing:
                - id (str): ID of the run to update
                - metrics (dict, optional): Dictionary of metrics to log
                - parameters (dict, optional): Dictionary of parameters to log
                - tags (list, optional): List of tags to add to the run

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
    run_updates = params.get('run_updates', [])

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

    if not run_updates:
        return {
            "success": False,
            "message": "run_updates list is required and cannot be empty",
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
    url = f"{host}/api/v2/projects/{project_id}/experiments/{experiment_id}/run-batch"
    
    print(f"Accessing: {url}")

    # Prepare the request payload
    payload = json.dumps({"runs": run_updates})

    # Prepare the curl command
    curl_command = [
        'curl', '-s',
        '-X', 'POST',
        '-H', f"Authorization: Bearer {config.get('api_key', '')}",
        '-H', 'Content-Type: application/json',
        '-d', payload,
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
                "message": "Successfully logged batch updates to experiment runs",
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