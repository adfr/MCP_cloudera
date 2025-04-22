#!/usr/bin/env python3
"""
Simple script to test the Cloudera MCP by running some commands directly
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv
from src import ClouderaMCP

# Load environment variables from .env file
load_dotenv()

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
        'upload_file',
        'upload_folder', 
        'create_job', 
        'delete_job', 
        'delete_all_jobs',
        'get_project_id',
        'list_projects',
        'get_runtimes',
        'create_job_run',
        'list_job_runs',
        'create_model_build',
        'create_model_deployment',
        'delete_application',
        'get_application',
        'list_applications',
        'create_application'
    ], help='MCP command to run')
    
    # Command-specific arguments
    parser.add_argument('--file-path', help='Path to the file to upload')
    parser.add_argument('--target-name', help='Target name for the uploaded file')
    parser.add_argument('--target-dir', help='Target directory for the uploaded file')
    parser.add_argument('--folder-path', help='Local folder path to upload')
    parser.add_argument('--job-name', help='Name for the job to create')
    parser.add_argument('--script-path', help='Script path for the job to create')
    parser.add_argument('--job-id', help='ID of the job to delete or run')
    parser.add_argument('--project-name', help='Name of the project to find')
    parser.add_argument('--runtime', help='Runtime identifier for jobs or applications')
    parser.add_argument('--env-vars', help='Environment variables as JSON string')
    parser.add_argument('--override-config', help='Job configuration overrides as JSON string')
    parser.add_argument('--description', help='Description for the job or application')
    # Model build specific arguments
    parser.add_argument('--model-id', help='ID of the model to build or deploy')
    parser.add_argument('--function-name', help='Name of the function that contains the model code')
    parser.add_argument('--kernel', help='Kernel type (default: python3)')
    parser.add_argument('--replica-size', help='Pod size for the build')
    parser.add_argument('--cpu', type=int, help='CPU cores')
    parser.add_argument('--memory', type=int, help='Memory in GB')
    parser.add_argument('--nvidia-gpu', type=int, help='Number of GPUs')
    parser.add_argument('--use-custom-docker-image', action='store_true', help='Use a custom Docker image')
    parser.add_argument('--custom-docker-image', help='Custom Docker image to use')
    # Model deployment specific arguments
    parser.add_argument('--build-id', help='ID of the model build to deploy')
    parser.add_argument('--name', help='Name for the deployment')
    parser.add_argument('--replica-count', type=int, help='Number of replicas')
    parser.add_argument('--min-replica-count', type=int, help='Minimum number of replicas')
    parser.add_argument('--max-replica-count', type=int, help='Maximum number of replicas')
    parser.add_argument('--enable-auth', action='store_true', help='Enable authentication for the deployment')
    parser.add_argument('--disable-auth', action='store_true', help='Disable authentication for the deployment')
    parser.add_argument('--target-node-selector', help='Target node selector for the deployment')
    # Application specific arguments
    parser.add_argument('--application-id', help='ID of the application to delete or get details for')
    
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
        
        elif args.command == 'upload_file':
            if not args.file_path:
                print("Error: --file-path is required for upload_file command")
                return 1
            result = mcp.upload_file(file_path=args.file_path, target_name=args.target_name, target_dir=args.target_dir)
        
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
            
        elif args.command == 'list_projects':
            result = mcp.list_projects()
            
        elif args.command == 'get_runtimes':
            result = mcp.get_runtimes()
            
        elif args.command == 'list_job_runs':
            # Get job_id if provided
            job_id = args.job_id
            result = mcp.list_job_runs(job_id=job_id, project_id=args.project_id)
        
        elif args.command == 'create_job_run':
            if not args.project_id:
                print("Error: --project-id is required for create_job_run command")
                return 1
                
            if not args.job_id:
                print("Error: --job-id is required for create_job_run command")
                return 1
            
            # Parse optional JSON parameters if provided
            env_vars = None
            if args.env_vars:
                try:
                    env_vars = json.loads(args.env_vars)
                except json.JSONDecodeError:
                    print("Error: --env-vars must be valid JSON")
                    return 1
            
            override_config = None
            if args.override_config:
                try:
                    override_config = json.loads(args.override_config)
                except json.JSONDecodeError:
                    print("Error: --override-config must be valid JSON")
                    return 1
            
            result = mcp.create_job_run(
                project_id=args.project_id,
                job_id=args.job_id,
                runtime_identifier=args.runtime,
                environment_variables=env_vars,
                override_config=override_config
            )
            
        elif args.command == 'create_model_build':
            if not args.project_id:
                print("Error: --project-id is required for create_model_build command")
                return 1
                
            if not args.model_id:
                print("Error: --model-id is required for create_model_build command")
                return 1
                
            if not args.file_path:
                print("Error: --file-path is required for create_model_build command")
                return 1
                
            if not args.function_name:
                print("Error: --function-name is required for create_model_build command")
                return 1
            
            # Parse environment variables if provided
            env_vars = None
            if args.env_vars:
                try:
                    env_vars = json.loads(args.env_vars)
                except json.JSONDecodeError:
                    print("Error: --env-vars must be valid JSON")
                    return 1
            
            result = mcp.create_model_build(
                project_id=args.project_id,
                model_id=args.model_id,
                file_path=args.file_path,
                function_name=args.function_name,
                kernel=args.kernel,
                runtime_identifier=args.runtime,
                replica_size=args.replica_size,
                cpu=args.cpu,
                memory=args.memory,
                nvidia_gpu=args.nvidia_gpu,
                use_custom_docker_image=args.use_custom_docker_image,
                custom_docker_image=args.custom_docker_image,
                environment_variables=env_vars
            )
        
        elif args.command == 'create_model_deployment':
            if not args.project_id:
                print("Error: --project-id is required for create_model_deployment command")
                return 1
                
            if not args.model_id:
                print("Error: --model-id is required for create_model_deployment command")
                return 1
                
            if not args.build_id:
                print("Error: --build-id is required for create_model_deployment command")
                return 1
                
            if not args.name:
                print("Error: --name is required for create_model_deployment command")
                return 1
            
            # Parse environment variables if provided
            env_vars = None
            if args.env_vars:
                try:
                    env_vars = json.loads(args.env_vars)
                except json.JSONDecodeError:
                    print("Error: --env-vars must be valid JSON")
                    return 1
            
            # Handle enable/disable auth flags
            enable_auth = True
            if args.disable_auth:
                enable_auth = False
            
            result = mcp.create_model_deployment(
                project_id=args.project_id,
                model_id=args.model_id,
                build_id=args.build_id,
                name=args.name,
                cpu=args.cpu,
                memory=args.memory,
                replica_count=args.replica_count,
                min_replica_count=args.min_replica_count,
                max_replica_count=args.max_replica_count,
                nvidia_gpu=args.nvidia_gpu,
                environment_variables=env_vars,
                enable_auth=enable_auth,
                target_node_selector=args.target_node_selector
            )
        
        elif args.command == 'delete_application':
            if not args.application_id:
                print("Error: --application-id is required for delete_application command")
                return 1
            
            result = mcp.delete_application(
                application_id=args.application_id,
                project_id=args.project_id
            )
            
        elif args.command == 'get_application':
            if not args.application_id:
                print("Error: --application-id is required for get_application command")
                return 1
            
            result = mcp.get_application(
                application_id=args.application_id,
                project_id=args.project_id
            )
            
        elif args.command == 'list_applications':
            result = mcp.list_applications(project_id=args.project_id)
            
        elif args.command == 'create_application':
            if not args.name:
                print("Error: --name is required for create_application command")
                return 1
                
            if not args.script_path:
                print("Error: --script-path is required for create_application command")
                return 1
            
            # Parse environment variables if provided
            env_vars = None
            if args.env_vars:
                try:
                    env_vars = json.loads(args.env_vars)
                except json.JSONDecodeError:
                    print("Error: --env-vars must be valid JSON")
                    return 1
            
            result = mcp.create_application(
                name=args.name,
                script=args.script_path,
                project_id=args.project_id,
                description=args.description if hasattr(args, 'description') else None,
                cpu=args.cpu,
                memory=args.memory,
                nvidia_gpu=args.nvidia_gpu,
                runtime_identifier=args.runtime,
                environment_variables=env_vars
            )
        
        # Display the result
        print("\nCommand result:")
        print_json(result)
    
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 