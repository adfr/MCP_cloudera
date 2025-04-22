"""Delete job function for Cloudera ML MCP"""

import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Dict, Any


def delete_job(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a job by ID
    
    Args:
        config: MCP configuration with host and api_key
        params: Function parameters
            - job_id: ID of the job to delete
        
    Returns:
        Delete operation results
    """
    # Validate required parameters
    job_id = params.get("job_id")
    if not job_id:
        return {"success": False, "message": "Missing required parameter: job_id"}
    
    # Get project_id from config
    project_id = params.get("project_id") or config.get("project_id")
    if not project_id:
        return {"success": False, "message": "Missing project_id in configuration or parameters"}
    
    # Format host URL correctly
    host = config.get("host", "")
    if not host:
        return {"success": False, "message": "Missing host in configuration"}
    
    # Make sure host has the correct scheme
    parsed_url = urlparse(host)
    if not parsed_url.scheme:
        host = "https://" + host
    elif parsed_url.scheme and "://" in host[len(parsed_url.scheme)+3:]:
        # Fix potential double https:// in the URL
        host = parsed_url.scheme + "://" + host.split("://")[-1]
    
    # Remove trailing slash if present
    host = host.rstrip('/')
    
    api_key = config.get("api_key")
    if not api_key:
        return {"success": False, "message": "Missing api_key in configuration"}
    
    # First, try to get the job details to include in the response
    job_url = f"{host}/api/v2/projects/{project_id}/jobs/{job_id}"
    print(f"Getting job details from: {job_url}")
    
    # Construct curl command for getting job details
    get_job_cmd = [
        "curl", "-s",
        "-H", f"Authorization: Bearer {api_key}",
        job_url
    ]
    
    job_name = f"Job ID {job_id}"
    try:
        # Execute curl command to get job details
        job_result = subprocess.run(get_job_cmd, capture_output=True, text=True)
        
        # If successful, parse the job name
        if job_result.returncode == 0 and job_result.stdout.strip():
            try:
                job_info = json.loads(job_result.stdout)
                job_name = job_info.get("name", job_name)
            except json.JSONDecodeError:
                # If we can't parse the response, continue with deletion anyway
                pass
    except Exception:
        # If we can't get the job details, continue with deletion anyway
        pass
    
    # Build the URL for the delete request
    delete_url = f"{host}/api/v2/projects/{project_id}/jobs/{job_id}"
    print(f"Deleting job with URL: {delete_url}")
    
    # Construct curl command for deletion
    curl_cmd = [
        "curl", "-s", "-X", "DELETE",
        "-H", f"Authorization: Bearer {api_key}",
        delete_url
    ]
    
    try:
        # Execute curl command with debug output
        print(f"Executing curl command: {' '.join(curl_cmd)}")
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        print(f"Curl exit code: {result.returncode}")
        print(f"Curl stdout: '{result.stdout}'")
        print(f"Curl stderr: '{result.stderr}'")
        
        # Check if the curl command was successful
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to delete job: {result.stderr}"
            }
        
        # Parse the response if there is any content
        if result.stdout.strip():
            try:
                response = json.loads(result.stdout)
                
                # Check if there's an error in the response
                if "error" in response:
                    return {
                        "success": False, 
                        "message": f"API error: {response.get('error', {}).get('message', 'Unknown error')}",
                        "details": response.get("error", {})
                    }
                
                return {
                    "success": True,
                    "message": f"Successfully deleted '{job_name}'",
                    "job_id": job_id,
                    "data": response
                }
            except json.JSONDecodeError:
                # If the response is not JSON, it might be empty for a successful deletion
                pass
        
        # If we got here, the deletion was likely successful but returned no content
        return {
            "success": True,
            "message": f"Successfully deleted '{job_name}'",
            "job_id": job_id
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting job: {str(e)}"
        } 