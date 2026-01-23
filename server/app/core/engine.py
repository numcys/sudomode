"""Policy Engine - Core logic for evaluating governance rules"""
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from simpleeval import SimpleEval
from app.core.config import settings
from app.api.models import GovernanceRequest, GovernanceResponse

class PolicyEngine:
    """Evaluates governance requests against policy rules"""
    
    def __init__(self, policies_file: Optional[str] = None):
        """
        Initialize the policy engine
        
        Args:
            policies_file: Optional path to policies YAML file. 
                          If not provided, uses settings.POLICIES_FILE
        """
        if policies_file:
            self.policies_file = Path(policies_file)
        else:
            self.policies_file = settings.get_policies_path()
        self.policies = self._load_policies()
        self.evaluator = SimpleEval()
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from YAML file"""
        try:
            with open(self.policies_file, 'r') as f:
                policies = yaml.safe_load(f) or {}
                return policies
        except FileNotFoundError:
            return {"rules": []}
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing policies file: {e}")
    
    def _matches_resource(self, rule_resource: str, request_resource: str) -> bool:
        """Check if request resource matches rule resource pattern"""
        if rule_resource == "*":
            return True
        return rule_resource == request_resource
    
    def _matches_action(self, rule_action: str, request_action: str) -> bool:
        """Check if request action matches rule action pattern"""
        if rule_action == "*":
            return True
        return rule_action == request_action
    
    def _evaluate_condition(
        self, 
        condition: Optional[str], 
        request: GovernanceRequest
    ) -> bool:
        """
        Safely evaluate a condition expression using simpleeval
        
        Args:
            condition: Condition string (e.g., "args.amount > 50")
            request: The governance request containing args
        
        Returns:
            True if condition evaluates to true, False otherwise
        """
        if not condition:
            return True  # No condition means always match
        
        try:
            # Prepare evaluation context
            # Make request.args accessible as 'args' in the expression
            self.evaluator.names = {
                "args": request.args,
                "resource": request.resource,
                "action": request.action,
            }
            
            # Evaluate the condition
            result = self.evaluator.eval(condition)
            return bool(result)
        except Exception as e:
            # If evaluation fails, log and return False (fail closed)
            print(f"Warning: Condition evaluation failed: {e}")
            return False
    
    def evaluate(self, request: GovernanceRequest) -> GovernanceResponse:
        """
        Evaluate a governance request against policy rules.
        
        This is the core method of the policy engine. It:
        1. Iterates through all rules in order
        2. Checks if the rule matches the request (resource, action, condition)
        3. Returns the first matching rule's decision
        4. Returns DENY by default if no rules match
        
        Rules are evaluated in order - FIRST MATCHING RULE WINS.
        This means you should put more specific rules before general ones.
        
        Example:
            Rule 1: resource="database", action="delete" -> DENY
            Rule 2: resource="*", action="*" -> ALLOW
            
            A request for database.delete will match Rule 1 and be DENIED,
            even though Rule 2 would also match.
        
        Args:
            request: The governance request to evaluate
                - resource: The resource being accessed (e.g., "database")
                - action: The action being performed (e.g., "read", "delete")
                - args: Dictionary of arguments (e.g., {"amount": 100})
        
        Returns:
            GovernanceResponse with:
                - status: "ALLOW", "DENY", or "REQUIRE_APPROVAL"
                - reason: Human-readable explanation of the decision
        """
        rules = self.policies.get("rules", [])
        
        for rule in rules:
            # Check if resource matches
            rule_resource = rule.get("resource", "*")
            if not self._matches_resource(rule_resource, request.resource):
                continue
            
            # Check if action matches
            rule_action = rule.get("action", "*")
            if not self._matches_action(rule_action, request.action):
                continue
            
            # Check condition if present
            condition = rule.get("condition")
            if condition and not self._evaluate_condition(condition, request):
                continue
            
            # Rule matches! Return the decision
            decision = rule.get("decision", "DENY")
            reason = rule.get("reason", f"Matched rule: {rule.get('name', 'unknown')}")
            
            return GovernanceResponse(
                status=decision,
                reason=reason
            )
        
        # No rule matched - default deny
        return GovernanceResponse(
            status="DENY",
            reason="No matching policy found - default deny"
        )

