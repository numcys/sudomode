"""SudoMode Client SDK - Python wrapper for governance API

This module provides a client for interacting with the SudoMode governance server.
It handles policy evaluation, approval workflows, and request management.
"""
import httpx
import time
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger("sudomode.client")
logger.addHandler(logging.NullHandler())

def configure_logging(level=logging.INFO):
    """Configure logging for the SudoMode client.
    
    Args:
        level: Logging level (default: logging.INFO)
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [SudoMode] %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)

class GovernanceResponse(BaseModel):
    """Response model matching the server API"""
    status: str  # "ALLOW", "DENY", or "REQUIRE_APPROVAL"
    reason: str
    request_id: Optional[str] = None  # Added to track approval requests

class SudoClient:
    """Client for interacting with SudoMode governance server"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the SudoMode client
        
        Args:
            base_url: Base URL of the SudoMode server (default: http://localhost:8000)
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=30.0
        )
    
    def check(self, resource: str, action: str, args: Optional[Dict[str, Any]] = None) -> GovernanceResponse:
        """
        Check if an action is allowed (low-level API call)
        
        Args:
            resource: The resource to act on (e.g., "database", "stripe.charge")
            action: The action to perform (e.g., "read", "delete", "charge")
            args: Optional dictionary of arguments (e.g., {"amount": 100})
        
        Returns:
            GovernanceResponse with status and reason
        
        Raises:
            httpx.HTTPError: If the request fails
        """
        payload = {
            "resource": resource,
            "action": action,
            "args": args or {}
        }
        
        response = self.client.post("/v1/govern", json=payload)
        response.raise_for_status()
        
        return GovernanceResponse(**response.json())
    
    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific request by ID
        
        Args:
            request_id: The unique identifier of the request
            
        Returns:
            Dictionary containing the request status and details
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = self.client.get(f"/v1/requests/{request_id}")
        response.raise_for_status()
        return response.json()

    def execute(self, resource: str, action: str, args: Optional[Dict[str, Any]] = None, poll_interval: int = 2) -> bool:
        """
        Execute an action with governance check and handle approval workflow
        
        This method:
        - Returns True if the action is ALLOWED
        - Raises PermissionError if the action is DENIED or REJECTED
        - For REQUIRES_APPROVAL, polls until a decision is made
        
        Args:
            resource: The resource to act on (e.g., "database", "stripe.charge")
            action: The action to perform (e.g., "read", "delete", "charge")
            args: Optional dictionary of arguments (e.g., {"amount": 100})
            poll_interval: Time in seconds between status checks (default: 2)
            
        Returns:
            True if the action is allowed or approved
            
        Raises:
            PermissionError: If the action is denied or rejected
            httpx.HTTPError: If the request fails
        """
        result = self.check(resource, action, args)
        
        if result.status == "ALLOW":
            return True
        elif result.status == "DENY":
            raise PermissionError(f"Permission denied: {result.reason}")
        elif result.status == "REQUIRE_APPROVAL":
            if not result.request_id:
                error_msg = "Approval required but no request_id returned"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"Action requires approval. Request ID: {result.request_id}")
            logger.info(f"Polling for approval status every {poll_interval} seconds...")
            
            while True:
                time.sleep(poll_interval)
                try:
                    status_data = self.get_request_status(result.request_id)
                    if status_data["status"] == "APPROVED":
                        logger.info(f"Request {result.request_id} approved")
                        return True
                    elif status_data["status"] == "REJECTED":
                        reason = status_data.get('reason', 'No reason provided')
                        error_msg = f"Request {result.request_id} was rejected: {reason}"
                        logger.warning(error_msg)
                        raise PermissionError(f"Action was rejected by human: {reason}")
                    # If still pending, continue the loop
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        error_msg = f"Request {result.request_id} not found on server"
                        logger.error(error_msg)
                        raise PermissionError("Approval request was not found on the server") from e
                    logger.error(f"HTTP error checking request status: {e}")
                    raise  # Re-raise other HTTP errors
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

