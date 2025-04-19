"""Utility functions for Cloudera ML MCP"""

import requests
from typing import Dict, Any


def get_session(config: Dict[str, str]) -> requests.Session:
    """
    Create a requests session with proper authentication headers
    
    Args:
        config: MCP configuration containing host and apiKey
        
    Returns:
        Configured requests session
    """
    session = requests.Session()
    session.headers.update({
        'Authorization': f"Bearer {config['api_key']}"
    })
    return session


def handle_error(error: Exception) -> str:
    """
    Format error messages for consistent handling
    
    Args:
        error: Exception that was raised
        
    Returns:
        Formatted error message
    """
    if isinstance(error, requests.RequestException):
        if error.response is not None:
            try:
                error_data = error.response.json()
                if 'message' in error_data:
                    return error_data['message']
            except ValueError:
                pass
            return f"HTTP Error {error.response.status_code}: {error.response.text}"
        return str(error)
    return str(error)


def format_url(config: Dict[str, str], endpoint: str) -> str:
    """
    Format full URL from host and endpoint
    
    Args:
        config: MCP configuration containing host
        endpoint: API endpoint path
        
    Returns:
        Full URL
    """
    host = config['host']
    # Remove trailing slash from host if present
    if host.endswith('/'):
        host = host[:-1]
    
    # Ensure endpoint starts with slash
    if not endpoint.startswith('/'):
        endpoint = f"/{endpoint}"
        
    return f"{host}{endpoint}" 