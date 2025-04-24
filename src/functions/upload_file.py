"""Upload file function for Cloudera ML MCP"""

import os
import time
import requests
from typing import Dict, Any


def upload_file_to_root(host, api_key, project_id, file_path, target_name=None, target_dir=None):
    """
    Upload a file to the project using direct PUT request
    
    Args:
        host: CML host URL
        api_key: API key for authentication
        project_id: ID of the project to upload to
        file_path: Full path to the file to upload
        target_name: Optional name to use for the uploaded file (default: use original filename)
        target_dir: Optional directory to upload to (default: root directory)
        
    Returns:
        Success/failure status
    """
    try:
        # Get the target file name
        original_file_name = os.path.basename(file_path)
        target_file_name = target_name or original_file_name
        
        # Create the full target path (directory + filename)
        target_path = target_file_name
        if target_dir:
            # Ensure the directory path doesn't start or end with a slash
            target_dir = target_dir.strip('/')
            if target_dir:
                target_path = f"{target_dir}/{target_file_name}"
        
        # Setup the upload URL
        upload_url = f"{host}/api/v2/projects/{project_id}/files"
        
        # Set the authorization header
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        # Open the file to upload
        with open(file_path, 'rb') as file_data:
            # Create the form data with the target path as the field name
            files = {
                target_path: file_data
            }
            
            # Make the PUT request
            response = requests.put(
                upload_url,
                headers=headers,
                files=files
            )
        
        # Check the response
        if response.status_code in (200, 201, 202, 204):
            print(f"Successfully uploaded file: {target_path}")
            return True
        else:
            print(f"Failed to upload file: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error processing file upload: {str(e)}")
        return False


def upload_file(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload a single file to Cloudera ML
    
    Args:
        config: MCP configuration
        params: Function parameters
            - file_path: Local path to the file to upload
            - target_name: Optional name to use for the uploaded file
            - target_dir: Optional directory to upload to
            
    Returns:
        Upload results
    """
    try:
        # Validate parameters
        file_path = params.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")
            
        project_id = config.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project_id in configuration"
            }
        
        target_name = params.get("target_name")
        target_dir = params.get("target_dir")
        
        # Check if file exists
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise ValueError(f"{file_path} is not a valid file")
        
        # Properly format the host URL
        host = config['host'].strip()
        # Remove duplicate https:// if present
        if host.startswith("https://https://"):
            host = host.replace("https://https://", "https://")
        # Ensure URL has a scheme
        if not host.startswith(("http://", "https://")):
            host = "https://" + host
        # Remove trailing slash if present
        host = host.rstrip("/")
        
        # Upload the file
        print(f"Uploading file: {file_path}")
        success = upload_file_to_root(
            host=host,
            api_key=config['api_key'],
            project_id=project_id,
            file_path=file_path,
            target_name=target_name,
            target_dir=target_dir
        )
        
        # Create the full target path for the response
        target_filename = target_name or os.path.basename(file_path)
        target_path = target_filename
        if target_dir:
            target_dir = target_dir.strip('/')
            if target_dir:
                target_path = f"{target_dir}/{target_filename}"
        
        if success:
            return {
                "success": True,
                "message": f"Successfully uploaded file: {target_path}",
                "file_path": file_path,
                "target_name": target_filename,
                "target_dir": target_dir or "",
                "target_path": target_path
            }
        else:
            return {
                "success": False,
                "message": f"Failed to upload file: {target_path}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error uploading file: {str(e)}"
        } 