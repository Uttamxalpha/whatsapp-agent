import asyncio
import base64
import logging
import time

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agents.graph import compiled_graph
from rag.corpus_loader import load_corpus

if "corpus_loaded" not in st.session_state:
    load_corpus()
    st.session_state.corpus_loaded = True

VERDICT_COLORS = {
    "TRUE": "#22c55e",
    "FALSE": "#ef4444",
    "MISLEADING": "#f97316",
    "UNVERIFIABLE": "#6b7280",
}

st.set_page_config(
    page_title="Misinfo Buster - WhatsApp Fact Checker",
    layout="wide",
)

st.markdown(
    """
    <style>
    .verdict-badge {
        display: inline-block;
        padding: 10px 26px;
        border-radius: 10px;
        color: white;
        font-size: 1.6rem;
        font-weight: bold;
        margin: 12px 0;
    }

    .stApp {
        max-width: 950px;
        margin: 0 auto;
    }

    .social-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px;
        border-radius: 12px;
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(6px);
        margin-bottom: 10px;
    }

    .github-main {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        color: #fff;
        padding: 10px 18px;
        border-radius: 10px;
        background: linear-gradient(135deg, #111, #333);
        transition: all 0.25s ease;
    }

    .github-main:hover {
        transform: translateY(-2px) scale(1.03);
        background: linear-gradient(135deg, #000, #555);
    }

    .github-main img {
        width: 24px;
        height: 24px;
        filter: invert(1);
    }

    .social-secondary {
        display: flex;
        gap: 14px;
    }

    .social-secondary a {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 8px;
        border-radius: 8px;
        transition: 0.2s;
    }

    .social-secondary a:hover {
        background: rgba(255,255,255,0.08);
        transform: scale(1.1);
    }

    .social-secondary img {
        width: 22px;
        height: 22px;
    }

    .footer {
        text-align: center;
        padding: 30px 0 10px 0;
        color: #888;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="social-bar">
        <a href="https://github.com/Uttamxalpha" target="_blank" class="github-main">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" />
            <span>View Project on GitHub</span>
        </a>
        <div class="social-secondary">
            <a href="https://www.linkedin.com/in/uttam-tiwari-097025273/" target="_blank">
                <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg" />
            </a>
            <a href="mailto:uttamt2006@gmail.com">
                <img src="https://www.gstatic.com/images/icons/material/product/2x/gmail_48dp.png" />
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Misinfo Buster")
st.caption("AI-powered WhatsApp Fact Checker - RAG - LLM - Real-time Verification")

with st.sidebar:
    st.header("How to use")
    st.markdown(
        "1. Paste a WhatsApp forward in the **Text** tab\n"
        "2. Upload a screenshot in the **Image** tab\n"
        "3. Enter a URL in the **URL** tab\n"
        "4. Click **Check** to fact-check the content"
    )


def build_initial_state(input_type, content):
    """Build a minimal AgentState dict for graph invocation."""
    return {
        "input_type": input_type,
        "raw_input": content,
        "extracted_text": "",
        "detected_language": "",
        "claims": [],
        "claim_results": [],
        "verdict": "",
        "confidence": 0.0,
        "explanation": "",
        "sources": [],
        "processing_time_ms": 0,
        "error": None,
    }


def run_pipeline(input_type, content):
    """Run the LangGraph pipeline directly and return the result dict."""
    initial_state = build_initial_state(input_type, content)
    start_time = time.time()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(compiled_graph.ainvoke(initial_state))
    loop.close()
    processing_time_ms = int((time.time() - start_time) * 1000)
    result["processing_time_ms"] = processing_time_ms
    return result


def display_results(data):
    """Display fact-check results with verdict badge and claim breakdown."""
    verdict = data.get("verdict", "UNVERIFIABLE")
    confidence = data.get("confidence", 0.0)
    explanation = data.get("explanation", "")
    claim_results = data.get("claim_results", [])
    sources = data.get("sources", [])
    processing_time_ms = data.get("processing_time_ms", 0)

    if data.get("error"):
        st.error(f"Pipeline error: {data['error']}")
        return

    color = VERDICT_COLORS.get(verdict, "#6b7280")
    st.markdown(
        f'<div class="verdict-badge" style="background-color: {color};">{verdict}</div>',
        unsafe_allow_html=True,
    )

    st.progress(confidence, text=f"Confidence: {confidence:.0%}")
    st.write(explanation)

    if claim_results:
        with st.expander("Claim-by-claim breakdown"):
            for i, cr in enumerate(claim_results, 1):
                cr_verdict = cr.get("sub_verdict", cr.get("verdict", ""))
                cr_color = VERDICT_COLORS.get(cr_verdict, "#6b7280")
                st.markdown(f"**Claim {i}:** {cr.get('claim', '')}")
                st.markdown(
                    f'<span style="color: {cr_color}; font-weight: bold;">'
                    f'{cr_verdict}</span> '
                    f'(confidence: {cr.get("confidence", 0.0):.0%})',
                    unsafe_allow_html=True,
                )
                st.write(cr.get("evidence_summary", ""))
                if cr.get("sources"):
                    for src in cr["sources"]:
                        st.markdown(f"- [{src}]({src})")
                st.divider()

    if sources:
        with st.expander("Sources"):
            for src in sources:
                st.markdown(f"- [{src}]({src})")

    st.caption(f"Processed in {processing_time_ms}ms")


tab_text, tab_image, tab_url = st.tabs(["Text", "Image", "URL"])

with tab_text:
    text_input = st.text_area("Paste the WhatsApp forward here", height=150)
    if st.button("Check Text", key="btn_text"):
        if not text_input.strip():
            st.warning("Please enter some text to check.")
        else:
            with st.spinner("Fact-checking..."):
                try:
                    result = run_pipeline("text", text_input)
                    display_results(result)
                except Exception as exc:
                    st.error(f"Error: {exc}")

with tab_image:
    uploaded_file = st.file_uploader("Upload screenshot", type=["jpg", "jpeg", "png"])
    if st.button("Check Image", key="btn_image"):
        if uploaded_file is None:
            st.warning("Please upload an image first.")
        else:
            with st.spinner("Fact-checking..."):
                try:
                    b64_content = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                    result = run_pipeline("image", b64_content)
                    display_results(result)
                except Exception as exc:
                    st.error(f"Error: {exc}")

with tab_url:
    url_input = st.text_input("Enter URL")
    if st.button("Check URL", key="btn_url"):
        if not url_input.strip():
            st.warning("Please enter a URL to check.")
        else:
            with st.spinner("Fact-checking..."):
                try:
                    result = run_pipeline("url", url_input)
                    display_results(result)
                except Exception as exc:
                    st.error(f"Error: {exc}")

st.markdown("---")
st.markdown(
    """
    <div class="footer">
        made with <span style="color: #ef4444;">&hearts;</span> by uttam
        <br/>
        <div style="margin-top: 8px;">
            <a href="https://github.com/Uttamxalpha" target="_blank" style="color:#aaa;text-decoration:none;margin:0 8px;">
                GitHub
            </a>
            <a href="https://www.linkedin.com/in/uttam-tiwari-097025273/" target="_blank" style="color:#aaa;text-decoration:none;margin:0 8px;">
                LinkedIn
            </a>
            <a href="mailto:uttamt2006@gmail.com" style="color:#aaa;text-decoration:none;margin:0 8px;">
                Gmail
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)