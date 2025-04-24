#!/usr/bin/env python3
"""
Wrapper script to use the upload_files.py functionality with the MCP
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Wrapper for uploading files to Cloudera ML')
    parser.add_argument('--folder-path', required=True, help='Local folder path to upload')
    parser.add_argument('--project-id', required=True, help='Cloudera ML project ID')
    parser.add_argument('--host', help='Cloudera ML host URL')
    parser.add_argument('--api-key', help='Cloudera ML API key')
    parser.add_argument('--ignore-folders', help='Comma-separated list of folders to ignore')
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()
    
    # Get configuration from args or environment variables
    host = args.host or os.environ.get("CLOUDERA_ML_HOST", "")
    api_key = args.api_key or os.environ.get("CLOUDERA_ML_API_KEY", "")
    
    if not host or not api_key:
        print("Error: Missing host or API key. Please provide them as arguments or environment variables.")
        return 1
    
    # Set up environment to use the cml_api virtual environment
    cml_api_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cml_api")
    python_path = os.path.join(cml_api_dir, "bin", "python")
    
    # Path to the upload_files.py script
    upload_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "upload_files.py")
    
    # Create a temporary wrapper script
    temp_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_temp_upload.py")
    
    ignore_folders = args.ignore_folders.split(",") if args.ignore_folders else ["node_modules", ".git", ".vscode", "dist", "out"]
    ignore_folders_str = "[" + ", ".join([f'"{folder}"' for folder in ignore_folders]) + "]"
    
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
    
    # Script content to write to the temporary file
    script_content = f'''
import os
import sys

# Add the site-packages directory to the path
sys.path.append('{os.path.join(cml_api_dir, "lib", "python3.13", "site-packages")}')

import cmlapi
from pathlib import Path

def setup_client(host, api_key):
    """Setup the CML API client"""
    config = cmlapi.Configuration()
    config.host = host
    api = cmlapi.ApiClient(config)
    api.set_default_header("authorization", f"Bearer {{api_key}}")
    return cmlapi.CMLServiceApi(api)

def upload_file_with_metadata(client, project_id, file_path, relative_path):
    """
    Upload a file and update its metadata to preserve the original name and path
    """
    try:
        # First upload the file (it will be named 'file' by default)
        client.upload_file(
                project_id=project_id,
                file=file_path)
        
        # Then update its metadata to preserve the original name and path
        metadata = {{
            "name": os.path.basename(file_path),
            "path": str(relative_path),
            "type": "file"
        }}
        
        client.update_project_file_metadata(
            project_id=project_id,
            path="file",  # The default name used by create_project_file
            body=metadata
        )
        
        print(f"Successfully uploaded and renamed: {{relative_path}}")
        return True
        
    except Exception as e:
        print(f"Error uploading {{file_path}}: {{str(e)}}")
        return False

def upload_directory(host, api_key, project_id, directory_path, ignore_folders):
    """
    Recursively upload all files in a directory while preserving names and structure
    """
    client = setup_client(host, api_key)
    base_path = Path(directory_path)
    
    success_count = 0
    failed_count = 0
    
    for root, dirs, files in os.walk(directory_path):
        # Remove ignored folders from dirs to prevent walking into them
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = Path(full_path).relative_to(base_path)
            result = upload_file_with_metadata(client, project_id, full_path, relative_path)
            if result:
                success_count += 1
            else:
                failed_count += 1
    
    return {{
        "success": success_count > 0,
        "message": f"Upload completed. Successfully uploaded {{success_count}} files.",
        "success_count": success_count,
        "failed_count": failed_count
    }}

# Main execution
result = upload_directory("{host}", "{api_key}", "{args.project_id}", "{args.folder_path}", {ignore_folders_str})
print(f"\\nUpload summary:")
print(f"  Success: {{result['success_count']}} files")
print(f"  Failed: {{result['failed_count']}} files")
print(f"  Status: {'Success' if result['success'] else 'Failed'}")
'''
    
    with open(temp_script, 'w') as f:
        f.write(script_content)
    
    # Execute the script with the system Python
    print(f"Executing upload script for folder: {args.folder_path}")
    return_code = os.system(f"python {temp_script}")
    
    # Clean up
    os.remove(temp_script)
    
    return 0 if return_code == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 