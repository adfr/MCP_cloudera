"""Delete all jobs function for Cloudera ML MCP"""

from typing import Dict, Any, List

from .. import utils


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
        session = utils.get_session(config)
        project_id = config["project_id"]
        
        # Get all jobs
        jobs_url = utils.format_url(config, f"/api/v2/projects/{project_id}/jobs")
        response = session.get(jobs_url)
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
                delete_url = utils.format_url(config, f"/api/v2/projects/{project_id}/jobs/{job_id}")
                delete_response = session.delete(delete_url)
                delete_response.raise_for_status()
                
                deleted_jobs.append({
                    "id": job_id,
                    "name": job_name
                })
            except Exception as e:
                failed_jobs.append({
                    "id": job_id,
                    "name": job_name,
                    "error": utils.handle_error(e)
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
    except Exception as e:
        return {
            "success": False,
            "message": utils.handle_error(e)
        } 