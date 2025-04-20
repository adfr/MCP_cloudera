"""Delete job function for Cloudera ML MCP"""

import requests
from typing import Dict, Any


def delete_job(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a job by ID
    
    Args:
        config: MCP configuration
        params: Function parameters
            - job_id: ID of the job to delete
        
    Returns:
        Delete operation results
    """
    try:
        # Validate job_id parameter
        job_id = params.get("job_id")
        if not job_id:
            raise ValueError("job_id is required")
        
        project_id = config.get("project_id")
        if not project_id:
            return {
                "success": False,
                "message": "Missing project_id in configuration"
            }
            
        # Properly format the host URL
        host = config['host'].strip()
        # Remove duplicate https:// if present
        if host.startswith("https://https://"):
            host = host.replace("https://https://", "https://")
        # Ensure URL has a scheme
        if not host.startswith(("http://", "https://")):
            host = "https://" + host
        # Remove trailing slash if present
        host = host.rstrip("/")
        
        # Setup common headers
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # First get the job details to show in the result
        job_url = f"{host}/api/v2/projects/{project_id}/jobs/{job_id}"
        try:
            print(f"Getting job details from: {job_url}")  # Debug output
            job_response = requests.get(job_url, headers=headers)
            job_response.raise_for_status()
            job_info = job_response.json()
            job_name = job_info.get("name", "Unknown job")
        except Exception:
            # If we can't get the job details, continue with deletion anyway
            job_name = f"Job ID {job_id}"
        
        # Delete the job
        delete_url = f"{host}/api/v2/projects/{project_id}/jobs/{job_id}"
        print(f"Deleting job at: {delete_url}")  # Debug output
        response = requests.delete(delete_url, headers=headers)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Successfully deleted '{job_name}'",
            "job_id": job_id
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"API request error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting job: {str(e)}"
        } 