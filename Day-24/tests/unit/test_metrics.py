"""
Unit Tests: Monitoring & Prometheus Metrics
Validates telemetry recording, gauge states, and Prometheus exposition formatting.
"""

from app.core.metrics import MetricsRegistry


def test_metrics_registry_initialization():
    """Verify clean initialization of telemetry registry."""
    reg = MetricsRegistry()
    assert reg.get_uptime_seconds() >= 0.0
    assert reg.active_workflows_gauge == 0


def test_record_http_request():
    """Verify HTTP request telemetry recording and latency aggregation."""
    reg = MetricsRegistry()
    reg.record_http_request("GET", "/health/live", 200, 0.015)
    reg.record_http_request("GET", "/health/live", 200, 0.025)

    assert reg.http_requests_total[("GET", "/health/live", "200")] == 2
    assert reg.http_request_duration_count["/health/live"] == 2
    assert round(reg.http_request_duration_sum["/health/live"], 3) == 0.040


def test_active_workflows_gauge():
    """Verify thread-safe increments and decrements of active workflow gauge."""
    reg = MetricsRegistry()
    assert reg.active_workflows_gauge == 0
    reg.increment_active_workflows()
    reg.increment_active_workflows()
    assert reg.active_workflows_gauge == 2
    reg.decrement_active_workflows()
    assert reg.active_workflows_gauge == 1
    reg.decrement_active_workflows()
    assert reg.active_workflows_gauge == 0
    # Guard against negative values
    reg.decrement_active_workflows()
    assert reg.active_workflows_gauge == 0


def test_record_workflow_execution():
    """Verify multi-agent workflow completion tracking."""
    reg = MetricsRegistry()
    reg.record_workflow_execution("streamlined", "completed", 0.05)
    assert reg.workflows_total[("streamlined", "completed")] == 1
    assert reg.workflow_duration_count["streamlined"] == 1


def test_record_finance_approval():
    """Verify finance invoice approval decision tracking."""
    reg = MetricsRegistry()
    reg.record_finance_approval("approved", "straight_through_processing")
    reg.record_finance_approval("pending_approval", "manager_approval")

    assert reg.finance_invoices_total[("approved", "straight_through_processing")] == 1
    assert reg.finance_invoices_total[("pending_approval", "manager_approval")] == 1


def test_format_prometheus_metrics():
    """Verify generated string follows Prometheus exposition standard."""
    reg = MetricsRegistry()
    reg.record_http_request("POST", "/api/v1/workflow/run", 200, 0.08)
    reg.increment_active_workflows()
    reg.record_agent_node("coordinator_agent")

    prom_text = reg.format_prometheus_metrics()

    assert "# HELP linkific_uptime_seconds" in prom_text
    assert "# TYPE linkific_uptime_seconds counter" in prom_text
    assert "# HELP linkific_http_requests_total" in prom_text
    assert 'linkific_http_requests_total{method="POST",endpoint="/api/v1/workflow/run",status="200"} 1' in prom_text
    assert "linkific_active_workflows 1" in prom_text
    assert 'linkific_agent_node_executions_total{agent_role="coordinator_agent"} 1' in prom_text


def test_get_summary_dict():
    """Verify JSON summary generation for dashboards."""
    reg = MetricsRegistry()
    reg.record_http_request("GET", "/metrics", 200, 0.01)
    summary = reg.get_summary_dict()

    assert "uptime_seconds" in summary
    assert "total_http_requests" in summary
    assert summary["total_http_requests"] == 1
    assert "average_endpoint_latency_seconds" in summary
