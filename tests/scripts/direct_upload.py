#!/usr/bin/env python3
"""
Direct file upload script for Cloudera ML
"""

import os
import sys
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def format_host_url(host):
    """Format the host URL correctly"""
    host = host.strip()
    # Remove duplicate https:// if present
    if host.startswith("https://https://"):
        host = host.replace("https://https://", "https://")
    # Ensure URL has a scheme
    if not host.startswith(("http://", "https://")):
        host = "https://" + host
    # Remove trailing slash if present
    return host.rstrip("/")

def upload_file(host, api_key, project_id, file_path, relative_path):
    """Upload a single file"""
    print(f"Uploading {relative_path}...")
    
    # 1. First, check if file exists using direct API
    try:
        target_name = os.path.basename(file_path)
        file_exists_url = f"{host}/api/v2/projects/{project_id}/files"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(file_exists_url, headers=headers)
        response.raise_for_status()
        
        existing_files = response.json().get("files", [])
        for existing_file in existing_files:
            if existing_file.get("name") == target_name:
                print(f"  Skipping: {relative_path} (already exists)")
                return True
    except Exception as e:
        print(f"  Warning: Could not check if file exists: {str(e)}")
    
    # 2. Try different API endpoints for uploading
    endpoints = [
        f"{host}/api/v2/projects/{project_id}/files",
        f"{host}/api/v2/projects/{project_id}/files/content",
        f"{host}/api/v2/projects/{project_id}/files/upload"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"  Trying endpoint: {endpoint}")
            with open(file_path, "rb") as file:
                files = {"file": (os.path.basename(file_path), file)}
                response = requests.post(
                    endpoint,
                    headers={"Authorization": f"Bearer {api_key}"},
                    files=files
                )
                response.raise_for_status()
                print(f"  Success: {relative_path} (using {endpoint})")
                return True
        except Exception as e:
            print(f"  Failed with endpoint {endpoint}: {str(e)}")
    
    print(f"  Failed: {relative_path} - All endpoints failed")
    return False

def upload_folder(host, api_key, project_id, folder_path, ignore_folders=None):
    """Upload a folder recursively"""
    if ignore_folders is None:
        ignore_folders = ["node_modules", ".git", ".vscode", "dist", "out"]
    
    # Ensure the folder path exists
    folder_path_obj = Path(folder_path)
    if not folder_path_obj.exists() or not folder_path_obj.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return False
    
    # Format the host URL
    host = format_host_url(host)
    
    success_count = 0
    failed_count = 0
    
    # Walk through the folder and upload files
    for root, dirs, files in os.walk(folder_path):
        # Skip ignored folders
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            
            if upload_file(host, api_key, project_id, file_path, relative_path):
                success_count += 1
            else:
                failed_count += 1
    
    print(f"\nUpload summary:")
    print(f"  Success: {success_count} files")
    print(f"  Failed: {failed_count} files")
    
    return success_count > 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Direct file upload for Cloudera ML")
    parser.add_argument("--folder-path", required=True, help="Path to folder to upload")
    parser.add_argument("--project-id", required=True, help="Cloudera ML project ID")
    parser.add_argument("--host", help="Cloudera ML host URL")
    parser.add_argument("--api-key", help="Cloudera ML API key")
    parser.add_argument("--ignore-folders", help="Comma-separated list of folders to ignore")
    args = parser.parse_args()
    
    # Get configuration
    host = args.host or os.environ.get("CLOUDERA_ML_HOST", "")
    api_key = args.api_key or os.environ.get("CLOUDERA_ML_API_KEY", "")
    
    if not host or not api_key:
        print("Error: Missing host or API key")
        return 1
    
    ignore_folders = args.ignore_folders.split(",") if args.ignore_folders else None
    
    if upload_folder(host, api_key, args.project_id, args.folder_path, ignore_folders):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 