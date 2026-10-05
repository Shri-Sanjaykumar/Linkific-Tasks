"""
Linkific Enterprise AI Service - Monitoring & Metrics Registry
Lightweight in-memory telemetry registry providing Prometheus exposition formatting.
"""

import time
from typing import Dict, Any
from collections import defaultdict
from threading import Lock


class MetricsRegistry:
    """
    Thread-safe metrics registry collecting operational telemetry for the service.
    Outputs metrics in standard Prometheus exposition text format.
    """

    def __init__(self):
        self._lock = Lock()
        self.start_time = time.time()

        # Metrics Counters & Gauges
        self.http_requests_total = defaultdict(int)  # (method, endpoint, status_code) -> count
        self.http_request_duration_sum = defaultdict(float)  # (endpoint) -> total_seconds
        self.http_request_duration_count = defaultdict(int)  # (endpoint) -> count

        self.active_workflows_gauge = 0

        self.workflows_total = defaultdict(int)  # (mode, status) -> count
        self.workflow_duration_sum = defaultdict(float)  # (mode) -> total_seconds
        self.workflow_duration_count = defaultdict(int)  # (mode) -> count

        self.finance_invoices_total = defaultdict(int)  # (status, tier) -> count
        self.agent_node_executions_total = defaultdict(int)  # (agent_role) -> count

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration_seconds: float) -> None:
        """Record an incoming HTTP request and its processing latency."""
        with self._lock:
            key = (method, endpoint, str(status_code))
            self.http_requests_total[key] += 1
            self.http_request_duration_sum[endpoint] += duration_seconds
            self.http_request_duration_count[endpoint] += 1

    def increment_active_workflows(self) -> None:
        """Increment active workflow gauge."""
        with self._lock:
            self.active_workflows_gauge += 1

    def decrement_active_workflows(self) -> None:
        """Decrement active workflow gauge."""
        with self._lock:
            if self.active_workflows_gauge > 0:
                self.active_workflows_gauge -= 1

    def record_workflow_execution(self, mode: str, status: str, duration_seconds: float) -> None:
        """Record completed multi-agent workflow execution."""
        with self._lock:
            self.workflows_total[(mode, status)] += 1
            self.workflow_duration_sum[mode] += duration_seconds
            self.workflow_duration_count[mode] += 1

    def record_finance_approval(self, status: str, tier: str) -> None:
        """Record finance invoice approval routing decision."""
        with self._lock:
            self.finance_invoices_total[(status, tier)] += 1

    def record_agent_node(self, agent_role: str) -> None:
        """Record invocation of a specialized agent node."""
        with self._lock:
            self.agent_node_executions_total[agent_role] += 1

    def get_uptime_seconds(self) -> float:
        """Return total elapsed uptime in seconds."""
        return round(time.time() - self.start_time, 2)

    def get_summary_dict(self) -> Dict[str, Any]:
        """Return a structured dictionary for JSON health/metrics dashboards."""
        with self._lock:
            total_requests = sum(self.http_requests_total.values())
            total_workflows = sum(self.workflows_total.values())
            avg_latencies = {}
            for ep, count in self.http_request_duration_count.items():
                if count > 0:
                    avg_latencies[ep] = round(self.http_request_duration_sum[ep] / count, 4)

            return {
                "uptime_seconds": self.get_uptime_seconds(),
                "total_http_requests": total_requests,
                "active_workflows": self.active_workflows_gauge,
                "total_workflows_completed": total_workflows,
                "http_requests_breakdown": {
                    f"{m} {ep} [{st}]": count for (m, ep, st), count in self.http_requests_total.items()
                },
                "average_endpoint_latency_seconds": avg_latencies,
                "finance_invoices_processed": dict(self.finance_invoices_total),
                "agent_node_executions": dict(self.agent_node_executions_total),
            }

    def format_prometheus_metrics(self) -> str:
        """Render registered metrics into official Prometheus line exposition format."""
        lines = []
        now_ts = int(time.time() * 1000)

        with self._lock:
            # Service Uptime
            lines.append("# HELP linkific_uptime_seconds Total runtime of the service in seconds")
            lines.append("# TYPE linkific_uptime_seconds counter")
            lines.append(f"linkific_uptime_seconds {self.get_uptime_seconds()}")

            # HTTP Requests Total
            lines.append("# HELP linkific_http_requests_total Total number of HTTP requests processed")
            lines.append("# TYPE linkific_http_requests_total counter")
            for (method, endpoint, status), count in self.http_requests_total.items():
                lines.append(f'linkific_http_requests_total{{method="{method}",endpoint="{endpoint}",status="{status}"}} {count}')

            # HTTP Request Duration
            lines.append("# HELP linkific_http_request_duration_seconds Total seconds spent processing HTTP requests")
            lines.append("# TYPE linkific_http_request_duration_seconds summary")
            for endpoint, total_sec in self.http_request_duration_sum.items():
                count = self.http_request_duration_count[endpoint]
                lines.append(f'linkific_http_request_duration_seconds_sum{{endpoint="{endpoint}"}} {round(total_sec, 6)}')
                lines.append(f'linkific_http_request_duration_seconds_count{{endpoint="{endpoint}"}} {count}')

            # Active Workflows Gauge
            lines.append("# HELP linkific_active_workflows Current number of active in-flight multi-agent workflows")
            lines.append("# TYPE linkific_active_workflows gauge")
            lines.append(f"linkific_active_workflows {self.active_workflows_gauge}")

            # Workflows Total
            lines.append("# HELP linkific_workflows_total Total multi-agent workflows executed")
            lines.append("# TYPE linkific_workflows_total counter")
            for (mode, status), count in self.workflows_total.items():
                lines.append(f'linkific_workflows_total{{mode="{mode}",status="{status}"}} {count}')

            # Agent Nodes Executions
            lines.append("# HELP linkific_agent_node_executions_total Total invocations of agent reasoning nodes")
            lines.append("# TYPE linkific_agent_node_executions_total counter")
            for role, count in self.agent_node_executions_total.items():
                lines.append(f'linkific_agent_node_executions_total{{agent_role="{role}"}} {count}')

            # Finance Invoices Total
            lines.append("# HELP linkific_finance_invoices_total Total finance invoices processed through automation gates")
            lines.append("# TYPE linkific_finance_invoices_total counter")
            for (status, tier), count in self.finance_invoices_total.items():
                lines.append(f'linkific_finance_invoices_total{{status="{status}",tier="{tier}"}} {count}')

        return "\n".join(lines) + "\n"


# Global singleton metrics registry
metrics_registry = MetricsRegistry()
