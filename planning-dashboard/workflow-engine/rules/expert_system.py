import logging

# Configure logger for rules engine
logger = logging.getLogger(__name__)

class ExpertRulesEngine:
    """
    Logic-based system for routine decision automation.
    Evaluates replenishment requests or scenario adjustments against predefined business rules.
    """
    def __init__(self):
        # Register standard rules
        self.rules = [
            self.rule_auto_approve_low_value,
            self.rule_flag_high_risk_supplier,
            self.rule_escalate_margin_impact,
            self.rule_auto_approve_green_supplier
        ]
        
    def evaluate(self, context):
        """
        Evaluate a context object (dictionary) against all registered rules.
        Returns a decision payload with status and reasoning.
        """
        decisions = []
        for rule in self.rules:
            result = rule(context)
            if result:
                decisions.append(result)
                
        # Aggregate decisions
        # Priority: Escalate -> Flag -> Auto-Approve -> Manual Review
        decision_status = "Manual Review"
        reasons = []
        
        for d in decisions:
            reasons.append(d['reason'])
            if d['action'] == 'Escalate':
                decision_status = 'Escalate'
                # Escalate overrides all
                break
            elif d['action'] == 'Flag' and decision_status != 'Escalate':
                decision_status = 'Flag'
            elif d['action'] == 'Auto-Approve' and decision_status not in ['Escalate', 'Flag']:
                decision_status = 'Auto-Approve'

        return {
            "status": decision_status,
            "reasons": reasons,
            "rule_count_fired": len(decisions)
        }

    # --- Rule Definitions ---
    
    def rule_auto_approve_low_value(self, context):
        """
        Rule: Auto-approve requests if value is < $50,000 and supplier risk is not High or Critical.
        """
        value = context.get('request_value_usd', 0)
        risk = context.get('supplier_risk', 'Unknown')
        
        if value < 50000 and risk not in ['High Risk', 'Critical Risk']:
            return {"action": "Auto-Approve", "reason": f"Low value request (${value:,.2f}) with acceptable risk ({risk})."}
        return None

    def rule_flag_high_risk_supplier(self, context):
        """
        Rule: Flag any request involving a Critical Risk supplier.
        """
        risk = context.get('supplier_risk', 'Unknown')
        if risk == 'Critical Risk':
            return {"action": "Flag", "reason": "Supplier classified as Critical Risk by fuzzy engine."}
        return None

    def rule_escalate_margin_impact(self, context):
        """
        Rule: Escalate if margin impact is negative and value is > $100,000.
        """
        margin_impact = context.get('margin_impact_pct', 0)
        value = context.get('request_value_usd', 0)
        
        if margin_impact < 0 and value > 100000:
            return {"action": "Escalate", "reason": f"Significant negative margin impact ({margin_impact}%) on high-value request."}
        return None

    def rule_auto_approve_green_supplier(self, context):
        """
        Rule: Auto-approve medium value requests (< $250k) if Supplier has strong sustainability score (>80).
        """
        value = context.get('request_value_usd', 0)
        sustainability = context.get('supplier_sustainability_score', 0)
        
        if value < 250000 and sustainability >= 80:
            return {"action": "Auto-Approve", "reason": f"Strong sustainability profile ({sustainability}) permits auto-approval for medium-value request."}
        return None

if __name__ == '__main__':
    engine = ExpertRulesEngine()
    
    test_context_1 = {
        'request_value_usd': 20000,
        'supplier_risk': 'Moderate Stability',
        'margin_impact_pct': 5,
        'supplier_sustainability_score': 60
    }
    print("Test 1:", engine.evaluate(test_context_1))
    
    test_context_2 = {
        'request_value_usd': 150000,
        'supplier_risk': 'Critical Risk',
        'margin_impact_pct': -2,
        'supplier_sustainability_score': 50
    }
    print("Test 2:", engine.evaluate(test_context_2))
