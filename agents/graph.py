import logging

from langgraph.graph import StateGraph, START, END

from core.state import AgentState
from agents.ocr_node import ocr_node
from agents.claim_extractor_node import claim_extractor_node
from agents.fact_checker_node import fact_checker_node
from agents.verdict_node import verdict_node
from agents.router import route_after_claims

logger = logging.getLogger(__name__)


def build_graph() -> object:
    """Construct and compile the LangGraph StateGraph for the misinformation pipeline."""
    graph = StateGraph(AgentState)

    graph.add_node("ocr_node", ocr_node)
    graph.add_node("claim_extractor_node", claim_extractor_node)
    graph.add_node("fact_checker_node", fact_checker_node)
    graph.add_node("verdict_node", verdict_node)

    graph.add_edge(START, "ocr_node")
    graph.add_edge("ocr_node", "claim_extractor_node")
    graph.add_conditional_edges("claim_extractor_node", route_after_claims)
    graph.add_edge("fact_checker_node", "verdict_node")
    graph.add_edge("verdict_node", END)

    logger.info("LangGraph state graph compiled successfully")
    return graph.compile()


compiled_graph = build_graph()
