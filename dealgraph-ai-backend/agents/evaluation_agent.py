def evaluate_analysis(
    risk_score: float, 
    recommendation: str, 
    graph: dict, 
    approvals: list, 
    brief: str, 
    risk_drivers: list
) -> dict:
    """Evaluation Agent: Evaluates the quality, trustworthiness, and completeness of the final output."""
    
    evaluation = {
        "completeness": "Pass",
        "groundedness": "Pass",
        "consistency": "Pass",
        "safety": "Pass",
        "explainability": "Pass",
        "hhh_helpful": "Pass",
        "hhh_honest": "Pass",
        "hhh_harmless": "Pass",
        "overall_quality_score": 100.0
    }
    
    score = 100.0
    
    # 1. Completeness
    if risk_score is None or not recommendation or not graph or not brief:
        evaluation["completeness"] = "Fail"
        score -= 20.0
        
    # 2. Consistency
    is_consistent = True
    if risk_score >= 75 and recommendation != "Escalate": 
        is_consistent = False
    elif 50 <= risk_score < 75 and recommendation != "Revise": 
        is_consistent = False
    elif risk_score < 50 and recommendation != "Approve with conditions": 
        is_consistent = False
        
    if not is_consistent:
        evaluation["consistency"] = "Fail"
        score -= 20.0
        
    # 3. Safety
    if risk_score > 70 and (not approvals or len(approvals) == 0):
        evaluation["safety"] = "Fail"
        score -= 20.0
        
    # 4. Explainability
    if not risk_drivers or len(risk_drivers) == 0:
        if risk_score > 0:
            evaluation["explainability"] = "Fail"
            score -= 10.0
            
    # 5. Groundedness
    # Mocking check for hallucination based on missing drivers vs high score
    if risk_score > 50 and len(risk_drivers) == 0:
        evaluation["groundedness"] = "Fail"
        score -= 10.0
        
    # 6. HHH Framework Check
    # Helpful: Provides clear recommendation and next steps
    if not recommendation:
        evaluation["hhh_helpful"] = "Fail"
        score -= 5.0
    # Honest: Driven strictly by data facts (consistency proxy)
    if evaluation["consistency"] == "Fail":
        evaluation["hhh_honest"] = "Fail"
        score -= 5.0
    # Harmless: Safe operational bounds
    if evaluation["safety"] == "Fail":
        evaluation["hhh_harmless"] = "Fail"
        score -= 10.0
        
    evaluation["overall_quality_score"] = max(0.0, score)
    
    return evaluation
