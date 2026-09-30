from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd
import streamlit as st

from src.config import SETTINGS
from src.exports import cases_to_frame, export_csv, export_excel, export_json
from src.generator import generate_cases, regenerate_case
from src.models import ReviewStatus, TestCase
from src.parser import read_uploaded_file
from src.quality import coverage_metrics, quality_findings
from src.sample_data import SAMPLE_REQUIREMENT

st.set_page_config(page_title="AI Test Case Studio", page_icon="🧪", layout="wide")
st.markdown("""<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
.hero {background:linear-gradient(120deg,#10243E,#1E6FD9);color:white;padding:24px 30px;border-radius:14px;margin-bottom:18px}
.hero h1 {margin:0;font-size:2.1rem}.hero p{margin:7px 0 0;color:#D7EAF8}
.small-note {color:#607487;font-size:.87rem}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>AI-Assisted Test Case Writing</h1><p>Requirement analysis, test generation, QA review, coverage, and export</p></div>', unsafe_allow_html=True)

if "requirement" not in st.session_state:
    st.session_state.requirement = SAMPLE_REQUIREMENT
if "result" not in st.session_state:
    st.session_state.result = None
if "audit" not in st.session_state:
    st.session_state.audit = []

with st.sidebar:
    st.header("POC controls")
    mode = st.radio("Generation engine", ["Demo Engine", "Vertex AI Gemini"], help="Demo Engine is deterministic and requires no cloud model access.")
    if mode == "Vertex AI Gemini":
        if SETTINGS.vertex_ready:
            st.success(f"Configured: {SETTINGS.model_name}")
        else:
            st.error("Set GOOGLE_CLOUD_PROJECT before using Vertex AI.")
    selected_types = st.multiselect("Test types", ["Functional", "Negative", "Boundary", "Validation", "Security", "Regression"], default=["Functional", "Negative", "Boundary", "Validation", "Security", "Regression"])
    case_count = st.slider("Number of test cases", 6, 24, 12)
    st.divider()
    st.caption("Human review is mandatory before a case becomes approved.")

tab_input, tab_analysis, tab_review, tab_dashboard = st.tabs(["1. Requirement", "2. AI analysis", "3. QA review", "4. Coverage & export"])

with tab_input:
    left, right = st.columns([2, 1])
    with left:
        uploaded = st.file_uploader("Upload requirement", type=["txt", "md", "csv", "json"])
        if uploaded is not None:
            try:
                st.session_state.requirement = read_uploaded_file(uploaded)
            except Exception as exc:
                st.error(str(exc))
        requirement = st.text_area("Requirement, user story, or specification", value=st.session_state.requirement, height=300)
        st.session_state.requirement = requirement
        generate_clicked = st.button("Generate test suite", type="primary", use_container_width=True, disabled=not selected_types)
    with right:
        st.subheader("POC scope")
        st.markdown("- Structured test cases\n- Traceability\n- Ambiguity detection\n- Quality checks\n- Human approval\n- Excel, CSV, JSON export")
        st.info("For a dependable client demo, first run the sample with Demo Engine. Switch to Vertex AI after cloud configuration is confirmed.")
    if generate_clicked:
        try:
            with st.spinner("Analyzing requirement and designing tests..."):
                st.session_state.result = generate_cases(requirement, selected_types, case_count, mode)
            st.session_state.audit.append({"time": datetime.now(timezone.utc).isoformat(), "action": "Generated suite", "detail": f"{case_count} cases with {mode}"})
            st.success("Test suite generated. Open the AI analysis and QA review tabs.")
        except Exception as exc:
            st.error(f"Generation failed: {exc}")

result = st.session_state.result

with tab_analysis:
    if not result:
        st.info("Generate a test suite from the Requirement tab.")
    else:
        a = result.analysis
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Requirement", a.requirement_id)
        c2.metric("Business rules", len(a.business_rules))
        c3.metric("Ambiguities", len(a.ambiguities))
        c4.metric("Generated cases", len(result.test_cases))
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Extracted understanding")
            st.write("**Actors:**", ", ".join(a.actors))
            st.write("**Business rules**")
            for rule in a.business_rules:
                st.write(f"- {rule}")
            st.write("**Constraints**")
            for constraint in a.constraints:
                st.write(f"- {constraint}")
        with col2:
            st.subheader("Questions for the product owner")
            if a.ambiguities:
                for item in a.ambiguities:
                    st.warning(item)
            else:
                st.success("No obvious ambiguity detected by the parser.")
            st.caption(f"Generated with: {result.model_used}")

with tab_review:
    if not result:
        st.info("Generate a test suite from the Requirement tab.")
    else:
        type_filter = st.multiselect("Filter by type", sorted({c.test_type for c in result.test_cases}), default=[])
        visible = [(i, c) for i, c in enumerate(result.test_cases) if not type_filter or c.test_type in type_filter]
        for idx, case in visible:
            with st.expander(f"{case.test_case_id} · {case.test_type} · {case.status.value} — {case.scenario}", expanded=idx == 0):
                scenario = st.text_input("Scenario", case.scenario, key=f"scenario_{idx}")
                preconditions = st.text_area("Preconditions", case.preconditions, key=f"pre_{idx}")
                steps = st.text_area("Steps (one per line)", "\n".join(case.steps), key=f"steps_{idx}")
                test_data = st.text_input("Test data", case.test_data, key=f"data_{idx}")
                expected = st.text_area("Expected result", case.expected_result, key=f"expected_{idx}")
                comment = st.text_input("Reviewer comment", case.reviewer_comment, key=f"comment_{idx}")
                b1, b2, b3, b4 = st.columns(4)
                if b1.button("Accept", key=f"accept_{idx}", use_container_width=True):
                    case.status = ReviewStatus.ACCEPTED; case.reviewer_comment = comment
                    st.session_state.audit.append({"time": datetime.now(timezone.utc).isoformat(), "action": "Accepted", "detail": case.test_case_id}); st.rerun()
                if b2.button("Save edits", key=f"edit_{idx}", use_container_width=True):
                    case.scenario=scenario; case.preconditions=preconditions; case.steps=[s.strip() for s in steps.splitlines() if s.strip()]; case.test_data=test_data; case.expected_result=expected; case.reviewer_comment=comment; case.status=ReviewStatus.EDITED
                    st.session_state.audit.append({"time": datetime.now(timezone.utc).isoformat(), "action": "Edited", "detail": case.test_case_id}); st.rerun()
                if b3.button("Reject", key=f"reject_{idx}", use_container_width=True):
                    case.status=ReviewStatus.REJECTED; case.reviewer_comment=comment
                    st.session_state.audit.append({"time": datetime.now(timezone.utc).isoformat(), "action": "Rejected", "detail": case.test_case_id}); st.rerun()
                if b4.button("Regenerate", key=f"regen_{idx}", use_container_width=True):
                    result.test_cases[idx]=regenerate_case(case)
                    st.session_state.audit.append({"time": datetime.now(timezone.utc).isoformat(), "action": "Regenerated", "detail": case.test_case_id}); st.rerun()

with tab_dashboard:
    if not result:
        st.info("Generate a test suite from the Requirement tab.")
    else:
        metrics = coverage_metrics(result.analysis, result.test_cases)
        accepted = sum(c.status in {ReviewStatus.ACCEPTED, ReviewStatus.EDITED} for c in result.test_cases)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rule coverage", f"{metrics['coverage']}%")
        m2.metric("Approved / edited", accepted)
        m3.metric("Needs review", metrics["statuses"].get("Needs review", 0))
        m4.metric("Average confidence", f"{sum(c.confidence for c in result.test_cases)/len(result.test_cases):.0%}")
        left, right = st.columns(2)
        with left:
            st.subheader("Test type distribution")
            st.bar_chart(pd.Series(metrics["types"], name="Cases"))
        with right:
            st.subheader("Automated quality checks")
            findings = quality_findings(result.test_cases)
            if findings:
                for finding in findings:
                    st.warning(finding)
            else:
                st.success("No duplicate, incomplete, vague, or low-confidence cases detected.")
        st.subheader("Traceability table")
        st.dataframe(cases_to_frame(result.test_cases)[["test_case_id", "requirement_id", "test_type", "scenario", "source_rule", "status"]], use_container_width=True, hide_index=True)
        approved = [c for c in result.test_cases if c.status in {ReviewStatus.ACCEPTED, ReviewStatus.EDITED}]
        export_set = approved if approved else result.test_cases
        if not approved:
            st.caption("No cases are approved yet. Downloads currently contain the complete draft suite.")
        d1, d2, d3 = st.columns(3)
        d1.download_button("Download Excel", export_excel(export_set), "approved_test_suite.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        d2.download_button("Download CSV", export_csv(export_set), "approved_test_suite.csv", "text/csv", use_container_width=True)
        d3.download_button("Download JSON", export_json(export_set), "approved_test_suite.json", "application/json", use_container_width=True)
        with st.expander("Audit trail"):
            st.dataframe(pd.DataFrame(st.session_state.audit), use_container_width=True, hide_index=True)

