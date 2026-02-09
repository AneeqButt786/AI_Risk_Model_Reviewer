"""Risk Model Reviewer - Streamlit App. Run with: streamlit run app.py"""

import asyncio
import time
import streamlit as st
from agents import Runner, set_default_openai_key
from openai.types.responses import ResponseTextDeltaEvent
from config import get_config
from agent_defs import risk_reviewer
from utils.logging import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="AI Risk Model Reviewer", layout="wide")

try:
    cfg = get_config()
    set_default_openai_key(cfg["openai_api_key"])
except ValueError as e:
    st.error(str(e))
    st.stop()

st.title("AI Risk Model Reviewer")
st.sidebar.markdown("**Capabilities**")
st.sidebar.markdown("- Model type, features, and structure")
st.sidebar.markdown("- Fairness (disparate impact, bias)")
st.sidebar.markdown("- Compliance: ECOA, FCRA, GDPR, SR 11-7")
st.sidebar.markdown("- Human-readable explanations and audit trail")

model_input = st.text_area(
    "Paste model summary or description",
    height=150,
    placeholder="e.g. Credit scoring model, XGBoost, features: Income, Age, Employment Length, target: Loan Approval…",
)
review_btn = st.button("Review", type="primary")

if review_btn:
    user_content = (model_input or "").strip()
    if not user_content:
        st.warning("Please describe the risk model to review.")
    else:
        response_placeholder = st.empty()
        accumulated = ""

        async def collect_stream():
            result = Runner.run_streamed(risk_reviewer, input=user_content)
            chunks = []
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    chunks.append(event.data.delta or "")
                await asyncio.sleep(0.01)
            return chunks

        with st.spinner("Reviewing model..."):
            try:
                logger.info("Processing: %s", user_content[:80])
                chunks = asyncio.run(collect_stream())
                for ch in chunks:
                    accumulated += ch
                    response_placeholder.markdown(accumulated)
                    time.sleep(0.01)
                logger.info("Response sent")
            except Exception:
                logger.exception("Query failed")
                response_placeholder.markdown("Something went wrong. Please try again.")
