import uuid
import datetime
from agents.security_agent import verify_security
from agents.intake_agent import process_intake
from agents.revenue_risk_agent import assess_risk
from agents.policy_agent import evaluate_policy
from agents.knowledge_graph_agent import generate_graph
from agents.evaluation_agent import evaluate_analysis
from agents.executive_brief_agent import create_brief
from tools.audit_log import log_audit_event

def _create_trace(agent_name: str, status: str, summary: str) -> dict:
    return {
        "agent": agent_name,
        "status": status,
        "summary": summary,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

def analyze_deal(deal_data: dict) -> dict:
    """Orchestrator: Coordinates the full multi-agent workflow."""
    deal_id = deal_data.get("deal_id", str(uuid.uuid4()))
    agent_trace = []
    audit_log = []
    
    def log_and_audit(msg: str):
        audit_log.append(f"[{deal_id}] {msg}")
        log_audit_event(deal_id, "ORCHESTRATOR", msg)

    log_and_audit("Analysis started.")
    
    # 1. Intake Agent
    structured_data, intake_summary = process_intake(deal_data)
    agent_trace.append(_create_trace("IntakeAgent", "Success", intake_summary))

    # 3. Revenue Risk Agent
    risk_assessment = assess_risk(structured_data)
    agent_trace.append(_create_trace("RevenueRiskAgent", "Success", f"Risk Level: {risk_assessment['risk_level']}. {len(risk_assessment['risk_drivers'])} drivers found."))

    # 4. Policy Agent
    policy_results = evaluate_policy(structured_data, risk_assessment["risk_score"])
    violations = policy_results["policy_violations"]
    approvals = policy_results["approval_path"]
        
    agent_trace.append(_create_trace("PolicyAgent", "Success", policy_results["approval_recommendation"]))

    # Derive recommendation earlier so Graph Agent can include it
    risk_score = risk_assessment["risk_score"]
    if risk_score >= 75:
        recommendation = "Escalate"
    elif risk_score >= 50:
        recommendation = "Revise"
    else:
        recommendation = "Approve with conditions"

    # 5. Knowledge Graph Agent
    graph = generate_graph(structured_data, risk_assessment, policy_results, recommendation)
    agent_trace.append(_create_trace("KnowledgeGraphAgent", "Success", "Knowledge graph generated."))

    # 6. Executive Brief Agent
    brief = create_brief(structured_data, risk_assessment, policy_results, recommendation)
    agent_trace.append(_create_trace("ExecutiveBriefAgent", "Success", "Brief generated."))

    # 7. Security Agent (Guardrail)
    security_results = verify_security(deal_data, risk_score, approvals, recommendation)
    if security_results["blocked"]:
        log_and_audit(f"Analysis blocked due to security failure: {security_results['detected_issues']}")
        formatted_trace = [f"{t['agent']} [{t['status']}]: {t['summary']}" for t in agent_trace]
        formatted_trace.append(f"SecurityAgent [Failed]: {security_results['safety_recommendation']}")
        return {
            "deal_id": deal_id,
            "risk_score": 100.0,
            "recommendation": "Block analysis",
            "approval_path": ["Security Review"],
            "executive_brief": f"Deal blocked due to security/compliance violations. Issues: {', '.join(security_results['detected_issues'])}",
            "graph": {},
            "evaluation": "N/A",
            "security_checks": "Failed",
            "agent_trace": formatted_trace,
            "audit_log": audit_log
        }
    else:
        agent_trace.append(_create_trace("SecurityAgent", "Success", "Security check passed."))

    # 8. Evaluation Agent
    evaluation = evaluate_analysis(risk_score, recommendation, graph, approvals, brief, risk_assessment["risk_drivers"])
    agent_trace.append(_create_trace("EvaluationAgent", "Success", f"Score: {evaluation['overall_quality_score']:.1f}"))
        
    log_and_audit("Analysis completed.")

    return {
        "deal_id": deal_id,
        "risk_score": float(risk_score),
        "recommendation": recommendation,
        "approval_path": approvals,
        "executive_brief": brief,
        "graph": graph,
        "evaluation": str(evaluation),
        "security_checks": "Passed",
        "asc606": risk_assessment.get("asc_606_compliant", True),
        "agent_trace": [f"{t['agent']} [{t['status']}]: {t['summary']}" for t in agent_trace],
        "audit_log": audit_log
    }
