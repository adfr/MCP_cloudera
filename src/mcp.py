"""
Main implementation of the Cloudera ML Model Control Protocol
"""

from typing import Dict, Any, Optional, List, Union, Callable
import json
import os

from . import functions
from . import utils


class ClouderaMCP:
    """
    Claude integration with Cloudera Machine Learning
    
    This MCP allows Claude to interact with Cloudera ML APIs to:
    - Upload files and folders
    - Create and manage jobs
    - Query project resources
    """
    
    # MCP metadata
    name = "cloudera-ml"
    version = "1.0.0"
    description = "Claude integration with Cloudera Machine Learning"
    
    # Configuration schema
    CONFIG_SCHEMA = {
        "host": {
            "type": "string",
            "description": "Cloudera ML host URL",
            "required": True
        },
        "api_key": {
            "type": "string", 
            "description": "Cloudera ML API key",
            "required": True
        },
        "project_id": {
            "type": "string",
            "description": "Cloudera ML project ID", 
            "required": False
        }
    }
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the Cloudera ML MCP
        
        Args:
            config: Optional configuration dictionary with host, api_key, and project_id
                   If not provided, will try to load from environment variables
        """
        if config is None:
            # Try to load from environment variables
            config = {
                "host": os.environ.get("CLOUDERA_ML_HOST", ""),
                "api_key": os.environ.get("CLOUDERA_ML_API_KEY", ""),
                "project_id": os.environ.get("CLOUDERA_ML_PROJECT_ID", "")
            }
        
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """Validate the configuration"""
        for key, schema in self.CONFIG_SCHEMA.items():
            if schema.get("required", False) and not self.config.get(key):
                raise ValueError(f"Missing required configuration: {key}")
    
    def upload_file(self, file_path: str, target_name: Optional[str] = None, target_dir: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to the Cloudera ML project
        
        Args:
            file_path: Path to the file to upload
            target_name: Optional name to save the file as
            target_dir: Optional directory to save the file in
            project_id: Optional project ID (uses the one in config if not provided)
            
        Returns:
            Upload file result
        """
        # Prepare configuration with project_id if provided
        config = dict(self.config)
        if project_id:
            config["project_id"] = project_id
            
        return functions.upload_file(config, {
            "file_path": file_path,
            "target_name": target_name,
            "target_dir": target_dir
        })
    
    def upload_folder(self, folder_path: str, ignore_folders: Optional[List[str]] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a folder to Cloudera ML
        
        Args:
            folder_path: Local path to the folder to upload
            ignore_folders: Folders to ignore during upload
            project_id: Optional project ID (uses the one in config if not provided)
            
        Returns:
            Upload results
        """
        # Prepare parameters
        params = {
            "folder_path": folder_path,
        }
        
        if ignore_folders:
            params["ignore_folders"] = ignore_folders
            
        # Add project_id if provided
        if project_id:
            params["project_id"] = project_id
            
        return functions.upload_folder(self.config, params)
    
    def create_job(self, name: str, script: str, 
                  kernel: str = "python3",
                  cpu: int = 1, 
                  memory: int = 1,
                  nvidia_gpu: int = 0,
                  runtime_identifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Cloudera ML job
        
        Args:
            name: Job name
            script: Script path relative to project root
            kernel: Kernel type (default: python3)
            cpu: CPU cores (default: 1)
            memory: Memory in GB (default: 1)
            nvidia_gpu: Number of GPUs (default: 0)
            runtime_identifier: Runtime environment identifier
            
        Returns:
            Job creation results
        """
        return functions.create_job(self.config, {
            "name": name,
            "script": script,
            "kernel": kernel,
            "cpu": cpu,
            "memory": memory,
            "nvidia_gpu": nvidia_gpu,
            "runtime_identifier": runtime_identifier
        })
    
    def list_jobs(self) -> Dict[str, Any]:
        """
        List jobs in the Cloudera ML project
        
        Returns:
            Dictionary containing list of jobs
        """
        return functions.list_jobs(self.config, {})
    
    def list_applications(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List applications in a Cloudera ML project
        
        Args:
            project_id: Optional project ID (uses the one in config if not provided)
            
        Returns:
            Dictionary containing list of applications
        """
        # Prepare parameters
        params = {}
        
        # Add project_id if provided
        if project_id:
            params["project_id"] = project_id
        
        # Call the function
        return functions.list_applications(self.config, params)
    
    def create_application(
        self, 
        name: str, 
        script: str, 
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        cpu: Optional[int] = None,
        memory: Optional[int] = None,
        nvidia_gpu: Optional[int] = None,
        runtime_identifier: Optional[str] = None,
        environment_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new application in a Cloudera ML project
        
        Args:
            name: Name for the application
            script: Script to run in the application
            project_id: Optional project ID (uses the one in config if not provided)
            description: Optional description for the application
            cpu: CPU cores (default: 1)
            memory: Memory in GB (default: 1)
            nvidia_gpu: Number of GPUs (default: 0)
            runtime_identifier: Runtime identifier for the application
            environment_variables: Environment variables as a dictionary
            
        Returns:
            Dictionary containing the application creation result
        """
        # Prepare parameters
        params = {
            "name": name,
            "script": script
        }
        
        # Add project_id from parameters or config
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        
        # Add optional parameters if provided
        if description:
            params["description"] = description
            
        if cpu is not None:
            params["cpu"] = cpu
            
        if memory is not None:
            params["memory"] = memory
            
        if nvidia_gpu is not None:
            params["nvidia_gpu"] = nvidia_gpu
            
        if runtime_identifier:
            params["runtime_identifier"] = runtime_identifier
            
        if environment_variables:
            params["environment_variables"] = environment_variables
        
        # Call the function
        return functions.create_application(self.config, params)
    
    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """
        Delete a job by ID
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            Delete operation results
        """
        return functions.delete_job(self.config, {"job_id": job_id})
    
    def delete_all_jobs(self) -> Dict[str, Any]:
        """
        Delete all jobs in the project
        
        Returns:
            Delete operation results
        """
        return functions.delete_all_jobs(self.config, {})

    def get_project_id(self, project_name: str) -> Dict[str, Any]:
        """
        Get project ID from a project name
        
        Args:
            project_name: Name of the project to find
            
        Returns:
            Project information with ID
        """
        return functions.get_project_id(self.config, {"project_name": project_name})
    
    def list_projects(self) -> Dict[str, Any]:
        """
        List all available projects
        
        Returns:
            Dictionary containing all projects information
        """
        return functions.get_project_id(self.config, {"project_name": "*"})
    
    def get_runtimes(self) -> Dict[str, Any]:
        """
        Get available runtimes from Cloudera ML
        
        Returns:
            Dictionary containing list of available runtimes
        """
        return functions.get_runtimes(self.config, {})
    
    def batch_list_projects(self, project_ids: List[str]) -> Dict[str, Any]:
        """
        Return a list of projects given a list of project IDs
        
        Args:
            project_ids: List of project IDs to return details for
            
        Returns:
            Dictionary containing list of specified projects
        """
        return functions.batch_list_projects(self.config, {"project_ids": project_ids})
    
    def create_experiment(self, name: str, description: Optional[str] = None, 
                         project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new experiment in Cloudera ML
        
        Args:
            name: Experiment name
            description: Experiment description (optional)
            project_id: Project ID (optional if set in configuration)
            
        Returns:
            Dictionary containing experiment creation results
        """
        params = {
            "name": name
        }
        
        if description:
            params["description"] = description
            
        if project_id:
            params["project_id"] = project_id
            
        return functions.create_experiment(self.config, params)
    
    def create_job_run(self, project_id: str, job_id: str, 
                      runtime_identifier: Optional[str] = None,
                      environment_variables: Optional[Dict[str, str]] = None,
                      override_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a run for an existing job in Cloudera ML
        
        Args:
            project_id: ID of the project containing the job
            job_id: ID of the job to run
            runtime_identifier: Runtime identifier (optional)
            environment_variables: Dictionary of environment variables (optional)
            override_config: Dictionary with configuration overrides (optional)
            
        Returns:
            Dict with success flag, message, and job run data
        """
        params = {
            "project_id": project_id,
            "job_id": job_id
        }
        
        if runtime_identifier:
            params["runtime_identifier"] = runtime_identifier
            
        if environment_variables:
            params["environment_variables"] = environment_variables
            
        if override_config:
            params["override_config"] = override_config
            
        return functions.create_job_run(self.config, params)
    
    def create_model_build(self, project_id: str, model_id: str, file_path: str, function_name: str,
                          kernel: str = "python3",
                          runtime_identifier: Optional[str] = None,
                          replica_size: Optional[str] = None,
                          cpu: int = 1,
                          memory: int = 2,
                          nvidia_gpu: int = 0,
                          use_custom_docker_image: bool = False,
                          custom_docker_image: Optional[str] = None,
                          environment_variables: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new model build in Cloudera ML
        
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
            environment_variables: Dictionary of environment variables (optional)
            
        Returns:
            Dict with success flag, message, and model build data
        """
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
        
        if runtime_identifier:
            params["runtime_identifier"] = runtime_identifier
            
        if replica_size:
            params["replica_size"] = replica_size
            
        if custom_docker_image:
            params["custom_docker_image"] = custom_docker_image
            
        if environment_variables:
            params["environment_variables"] = environment_variables
            
        return functions.create_model_build(self.config, params)
    
    def create_model_deployment(self, project_id: str, model_id: str, build_id: str, name: str,
                               cpu: int = 1,
                               memory: int = 2,
                               replica_count: int = 1,
                               min_replica_count: Optional[int] = None,
                               max_replica_count: Optional[int] = None,
                               nvidia_gpu: int = 0,
                               environment_variables: Optional[Dict[str, str]] = None,
                               enable_auth: bool = True,
                               target_node_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new model deployment in Cloudera ML
        
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
            environment_variables: Dictionary of environment variables (optional)
            enable_auth: Whether to enable authentication (default: True)
            target_node_selector: Target node selector for the deployment (optional)
            
        Returns:
            Dict with success flag, message, and model deployment data
        """
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
        
        if min_replica_count is not None:
            params["min_replica_count"] = min_replica_count
            
        if max_replica_count is not None:
            params["max_replica_count"] = max_replica_count
            
        if environment_variables:
            params["environment_variables"] = environment_variables
            
        if target_node_selector:
            params["target_node_selector"] = target_node_selector
            
        return functions.create_model_deployment(self.config, params)
    
    def delete_application(self, application_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete an application in Cloudera ML
        
        Args:
            application_id: ID of the application to delete
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with success flag and message
        """
        params = {
            "application_id": application_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.delete_application(self.config, params)
    
    def delete_experiment(self, experiment_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete an experiment in Cloudera ML
        
        Args:
            experiment_id: ID of the experiment to delete
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with success flag and message
        """
        params = {
            "experiment_id": experiment_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.delete_experiment(self.config, params)
    
    def delete_experiment_run(self, experiment_id: str, run_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete an experiment run in Cloudera ML
        
        Args:
            experiment_id: ID of the experiment containing the run
            run_id: ID of the experiment run to delete
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with success flag and message
        """
        params = {
            "experiment_id": experiment_id,
            "run_id": run_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.delete_experiment_run(self.config, params)
    
    def delete_experiment_run_batch(self, experiment_id: str, run_ids: List[str], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete multiple experiment runs in a single request
        
        Args:
            experiment_id: ID of the experiment containing the runs
            run_ids: List of run IDs to delete
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with success flag and message
        """
        params = {
            "experiment_id": experiment_id,
            "run_ids": run_ids
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.delete_experiment_run_batch(self.config, params)
    
    def delete_model(self, model_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a model by ID
        
        Args:
            model_id: ID of the model to delete
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with success flag and message
        """
        params = {
            "model_id": model_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.delete_model(self.config, params)
    
    def delete_project_file(self, file_path: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a file or directory from a Cloudera ML project
        
        Args:
            file_path: Path of the file or directory to delete (relative to project root)
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with success flag and message
        """
        params = {
            "file_path": file_path
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.delete_project_file(self.config, params)
    
    def get_application(self, application_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get details of a specific application from a Cloudera ML project
        
        Args:
            application_id: ID of the application to get details for
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with application details
        """
        params = {
            "application_id": application_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.get_application(self.config, params)
    
    def get_experiment(self, experiment_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get details of a specific experiment from a Cloudera ML project
        
        Args:
            experiment_id: ID of the experiment to get details for
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with experiment details
        """
        params = {
            "experiment_id": experiment_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.get_experiment(self.config, params)
    
    def get_experiment_run(self, experiment_id: str, run_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get details of a specific experiment run from a Cloudera ML project
        
        Args:
            experiment_id: ID of the experiment containing the run
            run_id: ID of the experiment run to get details for
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with experiment run details
        """
        params = {
            "experiment_id": experiment_id,
            "run_id": run_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.get_experiment_run(self.config, params)
    
    def get_job(self, job_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get details of a specific job from a Cloudera ML project
        
        Args:
            job_id: ID of the job to get details for
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with job details
        """
        params = {
            "job_id": job_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.get_job(self.config, params)
    
    def get_job_run(self, job_run_id: str, project_id: str = None, **kwargs) -> dict:
        """Get details of a job run with the specified ID.

        Args:
            job_run_id (str): ID of the job run to retrieve.
            project_id (str, optional): ID of the project where the job run exists. Defaults to the project ID in the MCP object.

        Returns:
            dict: Details of the job run.
        """
        if not project_id and self.config["project_id"]:
            project_id = self.config["project_id"]
        return functions.get_job_run(self.config, {'job_run_id': job_run_id, 'project_id': project_id, **kwargs})
    
    def get_model(self, model_id: str, project_id: str = None, **kwargs) -> dict:
        """Get details of a model with the specified ID.

        Args:
            model_id (str): ID of the model to retrieve.
            project_id (str, optional): ID of the project where the model exists. Defaults to the project ID in the MCP object.

        Returns:
            dict: Details of the model.
        """
        if not project_id and self.config["project_id"]:
            project_id = self.config["project_id"]
        return functions.get_model(self.config, {'model_id': model_id, 'project_id': project_id, **kwargs})
    
    def get_model_build(self, model_id: str, build_id: str, project_id: str = None, **kwargs) -> dict:
        """Get details of a specific model build with the specified ID.

        Args:
            model_id (str): ID of the model that contains the build.
            build_id (str): ID of the model build to retrieve.
            project_id (str, optional): ID of the project where the model exists. Defaults to the project ID in the MCP object.

        Returns:
            dict: Details of the model build.
        """
        if not project_id and self.config["project_id"]:
            project_id = self.config["project_id"]
        return functions.get_model_build(self.config, {'model_id': model_id, 'build_id': build_id, 'project_id': project_id, **kwargs})
    
    def get_model_deployment(self, model_id: str, deployment_id: str, project_id: str = None, **kwargs) -> dict:
        """Get details of a specific model deployment with the specified ID.

        Args:
            model_id (str): ID of the model that contains the deployment.
            deployment_id (str): ID of the model deployment to retrieve.
            project_id (str, optional): ID of the project where the model exists. Defaults to the project ID in the MCP object.

        Returns:
            dict: Details of the model deployment.
        """
        if not project_id and self.config["project_id"]:
            project_id = self.config["project_id"]
        return functions.get_model_deployment(self.config, {'model_id': model_id, 'deployment_id': deployment_id, 'project_id': project_id, **kwargs})
    
    def create_experiment_run(self, project_id: str, experiment_id: str, 
                             name: Optional[str] = None,
                             description: Optional[str] = None,
                             metrics: Optional[Dict[str, Any]] = None,
                             parameters: Optional[Dict[str, Any]] = None,
                             tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new experiment run in Cloudera ML
        
        Args:
            project_id: ID of the project
            experiment_id: ID of the experiment for the run
            name: Name of the run (optional)
            description: Description of the run (optional)
            metrics: Dictionary of metrics (optional)
            parameters: Dictionary of parameters (optional)
            tags: List of tags (optional)
            
        Returns:
            Dict with success flag, message, and experiment run data
        """
        params = {
            "project_id": project_id,
            "experiment_id": experiment_id
        }
        
        if name:
            params["name"] = name
            
        if description:
            params["description"] = description
            
        if metrics:
            params["metrics"] = metrics
            
        if parameters:
            params["parameters"] = parameters
            
        if tags:
            params["tags"] = tags
            
        return functions.create_experiment_run(self.config, params)
    
    def list_experiments(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List experiments in a Cloudera ML project
        
        Args:
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing list of experiments
        """
        params = {}
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.list_experiments(self.config, params)
    
    def list_job_runs(self, job_id: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List job runs in a Cloudera ML project
        
        Args:
            job_id: If provided, only list runs for this specific job
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing list of job runs
        """
        params = {}
        
        if job_id:
            params["job_id"] = job_id
            
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.list_job_runs(self.config, params)
    
    def list_models(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List models in a Cloudera ML project
        
        Args:
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing list of models
        """
        params = {}
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.list_models(self.config, params)
    
    def list_model_builds(self, model_id: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List model builds in a Cloudera ML project
        
        Args:
            model_id: If provided, only list builds for this specific model
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing list of model builds
        """
        params = {}
        
        if model_id:
            params["model_id"] = model_id
            
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.list_model_builds(self.config, params)
    
    def list_model_deployments(self, model_id: Optional[str] = None, build_id: Optional[str] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List model deployments in a Cloudera ML project
        
        Args:
            model_id: If provided, only list deployments for this specific model
            build_id: If provided, only list deployments for this specific build
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing list of model deployments
        """
        params = {}
        
        if model_id:
            params["model_id"] = model_id
            
        if build_id:
            params["build_id"] = build_id
            
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.list_model_deployments(self.config, params)
    
    def list_project_files(self, project_id: str, path: Optional[str] = "") -> Dict[str, Any]:
        """
        List files in a Cloudera ML project
        
        Args:
            project_id: ID of the project
            path: Path to list files from (relative to project root)
            
        Returns:
            Dictionary containing list of project files
        """
        params = {
            "project_id": project_id
        }
        
        if path:
            params["path"] = path
            
        return functions.list_project_files(self.config, params)

    def log_experiment_run_batch(self, experiment_id: str, run_updates: List[Dict[str, Any]], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Log metrics and parameters for multiple experiment runs in a batch
        
        Args:
            experiment_id: ID of the experiment containing the runs
            run_updates: List of run update objects, each containing:
                - id: ID of the run to update
                - metrics (optional): Dictionary of metrics to log
                - parameters (optional): Dictionary of parameters to log
                - tags (optional): List of tags to add to the run
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing operation result
        """
        params = {
            "experiment_id": experiment_id,
            "run_updates": run_updates
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.log_experiment_run_batch(self.config, params)

    def restart_application(self, application_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Restart a running application in a Cloudera ML project
        
        Args:
            application_id: ID of the application to restart
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing operation result
        """
        params = {
            "application_id": application_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.restart_application(self.config, params)
    
    def update_job(self, job_id: str, 
                  name: Optional[str] = None, 
                  script: Optional[str] = None,
                  kernel: Optional[str] = None,
                  cpu: Optional[int] = None, 
                  memory: Optional[int] = None,
                  nvidia_gpu: Optional[int] = None,
                  runtime_identifier: Optional[str] = None,
                  environment_variables: Optional[Dict[str, str]] = None,
                  project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing job in Cloudera ML
        
        Args:
            job_id: ID of the job to update
            name: New name for the job (optional)
            script: New script path for the job (optional)
            kernel: New kernel type (optional)
            cpu: New CPU cores allocation (optional)
            memory: New memory allocation in GB (optional)
            nvidia_gpu: New GPU allocation (optional)
            runtime_identifier: New runtime identifier (optional)
            environment_variables: New environment variables (optional)
            project_id: Project ID (optional if set in configuration)
            
        Returns:
            Dict with success flag, message, and job data
        """
        params = {
            "job_id": job_id
        }
        
        if project_id:
            params["project_id"] = project_id
        
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
            params["environment_variables"] = environment_variables
            
        return functions.update_job(self.config, params)
    
    def update_project(self, 
                      name: Optional[str] = None,
                      summary: Optional[str] = None,
                      template: Optional[str] = None,
                      public: Optional[bool] = None,
                      disable_git_repo: Optional[bool] = None,
                      project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a project in Cloudera ML
        
        Args:
            name: New name for the project (optional)
            summary: New summary for the project (optional)
            template: New template for the project (optional)
            public: Whether the project should be public (optional)
            disable_git_repo: Whether to disable the Git repository (optional)
            project_id: ID of the project to update (optional if set in configuration)
            
        Returns:
            Dict with success flag, message, and project data
        """
        params = {}
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
        
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
            
        return functions.update_project(self.config, params)
    
    def update_project_file_metadata(self, file_path: str,
                                    description: Optional[str] = None,
                                    hidden: Optional[bool] = None,
                                    project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update metadata of a file in a Cloudera ML project
        
        Args:
            file_path: Path of the file relative to the project root
            description: New description for the file (optional)
            hidden: Whether the file should be hidden (optional)
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dict with success flag, message, and file metadata
        """
        params = {
            "file_path": file_path
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
        
        # Add optional parameters if provided
        if description is not None:
            params["description"] = description
            
        if hidden is not None:
            params["hidden"] = hidden
            
        return functions.update_project_file_metadata(self.config, params)

    def stop_application(self, application_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop a running application in a Cloudera ML project
        
        Args:
            application_id: ID of the application to stop
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing operation result
        """
        params = {
            "application_id": application_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.stop_application(self.config, params)
    
    def stop_job_run(self, job_id: str, run_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop a running job run in a Cloudera ML project
        
        Args:
            job_id: ID of the job
            run_id: ID of the job run to stop
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing operation result
        """
        params = {
            "job_id": job_id,
            "run_id": run_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.stop_job_run(self.config, params)
    
    def stop_model_deployment(self, deployment_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop a model deployment in a Cloudera ML project
        
        Args:
            deployment_id: ID of the model deployment to stop
            project_id: ID of the project (optional if set in configuration)
            
        Returns:
            Dictionary containing operation result
        """
        params = {
            "deployment_id": deployment_id
        }
        
        if project_id:
            params["project_id"] = project_id
        elif "project_id" in self.config:
            params["project_id"] = self.config["project_id"]
        else:
            return {
                "success": False, 
                "message": "Project ID is required but not provided in parameters or configuration"
            }
            
        return functions.stop_model_deployment(self.config, params)

    # Function declaration map for Claude to understand available functions
    FUNCTIONS = {
        "upload_file": {
            "description": "Upload a single file to Cloudera ML root directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Local path to the file to upload"
                    },
                    "target_name": {
                        "type": "string",
                        "description": "Optional name to use for the uploaded file"
                    }
                },
                "required": ["file_path"]
            }
        },
        "upload_folder": {
            "description": "Upload a folder to Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_path": {
                        "type": "string",
                        "description": "Local path to the folder to upload"
                    },
                    "ignore_folders": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Folders to ignore during upload"
                    }
                },
                "required": ["folder_path"]
            }
        },
        "create_job": {
            "description": "Create a new Cloudera ML job",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Job name"
                    },
                    "script": {
                        "type": "string",
                        "description": "Script path relative to project root"
                    },
                    "kernel": {
                        "type": "string",
                        "description": "Kernel type (default: python3)"
                    },
                    "cpu": {
                        "type": "integer",
                        "description": "CPU cores (default: 1)"
                    },
                    "memory": {
                        "type": "integer",
                        "description": "Memory in GB (default: 1)"
                    },
                    "nvidia_gpu": {
                        "type": "integer",
                        "description": "Number of GPUs (default: 0)"
                    },
                    "runtime_identifier": {
                        "type": "string",
                        "description": "Runtime environment identifier"
                    }
                },
                "required": ["name", "script"]
            }
        },
        "list_jobs": {
            "description": "List jobs in the Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "list_applications": {
            "description": "List applications in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                }
            }
        },
        "delete_job": {
            "description": "Delete a job by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job to delete"
                    }
                },
                "required": ["job_id"]
            }
        },
        "delete_all_jobs": {
            "description": "Delete all jobs in the project",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "get_project_id": {
            "description": "Get project ID from a project name",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project to find"
                    }
                },
                "required": ["project_name"]
            }
        },
        "get_runtimes": {
            "description": "Get available runtimes from Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "batch_list_projects": {
            "description": "Return a list of projects given a list of project IDs",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of project IDs to return details for"
                    }
                },
                "required": ["project_ids"]
            }
        },
        "create_experiment": {
            "description": "Create a new experiment in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Experiment name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Experiment description (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID (optional if set in configuration)"
                    }
                },
                "required": ["name"]
            }
        },
        "create_job_run": {
            "description": "Create a run for an existing job in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project containing the job"
                    },
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job to run"
                    },
                    "runtime_identifier": {
                        "type": "string",
                        "description": "Runtime identifier (optional)"
                    },
                    "environment_variables": {
                        "type": "object",
                        "description": "Dictionary of environment variables (optional)"
                    },
                    "override_config": {
                        "type": "object",
                        "description": "Dictionary with configuration overrides (optional)"
                    }
                },
                "required": ["project_id", "job_id"]
            }
        },
        "create_model_build": {
            "description": "Create a new model build in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project"
                    },
                    "model_id": {
                        "type": "string",
                        "description": "ID of the model to build"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the model script file or main Python file"
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Name of the function that contains the model code"
                    },
                    "kernel": {
                        "type": "string",
                        "description": "Kernel type (default: python3)"
                    },
                    "runtime_identifier": {
                        "type": "string",
                        "description": "Runtime identifier (optional)"
                    },
                    "replica_size": {
                        "type": "string",
                        "description": "Pod size for the build (optional)"
                    },
                    "cpu": {
                        "type": "integer",
                        "description": "CPU cores (default: 1)"
                    },
                    "memory": {
                        "type": "integer",
                        "description": "Memory in GB (default: 2)"
                    },
                    "nvidia_gpu": {
                        "type": "integer",
                        "description": "Number of GPUs (default: 0)"
                    },
                    "use_custom_docker_image": {
                        "type": "boolean",
                        "description": "Whether to use a custom Docker image (default: False)"
                    },
                    "custom_docker_image": {
                        "type": "string",
                        "description": "Custom Docker image to use (optional)"
                    },
                    "environment_variables": {
                        "type": "object",
                        "description": "Dictionary of environment variables (optional)"
                    }
                },
                "required": ["project_id", "model_id", "file_path", "function_name"]
            }
        },
        "create_model_deployment": {
            "description": "Create a new model deployment in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project"
                    },
                    "model_id": {
                        "type": "string",
                        "description": "ID of the model to deploy"
                    },
                    "build_id": {
                        "type": "string",
                        "description": "ID of the model build to deploy"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the deployment"
                    },
                    "cpu": {
                        "type": "integer",
                        "description": "CPU cores (default: 1)"
                    },
                    "memory": {
                        "type": "integer",
                        "description": "Memory in GB (default: 2)"
                    },
                    "replica_count": {
                        "type": "integer",
                        "description": "Number of replicas (default: 1)"
                    },
                    "min_replica_count": {
                        "type": "integer",
                        "description": "Minimum number of replicas (optional)"
                    },
                    "max_replica_count": {
                        "type": "integer",
                        "description": "Maximum number of replicas (optional)"
                    },
                    "nvidia_gpu": {
                        "type": "integer",
                        "description": "Number of GPUs (default: 0)"
                    },
                    "environment_variables": {
                        "type": "object",
                        "description": "Dictionary of environment variables (optional)"
                    },
                    "enable_auth": {
                        "type": "boolean",
                        "description": "Whether to enable authentication (default: True)"
                    },
                    "target_node_selector": {
                        "type": "string",
                        "description": "Target node selector for the deployment (optional)"
                    }
                },
                "required": ["project_id", "model_id", "build_id", "name"]
            }
        },
        "delete_application": {
            "description": "Delete an application in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "ID of the application to delete"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["application_id"]
            }
        },
        "delete_experiment": {
            "description": "Delete an experiment in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment to delete"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id"]
            }
        },
        "delete_experiment_run": {
            "description": "Delete an experiment run in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment containing the run"
                    },
                    "run_id": {
                        "type": "string",
                        "description": "ID of the experiment run to delete"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id", "run_id"]
            }
        },
        "delete_experiment_run_batch": {
            "description": "Delete multiple experiment runs in a single request",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment containing the runs"
                    },
                    "run_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of run IDs to delete"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id", "run_ids"]
            }
        },
        "delete_model": {
            "description": "Delete a model in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "ID of the model to delete"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["model_id"]
            }
        },
        "delete_project_file": {
            "description": "Delete a file or directory from a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path of the file or directory to delete (relative to project root)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["file_path"]
            }
        },
        "get_application": {
            "description": "Get details of a specific application from a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "ID of the application to get details for"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["application_id"]
            }
        },
        "get_experiment": {
            "description": "Get details of a specific experiment from a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment to get details for"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id"]
            }
        },
        "get_experiment_run": {
            "description": "Get details of a specific experiment run from a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment containing the run"
                    },
                    "run_id": {
                        "type": "string",
                        "description": "ID of the experiment run to get details for"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id", "run_id"]
            }
        },
        "get_job": {
            "description": "Get details of a specific job from a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job to get details for"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["job_id"]
            }
        },
        "get_job_run": {
            "description": "Get details of a job run with the specified ID.",
            "required_params": ["job_run_id"],
            "optional_params": ["project_id"],
            "function": get_job_run
        },
        "get_model": {
            "description": "Get details of a model with the specified ID.",
            "required_params": ["model_id"],
            "optional_params": ["project_id"],
            "function": get_model
        },
        "get_model_build": {
            "description": "Get details of a specific model build with the specified ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "ID of the model that contains the build"
                    },
                    "build_id": {
                        "type": "string",
                        "description": "ID of the model build to retrieve"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["model_id", "build_id"]
            }
        },
        "get_model_deployment": {
            "description": "Get details of a specific model deployment with the specified ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "ID of the model that contains the deployment"
                    },
                    "deployment_id": {
                        "type": "string",
                        "description": "ID of the model deployment to retrieve"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["model_id", "deployment_id"]
            }
        },
        "create_experiment_run": {
            "description": "Create a new experiment run in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project"
                    },
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment for the run"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the run (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the run (optional)"
                    },
                    "metrics": {
                        "type": "object",
                        "description": "Dictionary of metrics (optional)"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Dictionary of parameters (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tags (optional)"
                    }
                },
                "required": ["project_id", "experiment_id"]
            }
        },
        "list_experiments": {
            "description": "List experiments in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": []
            }
        },
        "list_job_runs": {
            "description": "List job runs in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "If provided, only list runs for this specific job"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": []
            }
        },
        "list_models": {
            "description": "List models in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": []
            }
        },
        "list_model_builds": {
            "description": "List model builds in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "If provided, only list builds for this specific model"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": []
            }
        },
        "list_model_deployments": {
            "description": "List model deployments in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "If provided, only list deployments for this specific model"
                    },
                    "build_id": {
                        "type": "string",
                        "description": "If provided, only list deployments for this specific build"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": []
            }
        },
        "list_project_files": {
            "description": "List files in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to list files from (relative to project root)"
                    }
                },
                "required": ["project_id"]
            }
        },
        "log_experiment_run_batch": {
            "description": "Log metrics and parameters for multiple experiment runs in a batch",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment containing the runs"
                    },
                    "run_updates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "ID of the run to update"
                                },
                                "metrics": {
                                    "type": "object",
                                    "description": "Dictionary of metrics to log"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Dictionary of parameters to log"
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of tags to add to the run"
                                }
                            }
                        },
                        "description": "List of run update objects, each containing: id, metrics, parameters, tags"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id", "run_updates"]
            }
        },
        "restart_application": {
            "description": "Restart a running application in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "ID of the application to restart"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["application_id"]
            }
        },
        "stop_application": {
            "description": "Stop a running application in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "ID of the application to stop"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["application_id"]
            }
        },
        "stop_job_run": {
            "description": "Stop a running job run in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job"
                    },
                    "run_id": {
                        "type": "string",
                        "description": "ID of the job run to stop"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["job_id", "run_id"]
            }
        },
        "stop_model_deployment": {
            "description": "Stop a model deployment in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "deployment_id": {
                        "type": "string",
                        "description": "ID of the model deployment to stop"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["deployment_id"]
            }
        },
        "update_application": {
            "description": "Update an application in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "ID of the application to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the application (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the application (optional)"
                    },
                    "cpu": {
                        "type": "integer",
                        "description": "New CPU cores allocation (optional)"
                    },
                    "memory": {
                        "type": "integer",
                        "description": "New memory allocation in GB (optional)"
                    },
                    "nvidia_gpu": {
                        "type": "integer",
                        "description": "New GPU allocation (optional)"
                    },
                    "environment_variables": {
                        "type": "object",
                        "description": "New environment variables (optional)"
                    },
                    "runtime_identifier": {
                        "type": "string",
                        "description": "New runtime identifier (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["application_id"]
            }
        },
        "update_experiment": {
            "description": "Update an experiment in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the experiment (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the experiment (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id"]
            }
        },
        "update_experiment_run": {
            "description": "Update an experiment run in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "ID of the experiment containing the run"
                    },
                    "run_id": {
                        "type": "string",
                        "description": "ID of the experiment run to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the experiment run (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the experiment run (optional)"
                    },
                    "metrics": {
                        "type": "object",
                        "description": "New metrics to set for the experiment run (optional)"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "New parameters to set for the experiment run (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags to set for the experiment run (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["experiment_id", "run_id"]
            }
        },
        "update_job": {
            "description": "Update an existing job in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID of the job to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the job (optional)"
                    },
                    "script": {
                        "type": "string",
                        "description": "New script path for the job (optional)"
                    },
                    "kernel": {
                        "type": "string",
                        "description": "New kernel type (optional)"
                    },
                    "cpu": {
                        "type": "integer",
                        "description": "New CPU cores allocation (optional)"
                    },
                    "memory": {
                        "type": "integer",
                        "description": "New memory allocation in GB (optional)"
                    },
                    "nvidia_gpu": {
                        "type": "integer",
                        "description": "New GPU allocation (optional)"
                    },
                    "runtime_identifier": {
                        "type": "string",
                        "description": "New runtime identifier (optional)"
                    },
                    "environment_variables": {
                        "type": "object",
                        "description": "New environment variables (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["job_id"]
            }
        },
        "update_project": {
            "description": "Update a project in Cloudera ML",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "New name for the project (optional)"
                    },
                    "summary": {
                        "type": "string",
                        "description": "New summary for the project (optional)"
                    },
                    "template": {
                        "type": "string",
                        "description": "New template for the project (optional)"
                    },
                    "public": {
                        "type": "boolean",
                        "description": "Whether the project should be public (optional)"
                    },
                    "disable_git_repo": {
                        "type": "boolean",
                        "description": "Whether to disable the Git repository (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project to update (optional if set in configuration)"
                    }
                },
                "required": []
            }
        },
        "update_project_file_metadata": {
            "description": "Update metadata of a file in a Cloudera ML project",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path of the file relative to the project root"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the file (optional)"
                    },
                    "hidden": {
                        "type": "boolean",
                        "description": "Whether the file should be hidden (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project (optional if set in configuration)"
                    }
                },
                "required": ["file_path"]
            }
        }
    } 