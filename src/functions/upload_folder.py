"""Upload folder function for Cloudera ML MCP"""

import os
import json
import time
import datetime
from pathlib import Path
import requests
from typing import Dict, Any, List, Optional
import cmlapi


def setup_client(host, api_key):
    """
    Setup the CML API client
    
    Args:
        host: CML host URL
        api_key: API key for authentication
        
    Returns:
        Configured CML API client
    """
    # Properly format the host URL
    host = host.strip()
    # Remove duplicate https:// if present
    if host.startswith("https://https://"):
        host = host.replace("https://https://", "https://")
    # Ensure URL has a scheme
    if not host.startswith(("http://", "https://")):
        host = "https://" + host
    # Remove trailing slash if present
    host = host.rstrip("/")
    
    config = cmlapi.Configuration()
    config.host = host
    api_client = cmlapi.ApiClient(config)
    api_client.set_default_header("authorization", f"Bearer {api_key}")
    return cmlapi.CMLServiceApi(api_client)


def delete_file_if_exists(client, project_id, file_path):
    """
    Try to delete a file if it exists to avoid conflicts
    
    Args:
        client: CML API client
        project_id: ID of the project
        file_path: Path of the file to delete
    """
    try:
        client.delete_project_file(project_id=project_id, path=file_path)
        print(f"Deleted existing file: {file_path}")
        # Add a small delay to ensure the deletion is processed
        time.sleep(0.5)
    except Exception:
        # File might not exist, which is fine
        pass


def upload_file_to_project(host, api_key, project_id, file_path, relative_path):
    """
    Upload a single file to Cloudera ML using direct PUT request
    
    Args:
        host: CML host URL
        api_key: API key for authentication
        project_id: ID of the project to upload to
        file_path: Full path to the file to upload
        relative_path: Relative path within the project structure
        
    Returns:
        Success/failure status
    """
    try:
        # Convert relative path to string if it's a Path object
        target_path = str(relative_path)
        
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
        print(f"Error uploading {file_path}: {str(e)}")
        return False


def upload_folder(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload a folder to Cloudera ML using direct PUT request
    
    Args:
        config: MCP configuration
        params: Function parameters
            - folder_path: Local path to the folder to upload
            - ignore_folders: Optional list of folders to ignore
            
    Returns:
        Upload results
    """
    try:
        # Validate parameters
        folder_path = params.get("folder_path")
        if not folder_path:
            raise ValueError("folder_path is required")
            
        project_id = config.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project_id in configuration"
            }
        
        # Default ignored folders if not specified
        ignore_folders = params.get("ignore_folders") or ["node_modules", ".git", ".vscode", "dist", "out"]
        
        # Check if folder exists
        folder_path_obj = Path(folder_path)
        if not folder_path_obj.exists() or not folder_path_obj.is_dir():
            raise ValueError(f"{folder_path} is not a valid directory")
        
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
        
        successful_uploads = []
        failed_uploads = []
        
        # Walk through the directory structure and upload files
        for root, dirs, files in os.walk(folder_path):
            # Skip ignored folders - this modifies dirs in place to avoid walking into them
            dirs[:] = [d for d in dirs if d not in ignore_folders]
            
            for file in files:
                # Get the full path and relative path
                full_path = os.path.join(root, file)
                relative_path = Path(full_path).relative_to(folder_path_obj)
                
                # Upload the file using direct PUT
                print(f"Processing file: {relative_path}")
                success = upload_file_to_project(
                    host=host,
                    api_key=config['api_key'],
                    project_id=project_id,
                    file_path=full_path,
                    relative_path=relative_path
                )
                
                if success:
                    successful_uploads.append(str(relative_path))
                else:
                    failed_uploads.append({
                        "file": str(relative_path),
                        "error": "Failed to upload file"
                    })
                
                # Add a small delay between uploads to prevent rate limiting
                time.sleep(0.5)
        
        return {
            "success": True,
            "message": f"Upload completed. Successfully uploaded {len(successful_uploads)} files.",
            "failed_count": len(failed_uploads),
            "successful_count": len(successful_uploads),
            "results": {
                "success": successful_uploads,
                "failed": failed_uploads
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error uploading folder: {str(e)}"
        } 