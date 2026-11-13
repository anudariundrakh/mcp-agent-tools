from __future__ import annotations

import asyncio
import os

import streamlit as st

from src.client.agent_loop import AgentLoop
from src.client.mcp_client import MCPToolClient


st.set_page_config(page_title="MCP Enterprise Ops Assistant", page_icon="🛡️", layout="wide")
st.title("🛡️ MCP Enterprise Operations Assistant")
st.caption("Dynamic tool discovery • stdio MCP • zero-trust SQL/math controls • live Open-Meteo weather")

with st.sidebar:
    st.header("Agent Settings")
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    use_openai = st.toggle("Use OpenAI agent loop", value=False, disabled=not has_key)
    st.write("OpenAI key detected:" , "✅" if has_key else "❌")
    st.info("No paid API key is required for Deterministic Demo mode.")

client = MCPToolClient()

st.subheader("MCP Inspector")
try:
    tools = asyncio.run(client.list_tools())
    cols = st.columns(3)
    for idx, tool in enumerate(tools):
        with cols[idx % 3]:
            st.markdown(f"**{tool['name']}**")
            st.caption(tool["description"])
            with st.expander("Schema"):
                st.json(tool["inputSchema"])
except Exception as exc:
    st.error(f"Could not discover MCP tools: {type(exc).__name__}")

st.divider()
st.subheader("Chat & Operator Console")
default_prompt = (
    "Check if our inventory in Seattle has enough stock of SKU-90210 to fulfill order #4492, "
    "verify if rainfall there will delay ground dispatch today, and calculate the total shipping "
    "insurance cost at 3.5% of the order value."
)
prompt = st.text_area("Ask the operations assistant", value=default_prompt, height=120)
if st.button("Run autonomous workflow", type="primary"):
    with st.spinner("Running MCP tool workflow..."):
        result = asyncio.run(AgentLoop().run(prompt, force_demo=not use_openai))
    st.session_state["last_result"] = result

result = st.session_state.get("last_result")
if result:
    st.success(f"Mode: {result['mode']}")
    st.markdown("### Live Tool Call Timeline")
    for i, step in enumerate(result["steps"], start=1):
        with st.expander(f"Step {i}: {step['tool']} — {step['latency_ms']:.1f} ms", expanded=True):
            st.write("Arguments")
            st.json(step["arguments"])
            st.write("Raw MCP tool return")
            st.code(step["result"])
    st.markdown("### Grounded Answer")
    st.write(result["answer"])

st.divider()
st.subheader("Security Test Workbench")
left, right = st.columns(2)
with left:
    st.markdown("**Adversarial SQL Probe**")
    st.code("SELECT * FROM orders; DROP TABLE inventory;--")
    if st.button("Run SQL attack"):
        attack = asyncio.run(client.call_tool("query_sql_database", {"sql_query": "SELECT * FROM orders; DROP TABLE inventory;--"}))
        st.code(attack)
with right:
    st.markdown("**Math Sandbox Injection Probe**")
    st.code("__import__('os').listdir('.')")
    if st.button("Run math attack"):
        attack = asyncio.run(client.call_tool("evaluate_math_expression", {"expression": "__import__('os').listdir('.')"}))
        st.code(attack)
