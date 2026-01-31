"""
SudoMode Demo: AI Agent Governance
==================================

This script demonstrates how SudoMode protects your system by intercepting
and evaluating AI agent actions before they execute.

The demo simulates an AI Agent attempting various operations:
1. Safe operations (read) - Automatically allowed
2. Dangerous operations (delete) - Automatically blocked
3. High-risk operations (large payments) - Requires human approval

Prerequisites:
--------------
1. SudoMode server must be running on http://localhost:8000
   Start it with: cd server && uvicorn app.main:app --reload

2. Install SDK dependencies:
   pip install -r requirements.txt

Usage:
------
    python examples/demo_agent.py

What to Expect:
---------------
- Read operations will be allowed immediately
- Delete operations will be blocked with PermissionError
- High-value charges will pause and wait for approval
- Low-value charges will be allowed automatically

After running, check the dashboard at http://localhost:5173 to see
pending approval requests.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path to import sudomode SDK
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudomode import SudoClient, configure_logging

# Configure logging
configure_logging(level=logging.INFO)
logger = logging.getLogger("sudomode.demo")


def main():
    """
    Main demo function that simulates various AI agent operations.
    
    Each scenario demonstrates a different governance outcome:
    - ALLOW: Action proceeds immediately
    - DENY: Action is blocked with an exception
    - REQUIRE_APPROVAL: Action pauses until human approves/rejects
    """
    logger.info("=" * 60)
    logger.info("SudoMode Demo: AI Agent Governance")
    logger.info("=" * 60)
    logger.info("This demo demonstrates SudoMode's governance capabilities")
    
    # Initialize SudoMode client
    # The client connects to the SudoMode server to check permissions
    client = SudoClient(base_url="http://localhost:8000")
    
    try:
        logger.info("\nSCENARIO 1: Read Database (Should be ALLOWED)")
        logger.info("-" * 60)
        try:
            logger.info("Attempting to read database...")
            result = client.execute("database", "read", {})
            
            if result:
                logger.info("SUCCESS: Database read operation allowed")
                logger.info("The agent can now safely read from the database")
        except Exception as e:
            logger.error(f"Unexpected error during read operation: {e}")
        
        logger.info("\nSCENARIO 2: Delete Database (Should be DENIED)")
        logger.info("-" * 60)
        try:
            logger.info("Attempting to delete database...")
            client.execute("database", "delete", {})
            
            # If we reach here, something went wrong - delete should be blocked!
            logger.error("SECURITY VIOLATION: Delete operation was allowed")
            logger.error("SudoMode failed to protect the system!")
            
        except PermissionError as e:
            # This is the expected behavior - delete operations are blocked
            logger.warning(f"SECURITY: {e}")
            logger.info("The system is protected! Delete operation prevented.")
            
        except Exception as e:
            logger.error(f"Unexpected error during delete operation: {e}")
        
        logger.info("\nSCENARIO 3: High-Value Charge (Requires Approval)")
        logger.info("-" * 60)
        logger.info("This is a high-value transaction requiring human review")
        logger.info("The request will be sent to the dashboard for approval")
        logger.info("The agent will pause and wait for a decision...")
        
        try:
            logger.info("Initiating high-value charge of $5000...")
            result = client.execute("stripe.charge", "charge", {"amount": 5000})
            
            # If we reach here, the charge was approved!
            logger.info("TRANSFER COMPLETED: Human approval received")
            logger.info("A human reviewer approved this transaction")
            
        except PermissionError as e:
            # The charge was rejected by a human reviewer
            logger.warning(f"TRANSFER REJECTED: {e}")
            logger.info("A human reviewer rejected this transaction")
            
        except Exception as e:
            logger.error(f"Error during transaction: {e}")
            logger.error("Please check that the SudoMode server is running")
        
        logger.info("\nBONUS SCENARIO: Low-Value Charge (Auto-Approved)")
        logger.info("-" * 60)
        logger.info("This is a low-value transaction (under $50)")
        logger.info("According to policy, it should be auto-approved")
        
        try:
            # Low-value charge - should be automatically allowed
            result = client.execute("stripe.charge", "charge", {"amount": 30})
            
            if result:
                print("✅ Success: Low-value charge automatically approved")
                print("   → No human approval needed for small amounts")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    finally:
        # Always close the client to clean up HTTP connections
        client.close()
    
    # ============================================================
    # Summary
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("DEMO COMPLETE - SudoMode governance checks completed")
    logger.info("SudoMode successfully protected the system by:")
    logger.info("  Allowing safe operations (read)")
    logger.info("  Blocking dangerous operations (delete)")
    logger.info("  Requiring approval for high-risk operations (large payments)")
    logger.info("Next Steps:")
    logger.info("  Check the dashboard at http://localhost:5173")
    logger.info("  Review pending approval requests")
    logger.info("  Approve or reject requests as needed")
    logger.info("\n" + "=" * 60)
    print("  • Approve or reject requests as needed")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run the demo when script is executed directly
    main()
