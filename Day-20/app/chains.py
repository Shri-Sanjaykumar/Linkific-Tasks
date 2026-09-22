"""
Day 20 — Tool Chaining Pipelines
Implements and demonstrates 3 concrete multi-tool pipelines:
1. File Reader -> Data Analyzer (Reads CSV file, passes records to Data Analyzer)
2. Database Tool -> Data Analyzer (Retrieves SQL records, analyzes statistical summary)
3. Date Tool -> Calculator (Computes date difference in days, multiplies by rate/hours)
"""

import time
from typing import Dict, Any, Optional
from .schemas import ToolChainResult, ToolChainStep, ToolResult
from .registry import ToolRegistry, default_registry


class ToolChainPipeline:
    """Executes multi-tool workflows with intermediate payload routing and error propagation."""

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or default_registry

    def chain_file_to_analyzer(
        self,
        file_path: str = "Day-20/data/sample_sales.csv",
        analysis_operation: str = "summary",
        target_column: Optional[str] = None
    ) -> ToolChainResult:
        """
        Tool Chain 1: File Reader -> Data Analyzer
        Step 1: Read CSV file and parse structure.
        Step 2: Pass parsed tabular records to Data Analyzer for statistical profiling.
        """
        start_time = time.time()
        steps = []

        # Step 1: Read file
        s1_start = time.time()
        s1_args = {"file_path": file_path}
        res1 = self.registry.execute("file_reader", s1_args)
        s1_dur = (time.time() - s1_start) * 1000

        step1 = ToolChainStep(
            step_number=1,
            tool_name="file_reader",
            description=f"Read file '{file_path}' and extract tabular structure.",
            input_mapping={"source": "user_argument", "file_path": file_path},
            resolved_arguments=s1_args,
            output=res1,
            status="success" if res1.success else "failed",
            duration_ms=round(s1_dur, 2)
        )
        steps.append(step1)

        if not res1.success:
            total_dur = (time.time() - start_time) * 1000
            return ToolChainResult(
                chain_name="File Reader -> Data Analyzer",
                chain_description="Extracts data from local CSV and passes records to Data Analyzer.",
                success=False,
                steps=steps,
                final_output=None,
                error=f"Step 1 (file_reader) failed: {res1.error}",
                total_duration_ms=round(total_dur, 2)
            )

        # Intermediate payload routing
        parsed_records = res1.data.get("parsed_structure")
        raw_content = res1.data.get("content")
        payload_to_pass = parsed_records if parsed_records is not None else raw_content

        # Step 2: Data Analyzer
        s2_start = time.time()
        s2_args = {
            "operation": analysis_operation,
            "data": payload_to_pass,
            "target_column": target_column
        }
        res2 = self.registry.execute("data_analyzer", s2_args)
        s2_dur = (time.time() - s2_start) * 1000

        step2 = ToolChainStep(
            step_number=2,
            tool_name="data_analyzer",
            description=f"Analyze records with operation '{analysis_operation}'.",
            input_mapping={"source": "step_1.output.data.parsed_structure", "operation": analysis_operation},
            resolved_arguments={"operation": analysis_operation, "target_column": target_column, "records_count": len(parsed_records) if parsed_records else None},
            output=res2,
            status="success" if res2.success else "failed",
            duration_ms=round(s2_dur, 2)
        )
        steps.append(step2)

        total_dur = (time.time() - start_time) * 1000
        return ToolChainResult(
            chain_name="File Reader -> Data Analyzer",
            chain_description="Extracts data from local CSV and passes records to Data Analyzer.",
            success=res2.success,
            steps=steps,
            final_output=res2.data if res2.success else None,
            error=res2.error if not res2.success else None,
            total_duration_ms=round(total_dur, 2)
        )

    def chain_database_to_analyzer(
        self,
        query: str = "SELECT salary, tenure_years FROM employees;",
        analysis_operation: str = "summary",
        target_column: Optional[str] = None
    ) -> ToolChainResult:
        """
        Tool Chain 2: Database Tool -> Data Analyzer
        Step 1: Query SQL database to extract dataset.
        Step 2: Pass records to Data Analyzer to calculate summary statistics or column averages.
        """
        start_time = time.time()
        steps = []

        # Step 1: Database Query
        s1_start = time.time()
        s1_args = {"operation": "query", "query": query}
        res1 = self.registry.execute("database_tool", s1_args)
        s1_dur = (time.time() - s1_start) * 1000

        step1 = ToolChainStep(
            step_number=1,
            tool_name="database_tool",
            description=f"Execute SQL query '{query}'.",
            input_mapping={"source": "user_argument", "query": query},
            resolved_arguments=s1_args,
            output=res1,
            status="success" if res1.success else "failed",
            duration_ms=round(s1_dur, 2)
        )
        steps.append(step1)

        if not res1.success:
            total_dur = (time.time() - start_time) * 1000
            return ToolChainResult(
                chain_name="Database Tool -> Data Analyzer",
                chain_description="Queries records from SQLite database and passes them to Data Analyzer.",
                success=False,
                steps=steps,
                final_output=None,
                error=f"Step 1 (database_tool) failed: {res1.error}",
                total_duration_ms=round(total_dur, 2)
            )

        # Intermediate payload routing
        records = res1.data.get("records", [])

        # Step 2: Data Analyzer
        s2_start = time.time()
        s2_args = {
            "operation": analysis_operation,
            "data": records,
            "target_column": target_column
        }
        res2 = self.registry.execute("data_analyzer", s2_args)
        s2_dur = (time.time() - s2_start) * 1000

        step2 = ToolChainStep(
            step_number=2,
            tool_name="data_analyzer",
            description=f"Perform '{analysis_operation}' on retrieved SQL records.",
            input_mapping={"source": "step_1.output.data.records", "operation": analysis_operation},
            resolved_arguments={"operation": analysis_operation, "target_column": target_column, "records_count": len(records)},
            output=res2,
            status="success" if res2.success else "failed",
            duration_ms=round(s2_dur, 2)
        )
        steps.append(step2)

        total_dur = (time.time() - start_time) * 1000
        return ToolChainResult(
            chain_name="Database Tool -> Data Analyzer",
            chain_description="Queries records from SQLite database and passes them to Data Analyzer.",
            success=res2.success,
            steps=steps,
            final_output=res2.data if res2.success else None,
            error=res2.error if not res2.success else None,
            total_duration_ms=round(total_dur, 2)
        )

    def chain_date_to_calculator(
        self,
        start_date: str = "2026-09-01",
        end_date: str = "2026-09-22",
        multiplier: float = 8.0,
        operation: str = "multiply"
    ) -> ToolChainResult:
        """
        Tool Chain 3: Date Tool -> Calculator
        Step 1: Calculate calendar days between two milestone dates.
        Step 2: Pass days value to Calculator to multiply by hours/day or daily burn rate.
        """
        start_time = time.time()
        steps = []

        # Step 1: Date Difference
        s1_start = time.time()
        s1_args = {"operation": "date_diff", "start_date": start_date, "end_date": end_date}
        res1 = self.registry.execute("date_tool", s1_args)
        s1_dur = (time.time() - s1_start) * 1000

        step1 = ToolChainStep(
            step_number=1,
            tool_name="date_tool",
            description=f"Calculate days difference between {start_date} and {end_date}.",
            input_mapping={"start_date": start_date, "end_date": end_date},
            resolved_arguments=s1_args,
            output=res1,
            status="success" if res1.success else "failed",
            duration_ms=round(s1_dur, 2)
        )
        steps.append(step1)

        if not res1.success:
            total_dur = (time.time() - start_time) * 1000
            return ToolChainResult(
                chain_name="Date Tool -> Calculator",
                chain_description="Computes milestone interval in days and multiplies by hourly/cost multiplier.",
                success=False,
                steps=steps,
                final_output=None,
                error=f"Step 1 (date_tool) failed: {res1.error}",
                total_duration_ms=round(total_dur, 2)
            )

        # Intermediate payload routing
        days_diff = res1.data.get("days_difference")

        # Step 2: Calculator
        s2_start = time.time()
        s2_args = {
            "a": float(days_diff),
            "b": float(multiplier),
            "operation": operation
        }
        res2 = self.registry.execute("calculator", s2_args)
        s2_dur = (time.time() - s2_start) * 1000

        step2 = ToolChainStep(
            step_number=2,
            tool_name="calculator",
            description=f"Calculate {days_diff} {operation} {multiplier}.",
            input_mapping={"source": "step_1.output.data.days_difference", "multiplier": multiplier},
            resolved_arguments=s2_args,
            output=res2,
            status="success" if res2.success else "failed",
            duration_ms=round(s2_dur, 2)
        )
        steps.append(step2)

        total_dur = (time.time() - start_time) * 1000
        final_payload = {
            "start_date": start_date,
            "end_date": end_date,
            "interval_days": days_diff,
            "multiplier": multiplier,
            "operation": operation,
            "calculated_total": res2.data.get("result") if res2.success else None
        }

        return ToolChainResult(
            chain_name="Date Tool -> Calculator",
            chain_description="Computes milestone interval in days and multiplies by hourly/cost multiplier.",
            success=res2.success,
            steps=steps,
            final_output=final_payload if res2.success else None,
            error=res2.error if not res2.success else None,
            total_duration_ms=round(total_dur, 2)
        )
