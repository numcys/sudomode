"""Slack integration for sending approval notifications"""
import httpx
import os
import uuid
from typing import Optional
from app.api.models import GovernanceRequest

class SlackService:
    """Service for sending Slack notifications"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack service
        
        Args:
            webhook_url: Slack webhook URL. If not provided, reads from SLACK_WEBHOOK_URL env var
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def send_alert(
        self,
        request_data: GovernanceRequest,
        rule_reason: str,
        request_id: Optional[str] = None
    ) -> bool:
        """
        Send an approval request alert to Slack
        
        Args:
            request_data: The governance request that requires approval
            rule_reason: The reason from the matched policy rule
            request_id: Optional request ID for tracking (generates one if not provided)
        
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self.webhook_url:
            print("Warning: SLACK_WEBHOOK_URL not configured, skipping Slack notification")
            return False
        
        # Generate request ID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Format amount if present in args
        amount = request_data.args.get("amount")
        amount_str = f"${amount:,.2f}" if amount is not None else "N/A"
        
        # Build Slack message with blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️ SudoMode Approval Required"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Resource:*\n`{request_data.resource}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Action:*\n`{request_data.action}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Amount:*\n{amount_str}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Request ID:*\n`{request_id}`"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reason:*\n{rule_reason}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<http://localhost:3000/requests/{request_id}|View in Dashboard>*"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Prepare payload
        payload = {
            "text": f"⚠️ SudoMode Approval Required: {request_data.action} on {request_data.resource}",
            "blocks": blocks
        }
        
        try:
            response = await self.client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

