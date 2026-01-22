"""In-memory store for pending governance requests"""
from datetime import datetime
from typing import Dict, Optional, Any
from app.api.models import GovernanceRequest

# Global in-memory store
PENDING_REQUESTS: Dict[str, Dict[str, Any]] = {}

def add_request(request_id: str, request: GovernanceRequest, status: str = "PENDING", reason: str = "") -> None:
    """
    Add a request to the pending requests store
    
    Args:
        request_id: Unique identifier for the request
        request: The governance request object
        status: Status of the request (default: "PENDING")
        reason: Reason for the request (policy reason)
    """
    PENDING_REQUESTS[request_id] = {
        "id": request_id,
        "resource": request.resource,
        "action": request.action,
        "args": request.args,
        "status": status,
        "reason": reason,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

def get_request(request_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a request by ID
    
    Args:
        request_id: Unique identifier for the request
    
    Returns:
        Request dictionary or None if not found
    """
    return PENDING_REQUESTS.get(request_id)

def get_all_requests() -> list:
    """
    Get all pending requests
    
    Returns:
        List of all pending requests
    """
    return list(PENDING_REQUESTS.values())

def update_request_status(request_id: str, status: str) -> bool:
    """
    Update the status of a request
    
    Args:
        request_id: Unique identifier for the request
        status: New status (e.g., "APPROVED", "REJECTED")
    
    Returns:
        True if updated, False if request not found
    """
    if request_id not in PENDING_REQUESTS:
        return False
    
    PENDING_REQUESTS[request_id]["status"] = status
    PENDING_REQUESTS[request_id]["updated_at"] = datetime.utcnow().isoformat()
    return True

def remove_request(request_id: str) -> bool:
    """
    Remove a request from the store
    
    Args:
        request_id: Unique identifier for the request
    
    Returns:
        True if removed, False if request not found
    """
    if request_id in PENDING_REQUESTS:
        del PENDING_REQUESTS[request_id]
        return True
    return False


