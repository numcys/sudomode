"""
SudoMode Example: Bank Agent
==============================

A more realistic example showing how to integrate SudoMode into a
production AI agent that handles financial transactions.

This example demonstrates:
- Checking permissions before executing sensitive operations
- Handling different governance outcomes
- Proper error handling and logging
- Integration with actual business logic

Use Case:
---------
A banking AI agent that needs to:
- Read account balances (allowed)
- Transfer money between accounts (requires approval for large amounts)
- Process refunds (requires approval)
- View transaction history (allowed)
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sudomode import SudoClient


class BankAgent:
    """
    A banking AI agent that uses SudoMode for governance.
    
    This agent handles financial operations but always checks
    with SudoMode before executing sensitive actions.
    """
    
    def __init__(self, sudomode_url: str = "http://localhost:8000"):
        """
        Initialize the bank agent with SudoMode client.
        
        Args:
            sudomode_url: URL of the SudoMode server
        """
        self.client = SudoClient(base_url=sudomode_url)
        print("🏦 Bank Agent initialized with SudoMode governance")
    
    def get_account_balance(self, account_id: str) -> Optional[float]:
        """
        Get the balance of an account.
        
        This is a read operation, so it should be allowed automatically.
        
        Args:
            account_id: The account identifier
            
        Returns:
            Account balance or None if access denied
        """
        print(f"\n📊 Checking balance for account: {account_id}")
        
        try:
            # Check permission to read account data
            # Read operations are typically allowed by default
            result = self.client.execute(
                resource="account",
                action="read",
                args={"account_id": account_id}
            )
            
            if result:
                # Permission granted - proceed with actual balance retrieval
                # In a real implementation, you would query your database here
                balance = 1000.0  # Mock balance
                print(f"✅ Balance retrieved: ${balance:,.2f}")
                return balance
                
        except PermissionError as e:
            print(f"⛔ Access denied: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def transfer_money(
        self, 
        from_account: str, 
        to_account: str, 
        amount: float
    ) -> bool:
        """
        Transfer money between accounts.
        
        Large transfers require human approval via SudoMode.
        
        Args:
            from_account: Source account ID
            to_account: Destination account ID
            amount: Amount to transfer
            
        Returns:
            True if transfer succeeded, False otherwise
        """
        print(f"\n💸 Transferring ${amount:,.2f} from {from_account} to {to_account}")
        
        try:
            # Check permission with SudoMode
            # The policy engine will determine if this requires approval
            result = self.client.execute(
                resource="account",
                action="transfer",
                args={
                    "from_account": from_account,
                    "to_account": to_account,
                    "amount": amount
                }
            )
            
            if result:
                # Permission granted (either auto-approved or human-approved)
                # In a real implementation, you would execute the transfer here
                print(f"✅ Transfer completed: ${amount:,.2f}")
                print(f"   From: {from_account}")
                print(f"   To: {to_account}")
                return True
                
        except PermissionError as e:
            # Transfer was denied
            print(f"⛔ Transfer blocked: {e}")
            print("   → The transfer was not executed")
            return False
            
        except Exception as e:
            print(f"❌ Error during transfer: {e}")
            return False
    
    def process_refund(self, transaction_id: str, amount: float) -> bool:
        """
        Process a refund for a transaction.
        
        Refunds typically require approval as they involve money movement.
        
        Args:
            transaction_id: The original transaction ID
            amount: Amount to refund
            
        Returns:
            True if refund processed, False otherwise
        """
        print(f"\n↩️  Processing refund: ${amount:,.2f} for transaction {transaction_id}")
        
        try:
            # Check permission for refund operation
            result = self.client.execute(
                resource="payment",
                action="refund",
                args={
                    "transaction_id": transaction_id,
                    "amount": amount
                }
            )
            
            if result:
                # Refund approved - execute it
                print(f"✅ Refund processed: ${amount:,.2f}")
                return True
                
        except PermissionError as e:
            print(f"⛔ Refund blocked: {e}")
            return False
        except Exception as e:
            print(f"❌ Error processing refund: {e}")
            return False
    
    def close(self):
        """Clean up resources"""
        self.client.close()


def main():
    """Example usage of the Bank Agent"""
    print("=" * 60)
    print("Bank Agent Example with SudoMode Governance")
    print("=" * 60)
    
    # Initialize the agent
    agent = BankAgent()
    
    try:
        # Example 1: Read account balance (should be allowed)
        agent.get_account_balance("ACC-12345")
        
        # Example 2: Small transfer (might be auto-approved)
        agent.transfer_money("ACC-12345", "ACC-67890", 25.0)
        
        # Example 3: Large transfer (will require approval)
        agent.transfer_money("ACC-12345", "ACC-67890", 5000.0)
        
        # Example 4: Process refund (will require approval)
        agent.process_refund("TXN-ABC123", 100.0)
        
    finally:
        agent.close()
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

