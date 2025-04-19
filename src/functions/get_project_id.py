"""
Get project ID from project name.
"""

import json
from typing import Dict, Any

from ..utils import get_session, handle_error, format_url


def get_project_id(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a project ID from a project name.
    
    Args:
        config: MCP configuration with host and api_key
        params: Parameters containing project_name
        
    Returns:
        Dictionary with project information and ID
    """
    try:
        session = get_session(config)
        project_name = params.get("project_name")
        
        if not project_name:
            return {
                "status": "error",
                "message": "Missing project_name parameter"
            }
        
        # Call the API to list all projects
        url = format_url(config, "/api/v2/projects")
        response = session.get(url)
        response.raise_for_status()
        
        # Parse the response
        projects_data = response.json()
        projects = projects_data.get("projects", [])
        
        # Find the project with the matching name
        for project in projects:
            if project.get("name") == project_name:
                return {
                    "status": "success",
                    "project_id": project.get("id"),
                    "project_name": project_name,
                    "project_info": project
                }
        
        # If no project is found
        return {
            "status": "error",
            "message": f"No project found with name: {project_name}"
        }
        
    except Exception as e:
        error_message = handle_error(e)
        return {
            "status": "error",
            "message": f"Failed to get project ID: {error_message}"
        } 