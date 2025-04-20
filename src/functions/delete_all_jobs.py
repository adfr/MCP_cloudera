"""Delete all jobs function for Cloudera ML MCP"""

import requests
from typing import Dict, Any, List


def delete_all_jobs(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete all jobs in the project
    
    Args:
        config: MCP configuration
        params: Function parameters (unused)
        
    Returns:
        Delete operation results
    """
    try:
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
        
        # Get all jobs
        jobs_url = f"{host}/api/v2/projects/{project_id}/jobs"
        print(f"Getting all jobs from: {jobs_url}")  # Debug output
        response = requests.get(jobs_url, headers=headers)
        response.raise_for_status()
        
        jobs_data = response.json()
        jobs = jobs_data.get("jobs", [])
        
        if not jobs:
            return {
                "success": True,
                "message": "No jobs found to delete",
                "deleted_count": 0,
                "deleted_jobs": []
            }
        
        # Delete each job
        deleted_jobs = []
        failed_jobs = []
        
        for job in jobs:
            job_id = job.get("id")
            job_name = job.get("name", f"Job ID {job_id}")
            
            try:
                delete_url = f"{host}/api/v2/projects/{project_id}/jobs/{job_id}"
                print(f"Deleting job: {job_name} at: {delete_url}")  # Debug output
                delete_response = requests.delete(delete_url, headers=headers)
                delete_response.raise_for_status()
                
                deleted_jobs.append({
                    "id": job_id,
                    "name": job_name
                })
            except Exception as e:
                failed_jobs.append({
                    "id": job_id,
                    "name": job_name,
                    "error": str(e)
                })
        
        # Prepare result
        success = len(failed_jobs) == 0
        message = (
            f"Successfully deleted all {len(deleted_jobs)} jobs" 
            if success else 
            f"Deleted {len(deleted_jobs)} jobs, but failed to delete {len(failed_jobs)} jobs"
        )
        
        return {
            "success": success,
            "message": message,
            "deleted_count": len(deleted_jobs),
            "deleted_jobs": deleted_jobs,
            "failed_count": len(failed_jobs),
            "failed_jobs": failed_jobs
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"API request error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting jobs: {str(e)}"
        } 