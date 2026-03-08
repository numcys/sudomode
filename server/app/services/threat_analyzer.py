"""
SudoMode Threat Analyzer — "Service as Software" Bedrock Integration
=====================================================================
When SudoMode blocks a rogue agent action, this service automatically
runs an AI-powered anomaly/risk analysis using AWS Bedrock (Claude).

This is the "Service as Software" feature: automated SOC analysis
triggered on every BLOCK event.
"""

import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def analyze_threat(attempted_payload: dict) -> str:
    """
    Use AWS Bedrock (Claude) to generate a 1-sentence risk summary
    when a policy violation is detected.

    Args:
        attempted_payload: Dict with details of the blocked call, e.g.:
            {
                "tool": "issue_refund",
                "amount": 500,
                "limit": 50,
                "order_id": "ORD-123"
            }

    Returns:
        A 1-sentence risk summary string from the AI analyst,
        or a fallback message if Bedrock is unavailable.
    """
    tool = attempted_payload.get("tool", "unknown")
    amount = attempted_payload.get("amount", "unknown")
    limit = attempted_payload.get("limit", 50)

    prompt = (
        "You are a SudoMode SOC Analyst. "
        f"The AI agent just tried to refund ${amount} but the limit is ${limit}. "
        "Write a 1-sentence risk summary for the retail manager."
    )

    try:
        # Initialize Bedrock runtime client
        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
        )

        # Build the request body for Amazon Nova Pro on Bedrock
        request_body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            "inferenceConfig": {
                "maxTokens": 300,  # STRICT: protect AWS credits
                "temperature": 0.1,
            },
        })

        # Invoke the model
        response = bedrock.invoke_model(
            modelId="us.amazon.nova-pro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=request_body,
        )

        # Parse the response (Nova format)
        response_body = json.loads(response["body"].read())
        analysis = response_body["output"]["message"]["content"][0]["text"].strip()

        print(f"\n{'='*60}")
        print(f"🔍  SUDOMODE THREAT ANALYSIS (Bedrock)")
        print(f"{'='*60}")
        print(f"  {analysis}")
        print(f"{'='*60}\n")

        return analysis

    except NoCredentialsError:
        fallback = (
            f"[THREAT] Agent attempted ${amount} refund (limit: ${limit}). "
            "No AWS credentials configured — Bedrock analysis unavailable."
        )
        print(f"\n⚠️  {fallback}\n")
        return fallback

    except ClientError as e:
        fallback = (
            f"[THREAT] Agent attempted ${amount} refund (limit: ${limit}). "
            f"Bedrock error: {e.response['Error']['Message']}"
        )
        print(f"\n⚠️  {fallback}\n")
        return fallback

    except Exception as e:
        fallback = (
            f"[THREAT] Agent attempted ${amount} refund (limit: ${limit}). "
            f"Analysis unavailable: {str(e)}"
        )
        print(f"\n⚠️  {fallback}\n")
        return fallback
