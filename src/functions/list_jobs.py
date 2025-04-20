"""List jobs function for Cloudera ML MCP"""

import requests
from typing import Dict, Any
from datetime import datetime


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
        
        url = f"{host}/api/v2/projects/{project_id}/jobs"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        print(f"Making request to: {url}")  # Debug output
        response = requests.get(url, headers=headers)
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
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"API request error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing jobs: {str(e)}"
        } 