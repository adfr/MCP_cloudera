"""Get runtimes function for Cloudera ML MCP"""

import requests
import json
from typing import Dict, Any
from urllib.parse import urlparse


def get_runtimes(config: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get available runtimes from Cloudera ML
    
    Args:
        config: MCP configuration
        params: Function parameters (unused)
        
    Returns:
        Dictionary containing list of available runtimes
    """
    try:
        # Check if host is provided
        if not config.get('host'):
            return {
                "success": False,
                "message": "Missing host URL in configuration. Check your .env file."
            }
        
        # Properly format the host URL
        host = config['host'].strip()
        
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
        
        # Setup headers
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Try v2 API first
        url = f"{host}/api/v2/runtimes"
        print(f"Getting runtimes from: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 404:
            # Try fallback to v1 API
            url = f"{host}/api/v1/runtimes"
            print(f"V2 API not found, trying: {url}")
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        api_response = response.json()
        
        # Format runtimes for easier consumption
        formatted_runtimes = []
        
        if "runtimes" in api_response:
            for runtime in api_response["runtimes"]:
                identifier = runtime.get("image_identifier") or runtime.get("runtime_identifier")
                formatted_runtimes.append({
                    "identifier": identifier,
                    "edition": runtime.get("edition", "Unknown"),
                    "type": runtime.get("image_type", "Unknown"),
                    "description": runtime.get("short_description", "No description")
                })
        
        return {
            "success": True,
            "message": f"Found {len(formatted_runtimes)} available runtimes",
            "runtimes": formatted_runtimes,
            "count": len(formatted_runtimes)
        }
    except requests.exceptions.RequestException as e:
        error_message = f"API request error: {str(e)}"
        # Try to extract more details from the response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                if 'message' in error_details:
                    error_message = f"API error: {error_details['message']}"
            except:
                pass
            
        return {
            "success": False,
            "message": error_message
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrieving runtimes: {str(e)}"
        } 