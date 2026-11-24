"""Interactive Streamlit UI for BaseInt SQL Analytics Agent."""

import streamlit as st
import pandas as pd
from app.config import settings
from app.database.connection import get_engine
from app.database.schema import inspect_database_schema
from app.database.seed import seed_database
from app.agent.graph import execute_agent_pipeline
from app.ui.charts import generate_auto_chart

st.set_page_config(
    page_title="BaseInt | SQL Analytics Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure sample database is seeded on startup
@st.cache_resource
def init_db():
    engine = get_engine()
    seed_database(engine)
    return engine

engine = init_db()

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .doc-link {
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/database.png", width=64)
    st.title("BaseInt Controls")
    st.markdown("Enterprise SQL & Database Analytics Agent with Self-Correction Loops & AST Guardrails.")
    
    st.divider()
    st.subheader("System Status")
    st.success("Database: Connected (SQLite / PostgreSQL)")
    st.info(f"Self-Correction: Max {settings.max_retries} Retries")
    st.info("AST Read-Only Guard: Active")
    st.info("NeMo Input Rails: Active")
    
    st.divider()
    st.subheader("Documentation & Portal")
    st.markdown(f"📖 **Technical Reference Manual**: [localhost:3000/docs]({settings.base_url}/docs)")
    st.markdown(f"🛡️ **Security Audit Matrix**: [localhost:3000/security]({settings.base_url}/security)")
    st.markdown(f"📊 **Telemetry Dashboard**: [localhost:3000/telemetry]({settings.base_url}/telemetry)")
    st.markdown(f"⚡ **API Gateway**: [localhost:3000/api/v1/query]({settings.base_url}/api/v1/query)")

    st.divider()
    if st.button("🔄 Reseed Database"):
        msg = seed_database(engine)
        st.toast(msg, icon="✅")

# Header Section
st.markdown('<div class="main-header">BaseInt: SQL & Database Analytics Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Natural language query engine powered by LangGraph reflection loops, '
    'SQLAlchemy metadata introspection, AST safety filters, and dynamic Plotly chart canvases. '
    f'<a class="doc-link" href="{settings.base_url}">Visit Localhost:3000 Portal</a></div>',
    unsafe_allow_html=True
)

# Test Presets & Quick Actions
st.markdown("##### ⚡ Quick Test Presets:")
col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)

selected_preset = None
with col_q1:
    if st.button("Orders by Date (Test 1)", use_container_width=True):
        selected_preset = "Show orders sorted by date"
with col_q2:
    if st.button("DROP TABLE (Test 2)", use_container_width=True):
        selected_preset = "DROP TABLE orders; --"
with col_q3:
    if st.button("Top 5 Products", use_container_width=True):
        selected_preset = "Show top 5 products by price"
with col_q4:
    if st.button("Revenue by Region", use_container_width=True):
        selected_preset = "What is total revenue by customer region?"
with col_q5:
    if st.button("Product Categories", use_container_width=True):
        selected_preset = "Show product count and average price by category"

# Query Input Panel
st.subheader("1. Natural Language Query Panel")
query_val = selected_preset if selected_preset else ""
user_input = st.text_area(
    "Enter your database analytics question or prompt:",
    value=query_val,
    placeholder="e.g. 'Show orders sorted by date', 'What are our top 5 revenue generating customers?'",
    height=80
)

# Execution Options
col_exec, col_sim, col_empty = st.columns([1.5, 2, 4])
with col_exec:
    run_btn = st.button("🚀 Run Agentic Query", type="primary", use_container_width=True)
with col_sim:
    simulate_err = st.checkbox("Simulate initial column error (Test Case 1)", value=False)

if run_btn and user_input:
    with st.spinner("Executing BaseInt LangGraph pipeline with AST Guardrails & Schema Reflection..."):
        state = execute_agent_pipeline(user_input, simulate_initial_error=simulate_err)

    st.divider()

    # Results Section
    st.subheader("2. Query Execution & Verification Results")

    # Status Badges
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if state.get("ast_passed") and not state.get("error_message"):
            st.success("Status: Completed Successfully")
        elif not state.get("ast_passed"):
            st.error("Status: Blocked by Guardrail")
        else:
            st.warning("Status: Reflection Limit Reached")

    with b2:
        st.metric("Retries Executed", f"{state.get('retry_count', 0)} / {settings.max_retries}")

    with b3:
        ast_status = "SAFE (SELECT only)" if state.get("ast_passed") else "VIOLATION BLOCKED"
        st.metric("AST Safety Filter", ast_status)

    with b4:
        row_count = len(state.get("db_result") or [])
        st.metric("Rows Retrieved", row_count)

    # Security Warning Alert if Blocked
    if state.get("error_message"):
        if not state.get("ast_passed") or "NeMo Guardrail" in str(state.get("error_message")) or "Security Alert" in str(state.get("error_message")):
            st.error(f"🛡️ **Security Alert Triggered**: {state.get('error_message')}")
        else:
            st.warning(f"⚠️ **Execution Notice**: {state.get('error_message')}")

    # Code & Log Feeds (Collapsible)
    with st.expander("📝 Generated SQL Statement", expanded=True):
        if state.get("generated_sql"):
            st.code(state.get("generated_sql"), language="sql")
        else:
            st.info("No SQL generated (blocked prior to execution).")

    with st.expander("🔍 Telemetry & Self-Correction Logs", expanded=True):
        telemetry = state.get("telemetry_logs", [])
        if telemetry:
            for log_line in telemetry:
                if "error" in log_line.lower() or "blocked" in log_line.lower():
                    st.markdown(f":red[{log_line}]")
                elif "reflect" in log_line.lower() or "correct" in log_line.lower():
                    st.markdown(f":orange[{log_line}]")
                elif "success" in log_line.lower():
                    st.markdown(f":green[{log_line}]")
                else:
                    st.markdown(f":gray[{log_line}]")
        else:
            st.write("No telemetry logs recorded.")

    if state.get("reflection_history"):
        with st.expander("🔄 Reflection History Details", expanded=False):
            st.json(state.get("reflection_history"))

    # Tabular Data Results
    db_result = state.get("db_result")
    if db_result:
        st.subheader("3. Tabular Query Results")
        result_df = pd.DataFrame(db_result)
        st.dataframe(result_df, use_container_width=True)

        # Plotly Chart Canvas
        st.subheader("4. Dynamic Plotly Chart Canvas")
        fig = generate_auto_chart(db_result)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Query returned non-numeric or single-value data; standard tabular display active.")
    elif state.get("ast_passed") and not state.get("error_message"):
        st.info("Query executed successfully but returned 0 rows.")

# Footer
st.divider()
st.markdown(
    f"<center><small>BaseInt Enterprise SQL Agent • Connected to <a href='{settings.base_url}'>localhost:3000</a> • "
    "Full Compliance with LangGraph Self-Correction & AST Security Specifications</small></center>",
    unsafe_allow_html=True
)
