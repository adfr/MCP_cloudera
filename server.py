#!/usr/bin/env python3
"""
Cloudera ML MCP Server
This server enables LLMs to interact with Cloudera Machine Learning via API.
"""

import os
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List

# Load environment variables from .env file
load_dotenv()

# Import tools
from src.functions.upload_folder import upload_folder
from src.functions.create_job import create_job
from src.functions.list_jobs import list_jobs
from src.functions.delete_job import delete_job
from src.functions.delete_all_jobs import delete_all_jobs
from src.functions.get_project_id import get_project_id
from src.functions.get_runtimes import get_runtimes
from src.functions.create_job_run import create_job_run
from src.functions.create_experiment import create_experiment
from src.functions.create_experiment_run import create_experiment_run
from src.functions.create_model_build import create_model_build
from src.functions.create_model_deployment import create_model_deployment
from src.functions.delete_application import delete_application
from src.functions.delete_experiment import delete_experiment
from src.functions.delete_experiment_run import delete_experiment_run
from src.functions.delete_experiment_run_batch import delete_experiment_run_batch
from src.functions.delete_model import delete_model
from src.functions.delete_project_file import delete_project_file
from src.functions.get_application import get_application
from src.functions.get_experiment import get_experiment
from src.functions.get_experiment_run import get_experiment_run
from src.functions.get_job import get_job
from src.functions.get_job_run import get_job_run
from src.functions.get_model import get_model
from src.functions.get_model_build import get_model_build
from src.functions.get_model_deployment import get_model_deployment
from src.functions.list_applications import list_applications
from src.functions.list_experiments import list_experiments
from src.functions.list_job_runs import list_job_runs
from src.functions.list_models import list_models
from src.functions.list_model_builds import list_model_builds
from src.functions.list_model_deployments import list_model_deployments
from src.functions.list_project_files import list_project_files
from src.functions.log_experiment_run_batch import log_experiment_run_batch
from src.functions.restart_application import restart_application
from src.functions.stop_application import stop_application
from src.functions.stop_job_run import stop_job_run
from src.functions.stop_model_deployment import stop_model_deployment
from src.functions.update_application import update_application
from src.functions.update_experiment import update_experiment
from src.functions.update_experiment_run import update_experiment_run
from src.functions.update_job import update_job
from src.functions.update_project import update_project
from src.functions.update_project_file_metadata import update_project_file_metadata
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
def list_applications_tool(project_id: str = None) -> str:
    """
    List all applications in the Cloudera ML project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of applications
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_applications(config, {"project_id": project_id or config.get("project_id", "")})
    return json.dumps(result, indent=2)

@mcp.tool()
def list_experiments_tool(project_id: str = None) -> str:
    """
    List all experiments in the Cloudera ML project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of experiments
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_experiments(config, {"project_id": project_id or config.get("project_id", "")})
    return json.dumps(result, indent=2)

@mcp.tool()
def list_job_runs_tool(job_id: str = None, project_id: str = None) -> str:
    """
    List all job runs in the Cloudera ML project.
    
    Args:
        job_id: If provided, only list runs for this specific job
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of job runs
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {"project_id": project_id or config.get("project_id", "")}
    if job_id:
        params["job_id"] = job_id
        
    result = list_job_runs(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_models_tool(project_id: str = None) -> str:
    """
    List all models in the Cloudera ML project.
    
    Args:
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of models
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
        
    result = list_models(config, {"project_id": project_id or config.get("project_id", "")})
    return json.dumps(result, indent=2)

@mcp.tool()
def list_model_builds_tool(model_id: str = None, project_id: str = None) -> str:
    """
    List all model builds in the Cloudera ML project.
    
    Args:
        model_id: If provided, only list builds for this specific model
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of model builds
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {"project_id": project_id or config.get("project_id", "")}
    if model_id:
        params["model_id"] = model_id
        
    result = list_model_builds(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def list_model_deployments_tool(model_id: str = None, build_id: str = None, project_id: str = None) -> str:
    """
    List all model deployments in the Cloudera ML project.
    
    Args:
        model_id: If provided, only list deployments for this specific model
        build_id: If provided, only list deployments for this specific build
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of model deployments
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {"project_id": project_id or config.get("project_id", "")}
    if model_id:
        params["model_id"] = model_id
    if build_id:
        params["build_id"] = build_id
        
    result = list_model_deployments(config, params)
    return json.dumps(result, indent=2)

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
        project_name: Name of the project to find. Use "*" to list all projects.
        
    Returns:
        JSON string with project information and ID
    """
    config = get_config()
    result = get_project_id(config, {"project_name": project_name})
    
    # Convert result to string
    return json.dumps(result, indent=2)

@mcp.tool()
def list_projects_tool() -> str:
    """
    List all available projects.
    
    Returns:
        JSON string with all project information
    """
    config = get_config()
    result = get_project_id(config, {"project_name": "*"})
    
    # Convert result to string
    return json.dumps(result, indent=2)

@mcp.tool()
def get_runtimes_tool() -> str:
    """
    Get available runtimes from Cloudera ML.
    
    Returns:
        JSON string with list of available runtimes and their details
    """
    config = get_config()
    result = get_runtimes(config, {})
    
    # Convert result to string
    return json.dumps(result, indent=2)

@mcp.tool()
def create_job_run_tool(project_id: str, job_id: str, 
                       runtime_identifier: str = None, 
                       environment_variables: str = None,
                       override_config: str = None) -> str:
    """
    Create a run for an existing job in Cloudera ML.
    
    Args:
        project_id: ID of the project containing the job
        job_id: ID of the job to run
        runtime_identifier: Runtime identifier (optional)
        environment_variables: JSON string with environment variables (optional)
        override_config: JSON string with configuration overrides (optional)
    
    Returns:
        JSON string with job run data
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "job_id": job_id
    }
    
    # Add optional parameters if provided
    if runtime_identifier:
        params["runtime_identifier"] = runtime_identifier
    
    # Parse JSON strings into dictionaries if provided
    if environment_variables:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    if override_config:
        try:
            params["override_config"] = json.loads(override_config)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for override_config"
            })
    
    result = create_job_run(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def create_model_build_tool(project_id: str, model_id: str, file_path: str, function_name: str,
                           kernel: str = "python3", runtime_identifier: str = None,
                           replica_size: str = None, cpu: int = 1, memory: int = 2,
                           nvidia_gpu: int = 0, use_custom_docker_image: bool = False,
                           custom_docker_image: str = None, environment_variables: str = None) -> str:
    """
    Create a new model build in Cloudera ML.
    
    Args:
        project_id: ID of the project
        model_id: ID of the model to build
        file_path: Path to the model script file or main Python file
        function_name: Name of the function that contains the model code
        kernel: Kernel type (default: python3)
        runtime_identifier: Runtime identifier (optional)
        replica_size: Pod size for the build (optional)
        cpu: CPU cores (default: 1)
        memory: Memory in GB (default: 2)
        nvidia_gpu: Number of GPUs (default: 0)
        use_custom_docker_image: Whether to use a custom Docker image (default: False)
        custom_docker_image: Custom Docker image to use (optional)
        environment_variables: JSON string with environment variables (optional)
    
    Returns:
        JSON string with model build data
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "model_id": model_id,
        "file_path": file_path,
        "function_name": function_name,
        "kernel": kernel,
        "cpu": cpu,
        "memory": memory,
        "nvidia_gpu": nvidia_gpu,
        "use_custom_docker_image": use_custom_docker_image
    }
    
    # Add optional parameters if provided
    if runtime_identifier:
        params["runtime_identifier"] = runtime_identifier
    
    if replica_size:
        params["replica_size"] = replica_size
    
    if custom_docker_image:
        params["custom_docker_image"] = custom_docker_image
    
    # Parse JSON string into dictionary if provided
    if environment_variables:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    result = create_model_build(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def create_model_deployment_tool(project_id: str, model_id: str, build_id: str, name: str,
                                cpu: int = 1, memory: int = 2, replica_count: int = 1,
                                min_replica_count: int = None, max_replica_count: int = None,
                                nvidia_gpu: int = 0, enable_auth: bool = True,
                                target_node_selector: str = None, environment_variables: str = None) -> str:
    """
    Create a new model deployment in Cloudera ML.
    
    Args:
        project_id: ID of the project
        model_id: ID of the model to deploy
        build_id: ID of the model build to deploy
        name: Name of the deployment
        cpu: CPU cores (default: 1)
        memory: Memory in GB (default: 2)
        replica_count: Number of replicas (default: 1)
        min_replica_count: Minimum number of replicas (optional)
        max_replica_count: Maximum number of replicas (optional)
        nvidia_gpu: Number of GPUs (default: 0)
        enable_auth: Whether to enable authentication (default: True)
        target_node_selector: Target node selector for the deployment (optional)
        environment_variables: JSON string with environment variables (optional)
    
    Returns:
        JSON string with model deployment data
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "model_id": model_id,
        "build_id": build_id,
        "name": name,
        "cpu": cpu,
        "memory": memory,
        "replica_count": replica_count,
        "nvidia_gpu": nvidia_gpu,
        "enable_auth": enable_auth
    }
    
    # Add optional parameters if provided
    if min_replica_count is not None:
        params["min_replica_count"] = min_replica_count
    
    if max_replica_count is not None:
        params["max_replica_count"] = max_replica_count
    
    if target_node_selector:
        params["target_node_selector"] = target_node_selector
    
    # Parse JSON string into dictionary if provided
    if environment_variables:
        try:
            params["environment_variables"] = json.loads(environment_variables)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for environment_variables"
            })
    
    result = create_model_deployment(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_application_tool(application_id: str, project_id: str = None) -> str:
    """
    Delete an application in Cloudera ML.
    
    Args:
        application_id: ID of the application to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = delete_application(config, {
        "application_id": application_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_experiment_tool(experiment_id: str, project_id: str = None) -> str:
    """
    Delete an experiment in Cloudera ML.
    
    Args:
        experiment_id: ID of the experiment to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = delete_experiment(config, {
        "experiment_id": experiment_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_experiment_run_tool(experiment_id: str, run_id: str, project_id: str = None) -> str:
    """
    Delete an experiment run in Cloudera ML.
    
    Args:
        experiment_id: ID of the experiment containing the run
        run_id: ID of the experiment run to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = delete_experiment_run(config, {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def create_experiment_run_tool(project_id: str, experiment_id: str, name: str = None, 
                              description: str = None, metrics: str = None,
                              parameters: str = None, tags: str = None) -> str:
    """
    Create a new experiment run in Cloudera ML.
    
    Args:
        project_id: ID of the project
        experiment_id: ID of the experiment for the run
        name: Name of the run (optional)
        description: Description of the run (optional)
        metrics: JSON string with metrics (optional)
        parameters: JSON string with parameters (optional)
        tags: Comma-separated list of tags (optional)
    
    Returns:
        JSON string with experiment run creation result
    """
    config = get_config()
    
    params = {
        "project_id": project_id,
        "experiment_id": experiment_id
    }
    
    # Add optional parameters if provided
    if name:
        params["name"] = name
    
    if description:
        params["description"] = description
    
    # Parse JSON strings into dictionaries if provided
    if metrics:
        try:
            params["metrics"] = json.loads(metrics)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for metrics"
            })
    
    if parameters:
        try:
            params["parameters"] = json.loads(parameters)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "Invalid JSON for parameters"
            })
    
    # Parse comma-separated tags into a list if provided
    if tags:
        params["tags"] = [tag.strip() for tag in tags.split(",")]
    
    result = create_experiment_run(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_experiment_run_batch_tool(experiment_id: str, run_ids: str, project_id: str = None) -> str:
    """
    Delete multiple experiment runs in a single request.
    
    Args:
        experiment_id: ID of the experiment containing the runs
        run_ids: Comma-separated list of run IDs to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    # Convert comma-separated string to list
    run_ids_list = [run_id.strip() for run_id in run_ids.split(",")]
    
    result = delete_experiment_run_batch(config, {
        "experiment_id": experiment_id,
        "run_ids": run_ids_list,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_model_tool(model_id: str, project_id: str = None) -> str:
    """
    Delete a model in Cloudera ML.
    
    Args:
        model_id: ID of the model to delete
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    result = delete_model(config, {
        "model_id": model_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def delete_project_file_tool(file_path: str, project_id: str = None) -> str:
    """
    Delete a file or directory from a Cloudera ML project.
    
    Args:
        file_path: Path of the file or directory to delete (relative to project root)
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with operation result
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    result = delete_project_file(config, {
        "file_path": file_path,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_application_tool(application_id: str, project_id: str = None) -> str:
    """
    Get details of a specific application from a Cloudera ML project.
    
    Args:
        application_id: ID of the application to get details for
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string with application details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
        
    result = get_application(config, {
        "application_id": application_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_experiment_tool(experiment_id: str, project_id: str = None) -> str:
    """
    Get details of a specific experiment from a Cloudera ML project.
    
    Args:
        experiment_id: ID of the experiment to retrieve
        project_id: ID of the project containing the experiment (optional)
    
    Returns:
        JSON string with experiment details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_experiment(config, {
        "experiment_id": experiment_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_experiment_run_tool(experiment_id: str, run_id: str, project_id: str = None) -> str:
    """
    Get details of a specific experiment run from a Cloudera ML project.
    
    Args:
        experiment_id: ID of the experiment containing the run
        run_id: ID of the experiment run to retrieve
        project_id: ID of the project containing the experiment (optional)
    
    Returns:
        JSON string with experiment run details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_experiment_run(config, {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_job_tool(job_id: str, project_id: str = None) -> str:
    """
    Get details of a specific job from a Cloudera ML project.
    
    Args:
        job_id: ID of the job to retrieve
        project_id: ID of the project containing the job (optional)
    
    Returns:
        JSON string with job details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_job(config, {
        "job_id": job_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_job_run_tool(job_id: str, run_id: str, project_id: str = None) -> str:
    """
    Get details of a specific job run from a Cloudera ML project.
    
    Args:
        job_id: ID of the job containing the run
        run_id: ID of the job run to retrieve
        project_id: ID of the project containing the job (optional)
    
    Returns:
        JSON string with job run details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_job_run(config, {
        "job_id": job_id,
        "run_id": run_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_model_tool(model_id: str, project_id: str = None) -> str:
    """
    Get details of a specific model from a Cloudera ML project.
    
    Args:
        model_id: ID of the model to retrieve
        project_id: ID of the project containing the model (optional)
    
    Returns:
        JSON string with model details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_model(config, {
        "model_id": model_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_model_build_tool(model_id: str, build_id: str, project_id: str = None) -> str:
    """
    Get details of a specific model build from a Cloudera ML project.
    
    Args:
        model_id: ID of the model that contains the build
        build_id: ID of the model build to retrieve
        project_id: ID of the project containing the model (optional)
    
    Returns:
        JSON string with model build details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_model_build(config, {
        "model_id": model_id,
        "build_id": build_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def get_model_deployment_tool(model_id: str, deployment_id: str, project_id: str = None) -> str:
    """
    Get details of a specific model deployment from a Cloudera ML project.
    
    Args:
        model_id: ID of the model that contains the deployment
        deployment_id: ID of the model deployment to retrieve
        project_id: ID of the project containing the model (optional)
    
    Returns:
        JSON string with model deployment details
    """
    config = get_config()
    
    if project_id:
        config["project_id"] = project_id
    
    result = get_model_deployment(config, {
        "model_id": model_id,
        "deployment_id": deployment_id,
        "project_id": project_id or config.get("project_id", "")
    })
    
    return json.dumps(result, indent=2)

@mcp.tool()
def list_project_files_tool(path: str = "", project_id: str = None) -> str:
    """
    List files in a Cloudera ML project.
    
    Args:
        path: Path to list files from (relative to project root)
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing list of project files
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {"project_id": project_id or config.get("project_id", "")}
    if path:
        params["path"] = path
        
    result = list_project_files(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def log_experiment_run_batch_tool(experiment_id: str, run_updates: str, project_id: str = None) -> str:
    """
    Log metrics and parameters for multiple experiment runs in a batch.
    
    Args:
        experiment_id: ID of the experiment containing the runs
        run_updates: JSON string containing an array of run update objects, each with:
            - id: ID of the run to update
            - metrics (optional): Dictionary of metrics to log
            - parameters (optional): Dictionary of parameters to log
            - tags (optional): Array of tags to add to the run
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing operation result
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    # Parse the run_updates JSON string
    try:
        run_updates_list = json.loads(run_updates)
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "message": "Invalid JSON for run_updates"
        }, indent=2)
    
    params = {
        "experiment_id": experiment_id,
        "run_updates": run_updates_list,
        "project_id": project_id or config.get("project_id", "")
    }
        
    result = log_experiment_run_batch(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def restart_application_tool(application_id: str, project_id: str = None) -> str:
    """
    Restart a running application in a Cloudera ML project.
    
    Args:
        application_id: ID of the application to restart
        project_id: ID of the project (optional if not provided, uses default from configuration)
    
    Returns:
        JSON string containing operation result
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "application_id": application_id,
        "project_id": project_id or config.get("project_id", "")
    }
        
    result = restart_application(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def update_job_tool(job_id: str, name: str = None, script: str = None, 
                   kernel: str = None, cpu: int = None, memory: int = None, 
                   nvidia_gpu: int = None, runtime_identifier: str = None,
                   environment_variables: str = None, project_id: str = None) -> str:
    """
    Update an existing job in Cloudera ML.
    
    Args:
        job_id: ID of the job to update
        name: New name for the job (optional)
        script: New script path for the job (optional)
        kernel: New kernel type (optional)
        cpu: New CPU cores allocation (optional)
        memory: New memory allocation in GB (optional)
        nvidia_gpu: New GPU allocation (optional)
        runtime_identifier: New runtime identifier (optional)
        environment_variables: JSON string of environment variables (optional)
        project_id: Project ID (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with job update results
    """
    config = get_config()
    if project_id:
        config["project_id"] = project_id
    
    params = {
        "job_id": job_id
    }
    
    # Add optional parameters if provided
    if name is not None:
        params["name"] = name
        
    if script is not None:
        params["script"] = script
        
    if kernel is not None:
        params["kernel"] = kernel
        
    if cpu is not None:
        params["cpu"] = cpu
        
    if memory is not None:
        params["memory"] = memory
        
    if nvidia_gpu is not None:
        params["nvidia_gpu"] = nvidia_gpu
        
    if runtime_identifier is not None:
        params["runtime_identifier"] = runtime_identifier
        
    if environment_variables is not None:
        params["environment_variables"] = json.loads(environment_variables)
    
    result = update_job(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def update_project_tool(name: str = None, summary: str = None, template: str = None,
                       public: bool = None, disable_git_repo: bool = None, 
                       project_id: str = None) -> str:
    """
    Update a project in Cloudera ML.
    
    Args:
        name: New name for the project (optional)
        summary: New summary for the project (optional)
        template: New template for the project (optional)
        public: Whether the project should be public (optional)
        disable_git_repo: Whether to disable the Git repository (optional)
        project_id: ID of the project to update (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with project update results
    """
    config = get_config()
    params = {}
    
    if project_id:
        params["project_id"] = project_id
    elif config.get("project_id"):
        params["project_id"] = config["project_id"]
    
    # Add optional parameters if provided
    if name is not None:
        params["name"] = name
        
    if summary is not None:
        params["summary"] = summary
        
    if template is not None:
        params["template"] = template
        
    if public is not None:
        params["public"] = public
        
    if disable_git_repo is not None:
        params["disable_git_repo"] = disable_git_repo
    
    result = update_project(config, params)
    return json.dumps(result, indent=2)

@mcp.tool()
def update_project_file_metadata_tool(file_path: str, description: str = None,
                                     hidden: bool = None, project_id: str = None) -> str:
    """
    Update metadata of a file in a Cloudera ML project.
    
    Args:
        file_path: Path of the file relative to the project root
        description: New description for the file (optional)
        hidden: Whether the file should be hidden (optional)
        project_id: ID of the project (optional - if not provided, uses default from configuration)
    
    Returns:
        JSON string with file metadata update results
    """
    config = get_config()
    params = {
        "file_path": file_path
    }
    
    if project_id:
        params["project_id"] = project_id
    elif config.get("project_id"):
        params["project_id"] = config["project_id"]
    
    # Add optional parameters if provided
    if description is not None:
        params["description"] = description
        
    if hidden is not None:
        params["hidden"] = hidden
    
    result = update_project_file_metadata(config, params)
    return json.dumps(result, indent=2)

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