import numpy as np

def triangular_membership(x, a, b, c):
    """
    Compute triangular membership function.
    a: left base
    b: peak
    c: right base
    """
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        if b == a:
            return 1.0
        return (x - a) / (b - a)
    elif b < x < c:
        if c == b:
            return 1.0
        return (c - x) / (c - b)
    return 0.0

def evaluate_supplier_risk(financial_score, operational_score, geopolitical_score):
    """
    Evaluates supplier risk based on linguistic variables and fuzzy rules.
    Scores are expected to be between 0 and 100, where 100 is best.
    
    Linguistic Output:
    - "Critical Risk"
    - "High Risk"
    - "Moderate Stability"
    - "High Stability"
    
    Returns a dictionary with the crisp score (0-100 where 100 is max risk) and the linguistic classification.
    """
    # 1. Fuzzification (Input Variables: 0 to 100)
    # Financial Stability
    fin_poor = triangular_membership(financial_score, -1, 0, 40)
    fin_fair = triangular_membership(financial_score, 20, 50, 80)
    fin_good = triangular_membership(financial_score, 60, 100, 101)
    
    # Operational Reliability
    ops_poor = triangular_membership(operational_score, -1, 0, 40)
    ops_fair = triangular_membership(operational_score, 20, 50, 80)
    ops_good = triangular_membership(operational_score, 60, 100, 101)
    
    # Geopolitical Safety
    geo_poor = triangular_membership(geopolitical_score, -1, 0, 40)
    geo_fair = triangular_membership(geopolitical_score, 20, 50, 80)
    geo_good = triangular_membership(geopolitical_score, 60, 100, 101)
    
    # 2. Rule Evaluation (Mamdani Inference - using min/max)
    # Rule 1: IF Financial is Poor OR Operational is Poor OR Geopolitical is Poor THEN Risk is Critical
    rule_critical = max(fin_poor, ops_poor, geo_poor)
    
    # Rule 2: IF Financial is Fair AND Operational is Fair THEN Risk is High
    rule_high = min(fin_fair, ops_fair)
    # Geopolitical fair also contributes to high risk
    rule_high = max(rule_high, min(geo_fair, fin_fair))
    
    # Rule 3: IF Financial is Good AND Operational is Fair AND Geopolitical is Good THEN Risk is Moderate
    rule_moderate = min(fin_good, ops_fair, geo_good)
    # Alternative: Good operations but fair financial
    rule_moderate = max(rule_moderate, min(ops_good, fin_fair, geo_good))
    
    # Rule 4: IF Financial is Good AND Operational is Good AND Geopolitical is Good THEN Risk is Low
    rule_low = min(fin_good, ops_good, geo_good)
    
    # 3. Defuzzification (Centroid method for risk score 0-100 where 100 = max risk)
    # Output Risk Sets (0-100 scale where 100 is worst)
    # Critical Risk center = 90
    # High Risk center = 70
    # Moderate Stability center = 40
    # High Stability center = 10
    
    numerator = (rule_critical * 90) + (rule_high * 70) + (rule_moderate * 40) + (rule_low * 10)
    denominator = rule_critical + rule_high + rule_moderate + rule_low
    
    if denominator == 0:
        crisp_risk = 50.0  # Default to moderate if no rules fire
    else:
        crisp_risk = numerator / denominator
        
    # Determine the winning linguistic category
    memberships = {
        "Critical Risk": rule_critical,
        "High Risk": rule_high,
        "Moderate Stability": rule_moderate,
        "High Stability": rule_low
    }
    
    classification = max(memberships, key=memberships.get)
    if memberships[classification] == 0:
        if crisp_risk >= 80: classification = "Critical Risk"
        elif crisp_risk >= 60: classification = "High Risk"
        elif crisp_risk >= 30: classification = "Moderate Stability"
        else: classification = "High Stability"
        
    return {
        "crisp_risk_score": crisp_risk,
        "linguistic_classification": classification,
        "memberships": memberships
    }

if __name__ == '__main__':
    # Test cases
    print(evaluate_supplier_risk(80, 90, 85))  # Should be Highly Stable
    print(evaluate_supplier_risk(30, 80, 85))  # Should be Critical Risk due to fin_poor
    print(evaluate_supplier_risk(50, 50, 50))  # Should be High Risk
