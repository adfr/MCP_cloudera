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
    
    def upload_folder(self, folder_path: str, ignore_folders: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Upload a folder to Cloudera ML
        
        Args:
            folder_path: Local path to the folder to upload
            ignore_folders: Folders to ignore during upload
            
        Returns:
            Upload results
        """
        return functions.upload_folder(self.config, {
            "folder_path": folder_path,
            "ignore_folders": ignore_folders
        })
    
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
    
    # Function declaration map for Claude to understand available functions
    FUNCTIONS = {
        "upload_folder": {
            "description": "Upload a folder to Cloudera ML",
            "parameters": {
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
        },
        "create_job": {
            "description": "Create a new Cloudera ML job",
            "parameters": {
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
        },
        "list_jobs": {
            "description": "List jobs in the Cloudera ML project"
        },
        "delete_job": {
            "description": "Delete a job by ID",
            "parameters": {
                "job_id": {
                    "type": "string",
                    "description": "ID of the job to delete"
                }
            },
            "required": ["job_id"]
        },
        "delete_all_jobs": {
            "description": "Delete all jobs in the project"
        },
        "get_project_id": {
            "description": "Get project ID from a project name",
            "parameters": {
                "project_name": {
                    "type": "string",
                    "description": "Name of the project to find"
                }
            },
            "required": ["project_name"]
        },
        "list_projects": {
            "description": "List all available projects"
        },
        "get_runtimes": {
            "description": "Get available runtimes from Cloudera ML"
        }
    } 