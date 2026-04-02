import sys
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage
from unittest.mock import MagicMock

# Ensure the project root is on sys.path before importing project modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.conditional_agent import create_alert_router_agent
from src.tools.mlops_tools import check_alert_severity

def test_alert_severity_detection():
    """Test that severity detection works correctly."""
    assert check_alert_severity("Database is DOWN") == "critical"
    assert check_alert_severity("URGENT: critical issue") == "urgent"
    assert check_alert_severity("CPU warning at 85%") == "medium"
    assert check_alert_severity("Disk space notification") == "low"

def test_alert_router_critical_path():
    """Test the critical alert path."""
    mock_llm = MagicMock(name="ChatGroqMock")
    graph = create_alert_router_agent(llm_client=mock_llm, tools_for_graph=[])

    result = graph.invoke({
        "messages": [HumanMessage(content="Production database DOWN")],
        "alert_info": "Production database DOWN",
        "alert_severity": "unknown",
        "investigation_query": "",
        "investigation_step": 0,
        "max_investigation_steps": 3,
        "logs_found": False,
        "proposed_action": "",
        "human_approval_needed": False,
        "human_feedback": "",
        "system_metrics": {},
        "report_content": "",
        "final_result": ""
    })

    assert "CRITICAL" in result["final_result"]
    assert "escalation" in result["final_result"].lower()

def test_alert_router_medium_path():
    """Test the medium alert path."""
    mock_llm = MagicMock(name="ChatGroqMock")
    graph = create_alert_router_agent(llm_client=mock_llm, tools_for_graph=[])

    result = graph.invoke({
        "messages": [HumanMessage(content="CPU usage warning")],
        "alert_info": "CPU usage warning",
        "alert_severity": "unknown",
        "investigation_query": "",
        "investigation_step": 0,
        "max_investigation_steps": 3,
        "logs_found": False,
        "proposed_action": "",
        "human_approval_needed": False,
        "human_feedback": "",
        "system_metrics": {},
        "report_content": "",
        "final_result": ""
    })

    assert "MEDIUM" in result["final_result"]
    assert "diagnosis" in result["final_result"].lower()

def test_alert_router_urgent_path():
    """Test the urgent alert path."""
    mock_llm = MagicMock(name="ChatGroqMock")
    graph = create_alert_router_agent(llm_client=mock_llm, tools_for_graph=[])

    result = graph.invoke({
        "messages": [HumanMessage(content="URGENT: high memory usage")],
        "alert_info": "URGENT: high memory usage",
        "alert_severity": "unknown",
        "investigation_query": "",
        "investigation_step": 0,
        "max_investigation_steps": 3,
        "logs_found": False,
        "proposed_action": "",
        "human_approval_needed": False,
        "human_feedback": "",
        "system_metrics": {},
        "report_content": "",
        "final_result": ""
    })

    assert "URGENT" in result["final_result"]
    assert "priority" in result["final_result"].lower()
