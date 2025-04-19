"""Delete job function for Cloudera ML MCP"""

from typing import Dict, Any

from .. import utils


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
        
        session = utils.get_session(config)
        project_id = config["project_id"]
        
        # First get the job details to show in the result
        job_url = utils.format_url(config, f"/api/v2/projects/{project_id}/jobs/{job_id}")
        try:
            job_response = session.get(job_url)
            job_response.raise_for_status()
            job_info = job_response.json()
            job_name = job_info.get("name", "Unknown job")
        except Exception:
            # If we can't get the job details, continue with deletion anyway
            job_name = f"Job ID {job_id}"
        
        # Delete the job
        delete_url = utils.format_url(config, f"/api/v2/projects/{project_id}/jobs/{job_id}")
        response = session.delete(delete_url)
        response.raise_for_status()
        
        return {
            "success": True,
            "message": f"Successfully deleted '{job_name}'",
            "job_id": job_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": utils.handle_error(e)
        } 