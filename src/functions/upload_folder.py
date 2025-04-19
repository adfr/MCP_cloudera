"""Upload folder function for Cloudera ML MCP"""

import os
from pathlib import Path
import requests
from typing import Dict, Any, List, Optional

from .. import utils


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
        
        ignore_folders = params.get("ignore_folders") or ["node_modules", ".git", ".vscode", "dist", "out"]
        
        # Check if folder exists
        folder_path_obj = Path(folder_path)
        if not folder_path_obj.exists() or not folder_path_obj.is_dir():
            raise ValueError(f"{folder_path} is not a valid directory")
        
        session = utils.get_session(config)
        project_id = config["project_id"]
        
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
                            upload_url = utils.format_url(
                                config, f"/api/v2/projects/{project_id}/files"
                            )
                            response = session.post(upload_url, files=files)
                            response.raise_for_status()
                        
                        # Then update its metadata to preserve the path
                        metadata = {
                            "name": item.name,
                            "path": str(relative_path),
                            "type": "file"
                        }
                        
                        metadata_url = utils.format_url(
                            config, f"/api/v2/projects/{project_id}/files/file"
                        )
                        response = session.patch(
                            metadata_url,
                            json=metadata,
                            headers={"Content-Type": "application/json"}
                        )
                        response.raise_for_status()
                        
                        upload_results["success"].append(str(relative_path))
                    except Exception as e:
                        error_message = utils.handle_error(e)
                        upload_results["failed"].append({
                            "file": str(item),
                            "error": error_message
                        })
        
        # Start the upload process
        walk_and_upload(folder_path_obj)
        
        return {
            "success": True,
            "message": f"Upload completed. Successfully uploaded {len(upload_results['success'])} files.",
            "failed_count": len(upload_results["failed"]),
            "results": upload_results
        }
    except Exception as e:
        return {
            "success": False,
            "message": utils.handle_error(e)
        } 