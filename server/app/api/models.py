"""Pydantic models for governance API requests and responses"""
from pydantic import BaseModel
from typing import Dict, Any, Literal, Optional

class GovernanceRequest(BaseModel):
    """Request model for governance check"""
    resource: str
    action: str
    args: Dict[str, Any] = {}

class GovernanceResponse(BaseModel):
    """Response model for governance check"""
    status: Literal["ALLOW", "DENY", "REQUIRE_APPROVAL"]
    reason: str
    request_id: Optional[str] = None  # Included when status is REQUIRE_APPROVAL

