"""Upload folder function for Cloudera ML MCP"""

import os
from pathlib import Path
import requests
from typing import Dict, Any, List, Optional


def upload_folder(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload a folder to Cloudera ML
    
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
        
        # Setup headers
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        upload_results = {
            "success": [],
            "failed": []
        }
        
        # Function to recursively upload files
        def walk_and_upload(dir_path: Path):
            for item in dir_path.iterdir():
                # Skip ignored folders
                if item.is_dir() and item.name in ignore_folders:
                    continue
                
                # Process directories recursively
                if item.is_dir():
                    walk_and_upload(item)
                else:
                    try:
                        # Upload the file
                        relative_path = item.relative_to(folder_path_obj)
                        
                        # First upload the file
                        with open(item, "rb") as file:
                            files = {"file": (item.name, file)}
                            upload_url = f"{host}/api/v2/projects/{project_id}/files"
                            print(f"Uploading file: {relative_path} to {upload_url}")  # Debug output
                            response = requests.post(
                                upload_url, 
                                files=files,
                                headers={"Authorization": f"Bearer {config['api_key']}"}
                            )
                            response.raise_for_status()
                        
                        # Then update its metadata to preserve the path
                        metadata = {
                            "name": item.name,
                            "path": str(relative_path),
                            "type": "file"
                        }
                        
                        metadata_url = f"{host}/api/v2/projects/{project_id}/files/file"
                        print(f"Updating metadata for: {relative_path}")  # Debug output
                        response = requests.patch(
                            metadata_url,
                            json=metadata,
                            headers={
                                "Authorization": f"Bearer {config['api_key']}",
                                "Content-Type": "application/json"
                            }
                        )
                        response.raise_for_status()
                        
                        upload_results["success"].append(str(relative_path))
                    except Exception as e:
                        upload_results["failed"].append({
                            "file": str(item),
                            "error": str(e)
                        })
        
        # Start the upload process
        walk_and_upload(folder_path_obj)
        
        return {
            "success": True,
            "message": f"Upload completed. Successfully uploaded {len(upload_results['success'])} files.",
            "failed_count": len(upload_results["failed"]),
            "results": upload_results
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"API request error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error uploading folder: {str(e)}"
        } 