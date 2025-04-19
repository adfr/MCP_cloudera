"""List jobs function for Cloudera ML MCP"""

from typing import Dict, Any
from datetime import datetime

from .. import utils


def list_jobs(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List jobs in the Cloudera ML project
    
    Args:
        config: MCP configuration
        params: Function parameters (unused)
        
    Returns:
        Dictionary containing list of jobs
    """
    try:
        session = utils.get_session(config)
        project_id = config["project_id"]
        
        url = utils.format_url(config, f"/api/v2/projects/{project_id}/jobs")
        response = session.get(url)
        response.raise_for_status()
        
        # Format jobs for easier consumption
        jobs_data = response.json()
        jobs = jobs_data.get("jobs", [])
        
        formatted_jobs = []
        for job in jobs:
            # Format date for better readability
            created_at = job.get("created_at")
            if created_at:
                try:
                    # Parse ISO format date and format it
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                except (ValueError, TypeError):
                    formatted_date = created_at
            else:
                formatted_date = "Unknown"
            
            formatted_jobs.append({
                "id": job.get("id"),
                "name": job.get("name"),
                "status": job.get("status"),
                "created_at": formatted_date,
                "script": job.get("script"),
                "cpu": job.get("cpu"),
                "memory": job.get("memory"),
                "gpu": job.get("nvidia_gpu")
            })
        
        return {
            "success": True,
            "message": f"Found {len(formatted_jobs)} jobs",
            "jobs": formatted_jobs,
            "count": len(formatted_jobs)
        }
    except Exception as e:
        return {
            "success": False,
            "message": utils.handle_error(e)
        } 