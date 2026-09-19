"""
Day 18 — AI Agent Core Implementation
Implements DocumentResearchAgent following a structured ReAct-inspired workflow:
Plan -> Act -> Observe -> Decide -> [Refine] -> Final Response.
"""

import re
from typing import List, Dict, Any, Optional
from .schemas import AgentState, AgentResponse, ExecutionPlan
from .memory import AgentMemory
from .planner import Planner
from .tools import ToolRegistry


class DocumentResearchAgent:
    """
    Document Research Assistant Agent for Linkific AI/ML Internship.
    Performs autonomous information retrieval, verification, and grounded answering
    across synthetic enterprise documentation using a ReAct-inspired workflow.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.state: AgentState = AgentState.INITIALIZED
        self.memory: AgentMemory = AgentMemory()
        self.tools_used: List[str] = []
        self.data_dir = data_dir

    def run(self, user_question: str) -> AgentResponse:
        """
        Executes the ReAct-inspired workflow for a user question.
        Returns a structured AgentResponse with grounded answer and execution trace.
        """
        self.memory.reset()
        self.tools_used = []

        # Handle empty/whitespace input
        clean_q = user_question.strip() if user_question else ""
        if not clean_q:
            self.state = AgentState.FINAL_RESPONSE
            self.memory.add_trace(
                state="PLAN",
                action_or_plan="Evaluated user question and detected empty input string.",
                decision="Return immediate polite prompt asking for a valid question."
            )
            return AgentResponse(
                question="",
                answer="Please provide a valid question regarding company policies, onboarding, training, or project workflows.",
                sources=[],
                status="no_relevant_information",
                plan=[],
                tools_used=[],
                execution_trace=self.memory.get_trace_dicts()
            )

        # ----------------------------------------------------------------------
        # 1. PLANNING STAGE (PLAN)
        # ----------------------------------------------------------------------
        self.state = AgentState.PLANNING
        plan: ExecutionPlan = Planner.create_plan(clean_q)

        self.memory.add_trace(
            state="PLAN",
            action_or_plan=f"Analyzed query '{clean_q}' and determined intent '{plan.intent}'. Created {len(plan.steps)}-step ordered execution plan.",
            decision=f"Target workflow: {plan.intent}"
        )

        # ----------------------------------------------------------------------
        # FAST PATH: UNSUPPORTED / OUT-OF-DOMAIN QUESTIONS
        # ----------------------------------------------------------------------
        if plan.intent == "unsupported_domain":
            # Step 1: Query analysis
            plan.steps[0].status = "completed"

            # Step 2: Knowledge base scope check
            self.state = AgentState.TOOL_EXECUTION
            self.memory.add_trace(
                state="ACT",
                action_or_plan="Recognized out-of-domain topic in query. Invoking domain boundary check.",
                tool=None
            )
            self.state = AgentState.OBSERVING
            self.memory.add_trace(
                state="OBSERVE",
                action_or_plan="Checked knowledge base domain scope.",
                observation="Topic does not match internal policies, onboarding, training guidelines, or project workflows."
            )
            plan.steps[1].status = "completed"

            # Step 3: Decision
            self.state = AgentState.DECIDING
            self.memory.add_trace(
                state="DECIDE",
                action_or_plan="Evaluated information availability.",
                decision="Strict adherence to grounding rules: reject out-of-domain query safely to avoid unsupported statements."
            )
            plan.steps[2].status = "completed"

            # Step 4: Final response
            self.state = AgentState.FINAL_RESPONSE
            self.tools_used.append("final_response")
            self.memory.add_trace(
                state="FINAL",
                action_or_plan="Constructed polite out-of-domain refusal.",
                decision="Finished execution safely."
            )
            plan.steps[3].status = "completed"

            return AgentResponse(
                question=clean_q,
                answer=(
                    f"I do not have access to real-time external financial, stock market, cryptocurrency, or general external data. "
                    f"My knowledge base contains synthetic demonstration documentation covering internal company policies, "
                    f"intern onboarding (DOC-ONBOARD-002), training guidelines (DOC-TRAIN-003), and project workflows (DOC-WORKFLOW-004)."
                ),
                sources=[],
                status="no_relevant_information",
                plan=[s.model_dump() for s in plan.steps],
                tools_used=self.tools_used,
                execution_trace=self.memory.get_trace_dicts()
            )

        # ----------------------------------------------------------------------
        # 2. TOOL SELECTION & EXECUTION STAGE (ACT)
        # ----------------------------------------------------------------------
        self.state = AgentState.TOOL_SELECTION
        primary_tool = "document_search"
        tool_args: Dict[str, Any] = {"query": clean_q, "top_k": 3}

        # Step 1: Analysis completed
        plan.steps[0].status = "completed"

        if plan.intent == "document_lookup":
            match = re.search(r"doc-[a-z0-9-]+", clean_q.lower())
            doc_id = match.group(0).upper() if match else "DOC-LEAVE-001"
            primary_tool = "document_lookup"
            tool_args = {"document_id": doc_id}
        elif plan.intent == "document_metadata":
            match = re.search(r"doc-[a-z0-9-]+", clean_q.lower())
            doc_id = match.group(0).upper() if match else "DOC-LEAVE-001"
            primary_tool = "document_metadata"
            tool_args = {"document_id": doc_id}

        self.state = AgentState.TOOL_EXECUTION
        self.tools_used.append(primary_tool)

        self.memory.add_trace(
            state="ACT",
            action_or_plan=f"Executing tool '{primary_tool}' with arguments: {tool_args}",
            tool=primary_tool
        )

        tool_res = ToolRegistry.execute(primary_tool, tool_args)
        self.memory.record_tool_result(tool_res)
        plan.steps[1].status = "completed"

        # ----------------------------------------------------------------------
        # 3. OBSERVATION STAGE (OBSERVE)
        # ----------------------------------------------------------------------
        self.state = AgentState.OBSERVING
        obs_summary = ""
        context_items = []

        if primary_tool == "document_search":
            search_items = tool_res.data if tool_res.success and isinstance(tool_res.data, list) else []
            if search_items:
                top_score = search_items[0]["relevance_score"]
                obs_summary = f"Retrieved {len(search_items)} chunk(s). Highest relevance score: {top_score}."
                for item in search_items:
                    self.memory.add_context(item["matched_text"], item["document_title"])
                    context_items.append(item)
            else:
                obs_summary = "Zero chunks matched query in knowledge base above minimum threshold."
        elif primary_tool == "document_lookup":
            if tool_res.success and tool_res.data:
                doc_title = tool_res.data.get("title", "Document")
                obs_summary = f"Successfully retrieved full document '{doc_title}' ({len(tool_res.data.get('content', ''))} chars)."
                self.memory.add_context(tool_res.data.get("content", ""), doc_title)
            else:
                obs_summary = "Document lookup failed: document ID not found in knowledge base."
        elif primary_tool == "document_metadata":
            if tool_res.success and tool_res.data:
                obs_summary = f"Retrieved metadata for '{tool_res.data.get('title')}': Category={tool_res.data.get('category')}, Version={tool_res.data.get('version')}."
                self.memory.add_context(str(tool_res.data), tool_res.data.get("title", "Metadata"))
            else:
                obs_summary = "Metadata retrieval failed: document ID not found."

        self.memory.add_trace(
            state="OBSERVE",
            action_or_plan="Inspected tool execution result.",
            observation=obs_summary
        )
        plan.steps[2].status = "completed"

        # ----------------------------------------------------------------------
        # 4. DECISION STAGE (DECIDE)
        # ----------------------------------------------------------------------
        self.state = AgentState.DECIDING
        decision_text = ""
        should_refine = False

        if primary_tool == "document_search":
            if context_items and context_items[0]["relevance_score"] >= 0.40:
                decision_text = "Retrieved context is highly relevant and sufficient. Proceeding to final response synthesis."
                # Step 4 (refinement evaluation) was evaluated; refinement itself was skipped
                if len(plan.steps) > 3:
                    plan.steps[3].status = "skipped"
            elif context_items and context_items[0]["relevance_score"] >= 0.25:
                should_refine = True
                decision_text = "Retrieved context has moderate relevance (< 0.40). Triggering single-pass query refinement."
                if len(plan.steps) > 3:
                    plan.steps[3].status = "completed"
            else:
                decision_text = "No context found above relevance threshold. Proceeding to factual no-information response."
                if len(plan.steps) > 3:
                    plan.steps[3].status = "skipped"
        else:
            if self.memory.retrieved_contexts:
                decision_text = "Target document retrieved successfully. Proceeding to response generation."
            else:
                decision_text = "Target document not found. Returning safe error notice."

        self.memory.add_trace(
            state="DECIDE",
            action_or_plan="Evaluated observation against sufficiency criteria.",
            decision=decision_text
        )

        # Single-pass query refinement if needed
        if should_refine:
            substantive = [w for w in clean_q.split() if len(w) > 3][:3]
            refined_query = " ".join(substantive)
            self.memory.add_trace(
                state="ACT",
                action_or_plan=f"Executing refined search with query: '{refined_query}'",
                tool="document_search"
            )
            ref_res = ToolRegistry.execute("document_search", {"query": refined_query, "top_k": 2})
            ref_items = ref_res.data if ref_res.success and isinstance(ref_res.data, list) else []
            if ref_items:
                obs2 = f"Refined search returned {len(ref_items)} additional chunk(s)."
                for item in ref_items:
                    self.memory.add_context(item["matched_text"], item["document_title"])
            else:
                obs2 = "Refined search produced no additional matches."
            self.memory.add_trace(
                state="OBSERVE",
                action_or_plan="Inspected refined search output.",
                observation=obs2
            )
            self.memory.add_trace(
                state="DECIDE",
                action_or_plan="Evaluated combined retrieved context.",
                decision="Proceeding to final response with accumulated context."
            )

        # ----------------------------------------------------------------------
        # 5. FINAL RESPONSE STAGE (FINAL)
        # ----------------------------------------------------------------------
        self.state = AgentState.FINAL_RESPONSE
        combined_context = self.memory.get_combined_context()

        res_output = ToolRegistry.execute("final_response", {
            "context": combined_context,
            "question": clean_q
        })
        self.tools_used.append("final_response")

        final_data = res_output.data if res_output.success else {}
        answer = final_data.get("answer", "No answer generated.")
        status = final_data.get("status", "answered")

        sources = self.memory.get_source_titles() if status == "answered" else []

        self.memory.add_trace(
            state="FINAL",
            action_or_plan="Synthesized grounded final response with source document attribution.",
            decision=f"Status={status}, Source count={len(sources)}"
        )

        # Mark final step as completed
        plan.steps[-1].status = "completed"

        return AgentResponse(
            question=clean_q,
            answer=answer,
            sources=sources,
            status=status,
            plan=[s.model_dump() for s in plan.steps],
            tools_used=self.tools_used,
            execution_trace=self.memory.get_trace_dicts()
        )
