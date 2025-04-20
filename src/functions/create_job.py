"""Create job function for Cloudera ML MCP"""

import requests
import json
import os
from typing import Dict, Any, Optional
from urllib.parse import urlparse


def create_job(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new Cloudera ML job
    
    Args:
        config: MCP configuration
        params: Function parameters
            - name: Job name (required)
            - script: Script path relative to project root (required)
            - runtime_identifier: Runtime environment identifier (required for ML Runtime projects)
            - kernel: Kernel type (default: "python3")
            - cpu: CPU cores (default: 1)
            - memory: Memory in GB (default: 1)
            - nvidia_gpu: Number of GPUs (default: 0)
            - api_version: API version (default: v2)
            
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
            
        project_id = config.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project_id in configuration"
            }
        
        # Check if host is provided
        if not config.get('host'):
            return {
                "success": False,
                "message": "Missing host URL in configuration. Check your .env file."
            }
        
        # Set default values for optional parameters
        kernel = params.get("kernel", "python3")
        cpu = int(params.get("cpu", 1))  # Ensure these are integers
        memory = int(params.get("memory", 1))
        nvidia_gpu = int(params.get("nvidia_gpu", 0))
        api_version = params.get("api_version", "v2")
        
        # Use a default runtime if none specified (REQUIRED for ML Runtime projects)
        # Using validated runtime from list_runtimes.py
        runtime_identifier = params.get("runtime_identifier")
        if not runtime_identifier:
            # Default to a runtime available in the Cloudera ML instance
            runtime_identifier = "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-jupyterlab-python3.10-standard:2024.10.1-b12"
            print(f"No runtime_identifier provided, using default: {runtime_identifier}")
        
        # Create job data payload according to API requirements
        job_data = {
            "name": name,
            "script": script,
            "kernel": kernel,
            "cpu": cpu,
            "memory": memory,
            "nvidia_gpu": nvidia_gpu,
            "runtime_identifier": runtime_identifier  # Always include runtime_identifier
        }
        
        # Properly format the host URL
        host = config['host'].strip()
        
        # Debug the input host URL
        print(f"Original host URL: {host}")
        
        # Parse URL to ensure it's properly formatted
        parsed_url = urlparse(host)
        
        # If no scheme is provided, add https://
        if not parsed_url.scheme:
            host = f"https://{host}"
            parsed_url = urlparse(host)
        
        # Ensure we have a host part
        if not parsed_url.netloc:
            error_msg = f"Invalid host URL: {host}. Please check your .env file."
            print(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
        
        # Remove duplicate https:// if present
        if host.startswith("https://https://"):
            host = host.replace("https://https://", "https://")
        
        # Remove trailing slash if present
        host = host.rstrip("/")
        
        # Debug the cleaned host URL
        print(f"Cleaned host URL: {host}")
        
        # Setup headers
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Print environment variables for debugging (don't print API key)
        print(f"Environment variables:")
        for key, value in os.environ.items():
            if key.startswith("CLOUDERA_ML") and "API_KEY" not in key:
                print(f"  {key}: {value}")
        
        # Send API request
        url = f"{host}/api/{api_version}/projects/{project_id}/jobs"
        
        # Debug output
        print(f"Creating job '{name}' at: {url}")
        print(f"Job payload: {json.dumps(job_data, indent=2)}")
        
        response = requests.post(url, json=job_data, headers=headers)
        
        # Enhanced error handling for 400 errors
        if response.status_code == 400:
            error_message = "Bad Request - Invalid parameters"
            try:
                error_details = response.json()
                error_message = f"API Error: {error_details.get('message', 'Unknown error')}"
                print(f"Full error response: {json.dumps(error_details, indent=2)}")
            except:
                pass
                
            return {
                "success": False,
                "message": error_message,
                "status_code": response.status_code,
                "payload_sent": job_data
            }
            
        # For other errors
        response.raise_for_status()
        
        # Return success response
        return {
            "success": True,
            "message": f"Job '{name}' created successfully",
            "job": response.json()
        }
    except requests.exceptions.RequestException as e:
        error_message = f"API request error: {str(e)}"
        # Try to extract more details from the response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                if 'message' in error_details:
                    error_message = f"API error: {error_details['message']}"
                print(f"Full error response: {json.dumps(error_details, indent=2)}")
            except:
                pass
            
        return {
            "success": False,
            "message": error_message,
            "payload_sent": job_data if 'job_data' in locals() else None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating job: {str(e)}"
        } 