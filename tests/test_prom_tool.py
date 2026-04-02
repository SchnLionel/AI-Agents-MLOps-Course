import os
import sys
# Add src/aiops_agent_monitor to path
sys.path.insert(0, os.path.abspath('src/aiops_agent_monitor'))

from tools.mlops_tools import PrometheusQuery

# Use localhost:9091 for local testing (matches docker-compose port mapping)
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9091")
os.environ["PROMETHEUS_URL"] = PROMETHEUS_URL

print(f"Using Prometheus URL: {PROMETHEUS_URL}")
print("=" * 60)

# Test 1: Query CPU metrics
print("\n=== Test 1: Query CPU Metrics ===")
try:
    result = PrometheusQuery.invoke({
        'query': 'rate(node_cpu_seconds_total{mode!="idle"}[5m])',
        'time_range_minutes': 15,
        'step_seconds': 30
    })
    print(result)
except Exception as e:
    print(f"Error in Test 1: {e}")

# Test 2: Invalid time range (should fail gracefully)
print("\n=== Test 2: Invalid Time Range (Expected Error) ===")
result = PrometheusQuery.invoke({
    'query': 'cpu_usage',
    'time_range_minutes': -10,  # Invalid!
    'step_seconds': 30
})
print(result)

# Test 3: Invalid step seconds (should fail gracefully - New Validation)
print("\n=== Test 3: Invalid Step Seconds (Expected Error) ===")
result = PrometheusQuery.invoke({
    'query': 'up',
    'time_range_minutes': 5,
    'step_seconds': 5  # Too small! (< 10)
})
print(result)

# Test 4: Disallowed PromQL function (Expected Error - New Security)
print("\n=== Test 4: Disallowed PromQL Function (Expected Error) ===")
result = PrometheusQuery.invoke({
    'query': 'dangerous_function(cpu_usage)',
    'time_range_minutes': 5,
    'step_seconds': 30
})
print(result)

print("\n" + "=" * 60)
print("Tests completed!")
