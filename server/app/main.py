"""FastAPI application entry point for SudoMode"""
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.core.engine import PolicyEngine
from app.core.config import settings
from app.core.store import add_request, get_request, get_all_requests, update_request_status, remove_request
from app.api.models import GovernanceRequest, GovernanceResponse
from app.services.slack import SlackService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SudoMode AI",
    description="Governance & Authorization Layer for AI Agents",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize policy engine
engine = PolicyEngine()

# Initialize Slack service
slack_service = SlackService(webhook_url=settings.SLACK_WEBHOOK_URL)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/v1/govern", response_model=GovernanceResponse)
async def govern(request: GovernanceRequest) -> GovernanceResponse:
    """
    Governance endpoint - evaluates a request against policy rules
    
    Args:
        request: GovernanceRequest with resource, action, and args
    
    Returns:
        GovernanceResponse with status (ALLOW/DENY/REQUIRE_APPROVAL) and reason
    """
    # Evaluate the request
    response = engine.evaluate(request)
    
    # If approval is required, store the request and send Slack notification
    if response.status == "REQUIRE_APPROVAL":
        # Generate a request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Store the pending request
        add_request(
            request_id=request_id,
            request=request,
            status="PENDING",
            reason=response.reason
        )
        
        # Include request_id in the response
        response.request_id = request_id
        
        # Send Slack alert asynchronously (don't wait for it)
        # This is fire-and-forget - we return the response immediately
        try:
            await slack_service.send_alert(
                request_data=request,
                rule_reason=response.reason,
                request_id=request_id
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Failed to send Slack notification: {e}")
    
    return response

@app.get("/v1/requests")
async def list_requests():
    """
    Get all pending requests
    
    Returns:
        List of all pending requests
    """
    return {"requests": get_all_requests()}

@app.get("/v1/requests/{request_id}", response_model=dict)
async def get_request_status(request_id: str):
    """
    Get the status of a specific request by ID
    
    Args:
        request_id: The unique identifier of the request
        
    Returns:
        The request details including status, or 404 if not found
    """
    request_data = get_request(request_id)
    if not request_data:
        raise HTTPException(status_code=404, detail="Request not found")
    return request_data

@app.post("/v1/requests/{request_id}/approve")
async def approve_request(request_id: str):
    """
    Approve a pending request
    
    Args:
        request_id: Unique identifier for the request
    
    Returns:
        Success message with request details
    """
    request_data = get_request(request_id)
    if not request_data:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request_data["status"] != "PENDING":
        raise HTTPException(
            status_code=400, 
            detail=f"Request is already {request_data['status']}"
        )
    
    # Update status to APPROVED
    update_request_status(request_id, "APPROVED")
    
    # In a real app, this would trigger a webhook back to the agent
    # For now, we just mark it as approved
    
    return {
        "status": "success",
        "message": "Request approved",
        "request_id": request_id,
        "request": get_request(request_id)
    }

@app.post("/v1/requests/{request_id}/reject")
async def reject_request(request_id: str):
    """
    Reject a pending request
    
    Args:
        request_id: Unique identifier for the request
    
    Returns:
        Success message
    """
    request_data = get_request(request_id)
    if not request_data:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request_data["status"] != "PENDING":
        raise HTTPException(
            status_code=400, 
            detail=f"Request is already {request_data['status']}"
        )
    
    # Update status to REJECTED (or remove it)
    update_request_status(request_id, "REJECTED")
    
    return {
        "status": "success",
        "message": "Request rejected",
        "request_id": request_id
    }

