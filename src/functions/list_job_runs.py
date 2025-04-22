"""Function to list job runs in a Cloudera ML project."""

import json
import os
import subprocess
from urllib.parse import urlparse


def list_job_runs(config, params=None):
    """
    List job runs in a Cloudera ML project.

    Args:
        config (dict): MCP configuration.
        params (dict, optional): Parameters for the API call. Default is None.
            - project_id (str, optional): ID of the project to list job runs from.
                If not provided, it will be taken from the configuration.
            - job_id (str, optional): If provided, only list runs for this specific job.

    Returns:
        dict: Response with the following structure:
            {
                "success": bool,
                "message": str,
                "data": list  # List of job run objects if successful, otherwise None
            }
    """
    params = params or {}
    project_id = params.get('project_id') or config.get('project_id')
    job_id = params.get('job_id')

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
    if job_id:
        url = f"{host}/api/v2/projects/{project_id}/jobs/{job_id}/runs"
    else:
        # The generic endpoint doesn't seem to work, let the user know they need to provide a job ID
        return {
            "success": False,
            "message": "A job_id is required. The Cloudera ML API does not support listing all job runs without a specific job ID.",
            "data": None
        }

    print(f"Accessing: {url}")

    # Set up headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {config.get('api_key', '')}"
    }

    # Prepare the curl command
    curl_command = [
        'curl', '-s',
        '-X', 'GET',
        '-H', f"Authorization: Bearer {config.get('api_key', '')}",
        '-H', 'Content-Type: application/json',
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
                "message": "Successfully listed job runs",
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