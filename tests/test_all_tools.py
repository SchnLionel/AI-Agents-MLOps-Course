import os
import sys
import time
# Add src/aiops_agent_monitor to path
sys.path.insert(0, os.path.abspath('src/aiops_agent_monitor'))

from tools.mlops_tools import PrometheusQuery, LokiLogSearch, GrafanaDashboardLink

# Setup URLs for local testing
os.environ["PROMETHEUS_URL"] = os.getenv("PROMETHEUS_URL", "http://localhost:9091")
os.environ["LOKI_URL"] = os.getenv("LOKI_URL", "http://localhost:3100")
os.environ["GRAFANA_URL"] = os.getenv("GRAFANA_URL", "http://localhost:3001")

print("=== Starting Full Incident Investigation Simulation ===")
print(f"Prometheus: {os.environ['PROMETHEUS_URL']}")
print(f"Loki: {os.environ['LOKI_URL']}")
print(f"Grafana: {os.environ['GRAFANA_URL']}")
print("=" * 60)

# Simulate investigating alert from 30 minutes ago
alert_time = int(time.time()) - 1800
investigation_start = alert_time - 300
investigation_end = alert_time + 300

# 1. Check CPU trend
print("\n=== Step 1: Checking CPU Metrics ===")
cpu_result = PrometheusQuery.invoke({
    'query': 'rate(node_cpu_seconds_total{mode!="idle"}[1m])',
    'time_range_minutes': 60,
    'step_seconds': 60
})
print(cpu_result[:500] + ("..." if len(cpu_result) > 500 else ""))

# 2. Search logs
print("\n=== Step 2: Searching Logs for Errors ===")
log_result = LokiLogSearch.invoke({
    'query': '{job="docker"} |~ "(?i)(error|exception)"',
    'time_range_minutes': 10,
    'limit': 5,
    'target_service': 'news-classifier-api'
})
print(log_result)

# 3. Generate dashboard link
print("\n=== Step 3: Generating Grafana Dashboard Link ===")
dashboard_link = GrafanaDashboardLink.invoke({
    'dashboard_uid': 'news_classifier_health',
    'time_range_minutes': 60,
    'service_filter': 'news-classifier-api'
})
print(dashboard_link)

print("\n" + "=" * 60)
print("Investigation simulation completed!")
