from graph.graph_builder import build_deal_graph

def generate_graph(deal_data: dict, risk_assessment: dict, policy_results: dict, recommendation: str) -> dict:
    """Knowledge Graph Agent: Formats the collected context into a structured graph for frontend visualization."""
    return build_deal_graph(deal_data, risk_assessment, policy_results, recommendation)
