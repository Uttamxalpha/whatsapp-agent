import logging

from core.state import AgentState

logger = logging.getLogger(__name__)


def route_after_claims(state: AgentState) -> str:
    """Route to fact_checker_node or skip to verdict_node based on state."""
    if state.get("error") is not None:
        logger.info("Routing to verdict_node due to error in state")
        return "verdict_node"
    if state.get("verdict") == "UNVERIFIABLE":
        logger.info("Routing to verdict_node: no verifiable claims found")
        return "verdict_node"
    logger.info("Routing to fact_checker_node")
    return "fact_checker_node"
