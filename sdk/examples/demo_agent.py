"""
SudoMode Demo: Rogue AI Agent
==============================

This script demonstrates how SudoMode protects your system by intercepting
and evaluating AI agent actions before they execute.

The demo simulates a "Rogue AI Agent" attempting various operations:
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
- ✅ Read operations will be allowed immediately
- ⛔ Delete operations will be blocked with PermissionError
- ⏳ High-value charges will pause and wait for approval
- ✅ Low-value charges will be allowed automatically

After running, check the dashboard at http://localhost:5173 to see
pending approval requests.
"""

import sys
from pathlib import Path

# Add parent directory to path to import sudomode SDK
# This allows us to import the SDK without installing it as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudomode import SudoClient


def main():
    """
    Main demo function that simulates various AI agent operations.
    
    Each scenario demonstrates a different governance outcome:
    - ALLOW: Action proceeds immediately
    - DENY: Action is blocked with an exception
    - REQUIRE_APPROVAL: Action pauses until human approves/rejects
    """
    print("🤖 Rogue AI Agent Starting...")
    print("=" * 60)
    print("This agent will attempt various operations to demonstrate")
    print("SudoMode's governance capabilities.\n")
    
    # Initialize SudoMode client
    # The client connects to the SudoMode server to check permissions
    client = SudoClient(base_url="http://localhost:8000")
    
    try:
        # ============================================================
        # SCENARIO 1: Read Database (Should be ALLOWED)
        # ============================================================
        print("\n📖 Scenario 1: Agent tries to READ database...")
        print("-" * 60)
        try:
            # The execute() method checks permission before proceeding
            # For read operations, the policy allows it immediately
            result = client.execute("database", "read", {})
            
            if result:
                print("✅ Success: Database read operation allowed")
                print("   → The agent can now safely read from the database")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("   → This shouldn't happen for read operations")
        
        # ============================================================
        # SCENARIO 2: Delete Database (Should be DENIED)
        # ============================================================
        print("\n🗑️  Scenario 2: Agent tries to DELETE database...")
        print("-" * 60)
        try:
            # Attempting to delete the database
            # The policy engine will evaluate this and return DENY
            client.execute("database", "delete", {})
            
            # If we reach here, something went wrong - delete should be blocked!
            print("❌ ERROR: Delete was allowed (this should not happen!)")
            print("   → SudoMode failed to protect the system!")
            
        except PermissionError as e:
            # This is the expected behavior - delete operations are blocked
            print(f"⛔ Blocked by SudoMode: {e}")
            print("   → The system is protected! Delete operation prevented.")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        # ============================================================
        # SCENARIO 3: High-Value Charge (Should REQUIRE APPROVAL)
        # ============================================================
        print("\n💰 Scenario 3: Agent tries to CHARGE $5000...")
        print("-" * 60)
        print("   → This is a high-value transaction requiring human review")
        print("   → The request will be sent to the dashboard for approval")
        print("   → The agent will pause and wait for a decision...\n")
        
        try:
            # Attempting a high-value charge ($5000)
            # According to the policy, charges over $50 require approval
            # The execute() method will:
            # 1. Send the request to SudoMode
            # 2. Receive REQUIRE_APPROVAL status
            # 3. Poll the server every 2 seconds waiting for approval/rejection
            # 4. Return True if approved, raise PermissionError if rejected
            
            result = client.execute(
                "stripe.charge", 
                "charge", 
                {"amount": 5000}
            )
            
            # If we reach here, the charge was approved!
            print("✅ Transfer completed after approval")
            print("   → A human reviewed and approved this transaction")
            
        except PermissionError as e:
            # The charge was rejected by a human reviewer
            print(f"⛔ Blocked by SudoMode: {e}")
            print("   → A human reviewer rejected this transaction")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("   → Check that the server is running and accessible")
        
        # ============================================================
        # BONUS SCENARIO: Low-Value Charge (Should be ALLOWED)
        # ============================================================
        print("\n💵 Bonus Scenario: Agent tries to CHARGE $30...")
        print("-" * 60)
        print("   → This is a low-value transaction (under $50)")
        print("   → According to policy, it should be auto-approved\n")
        
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
    print("\n" + "=" * 60)
    print("🏁 Demo Complete!")
    print("=" * 60)
    print("\nSudoMode successfully protected the system by:")
    print("  ✅ Allowing safe operations (read)")
    print("  ⛔ Blocking dangerous operations (delete)")
    print("  ⏳ Requiring approval for high-risk operations (large payments)")
    print("\nNext Steps:")
    print("  • Check the dashboard at http://localhost:5173")
    print("  • Review pending approval requests")
    print("  • Approve or reject requests as needed")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run the demo when script is executed directly
    main()
