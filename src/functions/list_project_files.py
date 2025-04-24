"""Function to list files in a Cloudera ML project."""

import json
import requests
from urllib.parse import urlparse, quote


def list_project_files(config, params):
    """
    List files in a Cloudera ML project.

    Args:
        config (dict): MCP configuration.
        params (dict): Parameters for the API call.
            - project_id (str): ID of the project to list files from. Required.
            - path (str, optional): Path to list files from (relative to project root).
                Default is empty string (project root).

    Returns:
        dict: Response with the following structure:
            {
                "success": bool,
                "message": str,
                "data": list  # List of file objects if successful, otherwise None
            }
    """
    project_id = params.get('project_id')
    path = params.get('path', '')

    if not project_id:
        return {
            "success": False,
            "message": "project_id is required in params",
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

    # Fix URL formatting issues
    # First, remove any trailing slashes
    host = host.rstrip('/')
    
    # Then, ensure we have the correct scheme
    parsed_url = urlparse(host)
    if not parsed_url.scheme:
        # No scheme, add https://
        host = 'https://' + host
    elif host.startswith('http://'):
        # Convert http:// to https://
        host = 'https://' + host[7:]
    
    # Handle case where host might be incorrectly formatted with double scheme
    if parsed_url.netloc == '' and parsed_url.path.startswith('//'):
        # This handles cases like 'https://ml-a7716c71...'
        # where urlparse might not correctly parse the netloc
        parts = host.split('//')
        if len(parts) > 1:
            host = 'https://' + parts[-1]

    # Print the formatted host for debugging
    print(f"Formatted host: {host}")

    # Build the API URL
    url = f"{host}/api/v2/projects/{project_id}/files"
    if path:
        # Add query parameter for path with proper URL encoding
        url += f"?path={quote(path)}"
    
    print(f"Accessing: {url}")

    # Prepare headers for the request
    headers = {
        "Authorization": f"Bearer {config.get('api_key', '')}",
        "Content-Type": "application/json"
    }\

    # Make the API request using requests library
    try:
        # Verify that the URL starts with https:// and add it if it doesn't
        if not url.startswith("https://"):
            # Remove any leading http:// and any leading slashes
            url = url.lstrip("http://").lstrip("/")
            url = "https://" + url
        print(f"URL: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                data = response.json()
                return {
                    "success": True,
                    "message": "Successfully listed project files",
                    "data": data
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "message": f"Failed to parse response as JSON: {str(e)}",
                    "data": None
                }
        else:
            return {
                "success": False,
                "message": f"API request failed with status code {response.status_code}: {response.text}",
                "data": None
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Error making API request: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}",
            "data": None
        } 