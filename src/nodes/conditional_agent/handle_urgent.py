import logging
from src.state import AgentState

logger = logging.getLogger(__name__)

def handle_urgent_alert_node(state: AgentState):
    """
    Handle urgent alerts: simulated as a priority notification to the dev team.
    """
    alert = state.get("alert_info", "Unknown alert")
    logger.info(f"Node 'handle_urgent_alert': URGENT alert ({alert}). Priority notification sent.")
    
    return {
        "final_result": f"URGENT alert detected ({alert}). Priority notification sent to the dev team."
    }
