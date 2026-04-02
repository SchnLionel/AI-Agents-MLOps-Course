import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path to import the tool
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/tool_services/loki_tool")))

from tool import LokiLogSearchTool

def test_search_logs_success():
    """Test successful log search."""
    tool = LokiLogSearchTool("http://mock-loki:3100")
    
    mock_data = {
        "status": "success",
        "data": {
            "result": [
                {
                    "stream": {"job": "docker", "service": "news-api"},
                    "values": [
                        ["1600000000000000000", "ERROR: Connection failed"],
                        ["1600000030000000000", "ERROR: Retry exhausted"]
                    ]
                }
            ]
        }
    }
    
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        result = tool.search("ERROR", 5, 10, target_service="news-api")
        
        assert "ERROR: Connection failed" in result
        assert "ERROR: Retry exhausted" in result
        mock_get.assert_called_once()

def test_search_logs_no_results():
    """Test log search with no matching entries."""
    tool = LokiLogSearchTool("http://mock-loki:3100")
    
    mock_data = {"status": "success", "data": {"result": []}}
    
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        result = tool.search("NONEXISTENT", 5, 10)
        
        assert "No logs found" in result

def test_search_logs_invalid_time_range():
    """Test log search with invalid parameters."""
    tool = LokiLogSearchTool("http://mock-loki:3100")
    
    result = tool.search("ERROR", 0, 10)
    assert "Error" in result
    assert "time_range_minutes" in result

def test_search_logs_timeout():
    """Test handling of Loki timeout."""
    tool = LokiLogSearchTool("http://mock-loki:3100")
    
    with patch("requests.get", side_effect=Exception("Connection timeout")):
        result = tool.search("ERROR", 5, 10)
        assert "Error" in result
        assert "Connection timeout" in result
