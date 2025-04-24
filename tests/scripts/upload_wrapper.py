#!/usr/bin/env python3
"""
Simple wrapper script to upload folders to Cloudera ML projects
"""

import os
import sys
import subprocess
import json
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Upload folder to Cloudera ML project")
    parser.add_argument("--folder-path", required=True, help="Path to folder to upload")
    parser.add_argument("--project-id", required=True, help="Cloudera ML project ID")
    parser.add_argument("--host", help="Cloudera ML host URL")
    parser.add_argument("--api-key", help="Cloudera ML API key")
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    # Get configuration
    host = args.host or os.environ.get("CLOUDERA_ML_HOST", "")
    api_key = args.api_key or os.environ.get("CLOUDERA_ML_API_KEY", "")
    project_id = args.project_id
    folder_path = args.folder_path
    
    if not host or not api_key:
        print("Error: Missing host or API key")
        return 1
    
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        return 1
    
    # Format host URL correctly
    host = host.strip()
    # Remove duplicate https:// if present
    if host.startswith("https://https://"):
        host = host.replace("https://https://", "https://")
    # Ensure URL has a scheme
    if not host.startswith(("http://", "https://")):
        host = "https://" + host
    # Remove trailing slash if present
    host = host.rstrip("/")
    
    # Call the original upload_files.py with the correct Python environment
    upload_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "upload_files.py")
    
    # Create a temporary script
    temp_script = """
import os
import sys
import subprocess

# Command to use for upload
command = f'cd {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))} && ' + \
          f'python -c "' + \
          f'import sys; sys.path.append(\\\\\\"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/cml_api/lib/python3.13/site-packages\\\\\\"); ' + \
          f'import os; ' + \
          f'from pathlib import Path; ' + \
          f'import cmlapi; ' + \
          f'def setup_client(host, api_key): ' + \
          f'    config = cmlapi.Configuration(); ' + \
          f'    config.host = host; ' + \
          f'    api = cmlapi.ApiClient(config); ' + \
          f'    api.set_default_header(\\\\\\\"authorization\\\\\\\", f\\\\\\\"Bearer {{api_key}}\\\\\\\"); ' + \
          f'    return cmlapi.CMLServiceApi(api); ' + \
          f'client = setup_client(\\\\\\"{host}\\\\\\", \\\\\\"{api_key}\\\\\\"); ' + \
          f'for root, dirs, files in os.walk(\\\\\\"{folder_path}\\\\\\"): ' + \
          f'    for file in files: ' + \
          f'        full_path = os.path.join(root, file); ' + \
          f'        rel_path = Path(full_path).relative_to(Path(\\\\\\"{folder_path}\\\\\\")); ' + \
          f'        print(f\\\\\\\"Uploading {{rel_path}}...\\\\\\\"); ' + \
          f'        try: ' + \
          f'            client.upload_file(project_id=\\\\\\"{project_id}\\\\\\", file=full_path); ' + \
          f'            metadata = {{\\\\\\\"name\\\\\\\": file, \\\\\\\"path\\\\\\\": str(os.path.dirname(rel_path)) if os.path.dirname(rel_path) else \\\\\\\"\\\\\\\", \\\\\\\"type\\\\\\\": \\\\\\\"file\\\\\\\"}}; ' + \
          f'            client.update_project_file_metadata(project_id=\\\\\\"{project_id}\\\\\\", path=\\\\\\\"file\\\\\\\", body=metadata); ' + \
          f'            print(f\\\\\\\"  Success: {{rel_path}}\\\\\\\"); ' + \
          f'        except Exception as e: ' + \
          f'            print(f\\\\\\\"  Failed: {{rel_path}} - {{str(e)}}\\\\\\\"); ' + \
          f'"'

os.system(command)
"""
    
    temp_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_temp_upload_script.py")
    with open(temp_script_path, "w") as f:
        f.write(temp_script)
    
    # Execute the temporary script
    print(f"Starting upload of folder: {folder_path}")
    try:
        subprocess.run(["python", temp_script_path], check=True)
        print(f"Upload process completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error during upload: {e}")
        return 1
    finally:
        # Clean up
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 