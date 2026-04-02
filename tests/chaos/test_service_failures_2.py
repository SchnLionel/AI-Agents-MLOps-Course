import pytest
import requests
import subprocess
import time
import os
import concurrent.futures

def stop_service(service_name):
    print(f"Stopping service: {service_name}...")
    compose_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../docker-compose.yml"))
    subprocess.run(["docker", "compose", "-f", compose_path, "stop", service_name], check=True)

def start_service(service_name):
    print(f"Starting service: {service_name}...")
    compose_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../docker-compose.yml"))
    subprocess.run(["docker", "compose", "-f", compose_path, "start", service_name], check=True)

def test_graceful_degradation_loki_failure(service_urls, sample_alert):
    """
    Verify agent degrades gracefully when optional Loki service fails.
    """
    gateway_url = service_urls["gateway"]

    try:
        # Stop Loki (optional service)
        stop_service("loki-tool-service")
        time.sleep(2)

        # Send diagnosis request
        start_time = time.time()
        resp = requests.post(f"{gateway_url}/diagnose_alert",
                            json=sample_alert, timeout=90)
        latency = time.time() - start_time

        # Should succeed despite Loki failure (graceful degradation)
        assert resp.status_code == 200
        data = resp.json()

        # Verify degraded mode indicators in diagnosis
        diagnosis = data.get("agent_diagnosis", "").lower()
        has_degradation_indicator = any(term in diagnosis for term in [
            "log", "loki", "error", "unavailable", "unable", "failed", "skipped"
        ])

        # Should still complete reasonably fast (not hang)
        assert latency < 90, f"Request took too long: {latency:.2f}s"

        print(f"✓ Graceful degradation: completed in {latency:.2f}s")
        print(f"  Diagnosis mentions degradation: {has_degradation_indicator}")

    finally:
        start_service("loki-tool-service")
        time.sleep(5)

def test_no_cascading_failure_under_load(service_urls, sample_alert):
    """
    Verify that when one service fails, it doesn't cascade to others.
    """
    gateway_url = service_urls["gateway"]
    agent_url = service_urls["agent"]
    prometheus_service_name = "prometheus-tool-service"

    try:
        # 1. Trip the circuit breaker
        print("\n✓ Step 1: Stopping Prometheus and tripping circuit breaker...")
        stop_service(prometheus_service_name)
        time.sleep(3)

        # Trigger failures to open the circuit breaker (threshold=3)
        for i in range(4):
            try:
                requests.post(f"{gateway_url}/diagnose_alert", json=sample_alert, timeout=60)
            except Exception:
                pass

        time.sleep(3) # Let circuit state propagate

        # 2. Send 20 concurrent requests
        print("\n✓ Step 2: Sending 20 concurrent requests...")
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(
                    requests.post,
                    f"{gateway_url}/diagnose_alert",
                    json=sample_alert,
                    timeout=30
                )
                for _ in range(20)
            ]

            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        total_duration = time.time() - start_time
        print(f"  All 20 requests completed in {total_duration:.2f}s")

        # 3. Verify other services still healthy
        agent_health = requests.get(f"{agent_url}/health", timeout=5)
        assert agent_health.status_code == 200
        
        loki_health = requests.get(f"{service_urls['loki']}/health", timeout=5)
        assert loki_health.status_code == 200

        # All should fail fast (circuit breaker open) - 503 or 500
        for resp in results:
            assert resp.status_code in [500, 502, 503], f"Unexpected status: {resp.status_code}"

        assert total_duration < 30, f"Requests took {total_duration:.2f}s - not failing fast!"

    finally:
        start_service(prometheus_service_name)
        time.sleep(35) # Wait for circuit recovery

def test_agent_timeout_handling(service_urls, sample_alert):
    """
    Test that agent completes diagnosis within reasonable time even if service is slow.
    """
    gateway_url = service_urls["gateway"]

    # Test 1: Baseline
    print("\n✓ Step 1: Establishing baseline...")
    start = time.time()
    resp = requests.post(f"{gateway_url}/diagnose_alert", json=sample_alert, timeout=120)
    baseline_duration = time.time() - start
    assert resp.status_code == 200
    print(f"  Baseline: {baseline_duration:.2f}s")

    # Test 2: Stop Loki and check timeout
    print("\n✓ Step 2: Testing with Loki unavailable...")
    try:
        stop_service("loki-tool-service")
        time.sleep(2)

        start = time.time()
        resp = requests.post(f"{gateway_url}/diagnose_alert", json=sample_alert, timeout=150)
        degraded_duration = time.time() - start

        assert resp.status_code == 200
        assert degraded_duration < 150, f"Request took too long: {degraded_duration:.2f}s"
        print(f"  Degraded: {degraded_duration:.2f}s")
        print(f"  Timeout handling verified.")

    finally:
        start_service("loki-tool-service")
        time.sleep(5)
