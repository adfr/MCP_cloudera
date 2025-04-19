#!/usr/bin/env python3
"""
Simple script to test the Cloudera MCP by running some commands directly
"""

import os
import sys
import json
import argparse
from src import ClouderaMCP

def print_json(data):
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run and test Cloudera ML MCP')
    
    # MCP configuration arguments
    parser.add_argument('--host', help='Cloudera ML host URL')
    parser.add_argument('--api-key', help='Cloudera ML API key')
    parser.add_argument('--project-id', help='Cloudera ML project ID')
    
    # Command to run
    parser.add_argument('command', choices=[
        'list_jobs', 
        'upload_folder', 
        'create_job', 
        'delete_job', 
        'delete_all_jobs',
        'get_project_id'
    ], help='MCP command to run')
    
    # Command-specific arguments
    parser.add_argument('--folder-path', help='Local folder path to upload')
    parser.add_argument('--job-name', help='Name for the job to create')
    parser.add_argument('--script-path', help='Script path for the job to create')
    parser.add_argument('--job-id', help='ID of the job to delete')
    parser.add_argument('--project-name', help='Name of the project to find')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Load configuration from args or environment variables
    config = {
        "host": args.host or os.environ.get("CLOUDERA_ML_HOST", ""),
        "api_key": args.api_key or os.environ.get("CLOUDERA_ML_API_KEY", ""),
    }
    
    # Add project_id only if provided
    if args.project_id or os.environ.get("CLOUDERA_ML_PROJECT_ID"):
        config["project_id"] = args.project_id or os.environ.get("CLOUDERA_ML_PROJECT_ID", "")
    
    # Check if configuration is provided
    required_config = ["host", "api_key"]
    missing_config = [k for k in required_config if not config.get(k)]
    if missing_config:
        print(f"Missing configuration: {', '.join(missing_config)}")
        print("Please set the following environment variables:")
        print("  CLOUDERA_ML_HOST - Your Cloudera ML host URL")
        print("  CLOUDERA_ML_API_KEY - Your Cloudera ML API key")
        print("\nOr provide them as arguments:")
        print("  run_mcp.py --host URL --api-key KEY command")
        return 1
    
    # Initialize the MCP
    print("Initializing Cloudera MCP...")
    mcp = ClouderaMCP(config)
    print("MCP initialized successfully!")
    
    # Run the requested command
    print(f"\nRunning command: {args.command}")
    
    try:
        if args.command == 'list_jobs':
            result = mcp.list_jobs()
        
        elif args.command == 'upload_folder':
            if not args.folder_path:
                print("Error: --folder-path is required for upload_folder command")
                return 1
            result = mcp.upload_folder(folder_path=args.folder_path)
        
        elif args.command == 'create_job':
            if not args.job_name or not args.script_path:
                print("Error: --job-name and --script-path are required for create_job command")
                return 1
            result = mcp.create_job(name=args.job_name, script=args.script_path)
        
        elif args.command == 'delete_job':
            if not args.job_id:
                print("Error: --job-id is required for delete_job command")
                return 1
            result = mcp.delete_job(job_id=args.job_id)
        
        elif args.command == 'delete_all_jobs':
            result = mcp.delete_all_jobs()
            
        elif args.command == 'get_project_id':
            if not args.project_name:
                print("Error: --project-name is required for get_project_id command")
                return 1
            result = mcp.get_project_id(project_name=args.project_name)
        
        # Display the result
        print("\nCommand result:")
        print_json(result)
    
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 