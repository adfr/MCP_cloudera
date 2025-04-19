"""Create job function for Cloudera ML MCP"""

from typing import Dict, Any, Optional

from .. import utils


def create_job(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new Cloudera ML job
    
    Args:
        config: MCP configuration
        params: Function parameters
            - name: Job name
            - script: Script path relative to project root
            - kernel: Kernel type (default: "python3")
            - cpu: CPU cores (default: 1)
            - memory: Memory in GB (default: 1)
            - nvidia_gpu: Number of GPUs (default: 0)
            - runtime_identifier: Runtime environment identifier
            
    Returns:
        Job creation results
    """
    try:
        # Validate required parameters
        name = params.get("name")
        script = params.get("script")
        
        if not name:
            raise ValueError("Job name is required")
        if not script:
            raise ValueError("Script path is required")
        
        # Set default values for optional parameters
        kernel = params.get("kernel", "python3")
        cpu = params.get("cpu", 1)
        memory = params.get("memory", 1)
        nvidia_gpu = params.get("nvidia_gpu", 0)
        runtime_identifier = params.get(
            "runtime_identifier", 
            "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-jupyterlab-python3.10-standard:2024.10.1-b12"
        )
        
        # Create job data payload
        job_data = {
            "name": name,
            "script": script,
            "kernel": kernel,
            "cpu": cpu,
            "memory": memory,
            "nvidia_gpu": nvidia_gpu
        }
        
        # Add runtime identifier if provided
        if runtime_identifier:
            job_data["runtime_identifier"] = runtime_identifier
        
        # Send API request
        session = utils.get_session(config)
        project_id = config["project_id"]
        
        url = utils.format_url(config, f"/api/v2/projects/{project_id}/jobs")
        response = session.post(url, json=job_data)
        response.raise_for_status()
        
        # Return success response
        return {
            "success": True,
            "message": f"Job '{name}' created successfully",
            "job": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "message": utils.handle_error(e)
        } 