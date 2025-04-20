"""
Get project ID from project name.
"""

import json
import requests
from typing import Dict, Any
from urllib.parse import urlparse


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
        project_name = params.get("project_name")
        
        if not project_name:
            return {
                "status": "error",
                "message": "Missing project_name parameter"
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
        
        url = f"{host}/api/v2/projects"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        print(f"Making request to: {url}")  # Debug output
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Handle special case for listing all projects
        if project_name == "*":
            projects_list = []
            if 'projects' in data and data['projects']:
                for project in data['projects']:
                    projects_list.append({
                        "name": project.get('name'),
                        "id": project.get('id'),
                        "owner": project.get('owner')
                    })
                
                return {
                    "status": "success",
                    "projects": projects_list,
                    "count": len(projects_list)
                }
            else:
                return {
                    "status": "error",
                    "message": "No projects found or you don't have permission to access them",
                    "raw_response": data
                }
        
        # Find the project with the matching name
        if 'projects' in data and data['projects']:
            for project in data['projects']:
                if project.get('name') == project_name:
                    return {
                        "status": "success",
                        "project_id": project.get('id'),
                        "project_name": project_name,
                        "project_info": project
                    }
        
        # If no project is found
        return {
            "status": "error",
            "message": f"No project found with name: {project_name}"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to get project ID: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get project ID: {str(e)}"
        } 