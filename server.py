#!/usr/bin/env python3
"""
Cloudera ML MCP Server
This server enables LLMs to interact with Cloudera Machine Learning via API.
"""

import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import tools
from src.functions.upload_folder import upload_folder
from src.functions.create_job import create_job
from src.functions.list_jobs import list_jobs
from src.functions.delete_job import delete_job
from src.functions.delete_all_jobs import delete_all_jobs
from src.functions.get_project_id import get_project_id
from src.utils import get_session, handle_error, format_url

# Create MCP server
mcp = FastMCP(name="Cloudera ML MCP Server")

# Get configuration from environment variables
def get_config():
    return {
        "host": os.environ.get("CLOUDERA_ML_HOST", ""),
        "api_key": os.environ.get("CLOUDERA_ML_API_KEY", "")
    }

# Register functions as MCP tools
@mcp.tool()
def upload_folder_tool(folder_path: str, ignore_folders: str = None) -> str:
    """
    Upload a folder to Cloudera ML.
    
    Args:
        folder_path: Local path to the folder to upload
        ignore_folders: Comma-separated list of folders to ignore (optional)
    
    Returns:
        JSON string with upload results
    """
    config = get_config()
    # Convert comma-separated string to list if provided
    ignore_list = ignore_folders.split(",") if ignore_folders else None
    
    result = upload_folder(config, {
        "folder_path": folder_path,
        "ignore_folders": ignore_list
    })
    return result

@mcp.tool()
def create_job_tool(name: str, script: str, kernel: str = "python3", 
                   cpu: int = 1, memory: int = 1, nvidia_gpu: int = 0,
                   runtime_identifier: str = None, project_id: str = None) -> str:
    """
    Create a new Cloudera ML job.
    
    Args:
        name: Job name
        script: Script path relative to project root
        kernel: Kernel type (default: python3)
        cpu: CPU cores (default: 1)
        memory: Memory in GB (default: 1)
        nvidia_gpu: Number of GPUs (default: 0)
        runtime_identifier: Runtime environment identifier
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with job creation results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    result = create_job(config, {
        "name": name,
        "script": script,
        "kernel": kernel,
        "cpu": cpu,
        "memory": memory,
        "nvidia_gpu": nvidia_gpu,
        "runtime_identifier": runtime_identifier
    })
    return result

@mcp.tool()
def list_jobs_tool(project_id: str = None) -> str:
    """
    List all jobs in the Cloudera ML project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of jobs
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_jobs(config, {})
    return result

@mcp.tool()
def delete_job_tool(job_id: str, project_id: str = None) -> str:
    """
    Delete a job by ID.
    
    Args:
        job_id: ID of the job to delete
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with delete operation results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = delete_job(config, {"job_id": job_id})
    return result

@mcp.tool()
def delete_all_jobs_tool(project_id: str = None) -> str:
    """
    Delete all jobs in the project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with delete operation results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = delete_all_jobs(config, {})
    return result

@mcp.tool()
def get_project_id_tool(project_name: str) -> str:
    """
    Get project ID from a project name.
    
    Args:
        project_name: Name of the project to find
        
    Returns:
        JSON string with project information and ID
    """
    config = get_config()
    result = get_project_id(config, {"project_name": project_name})
    return result

if __name__ == "__main__":
    # Check if configuration is complete
    config = get_config()
    missing = [k for k, v in config.items() if not v]
    
    if missing:
        print(f"Error: Missing configuration: {', '.join(missing)}")
        print("Please set the following environment variables:")
        print("  CLOUDERA_ML_HOST - Your Cloudera ML host URL")
        print("  CLOUDERA_ML_API_KEY - Your Cloudera ML API key")
        exit(1)
    
    # Initialize and run the server
    print(f"Starting Cloudera ML MCP Server with host: {config['host']}")
    mcp.run(transport='stdio') 