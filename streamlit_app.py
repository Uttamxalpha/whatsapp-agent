import base64
import logging

import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERDICT_COLORS: dict[str, str] = {
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

    /* 🔥 MAIN GITHUB BUTTON */
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

# 🔥 GITHUB HERO BAR
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
st.caption("AI-powered WhatsApp Fact Checker • RAG • LLM • Real-time Verification")

with st.sidebar:
    st.header("Settings")
    api_base = st.text_input("API Base URL", value="http://localhost:8000")
    st.divider()
    st.header("How to use")
    st.markdown(
        "1. Paste a WhatsApp forward in the **Text** tab\n"
        "2. Upload a screenshot in the **Image** tab\n"
        "3. Enter a URL in the **URL** tab\n"
        "4. Click **Check** to fact-check the content"
    )

tab_text, tab_image, tab_url = st.tabs(["Text", "Image", "URL"])


def display_results(data: dict) -> None:
    verdict = data.get("verdict", "UNVERIFIABLE")
    confidence = data.get("confidence", 0.0)
    explanation = data.get("explanation", "")
    claim_results = data.get("claim_results", [])
    sources = data.get("sources", [])
    processing_time_ms = data.get("processing_time_ms", 0)

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
                cr_color = VERDICT_COLORS.get(cr.get("verdict", ""), "#6b7280")
                st.markdown(f"**Claim {i}:** {cr.get('claim', '')}")
                st.markdown(
                    f'<span style="color: {cr_color}; font-weight: bold;">'
                    f'{cr.get("verdict", "")}</span> '
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

with tab_text:
    text_input = st.text_area("Paste the WhatsApp forward here", height=150)
    if st.button("Check Text", key="btn_text"):
        if not text_input.strip():
            st.warning("Please enter some text to check.")
        else:
            with st.spinner("Fact-checking..."):
                try:
                    resp = requests.post(
                        f"{api_base}/api/v1/check/text",
                        json={"text": text_input},
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        display_results(resp.json())
                    else:
                        st.error(f"API error ({resp.status_code}): {resp.text}")
                except requests.exceptions.RequestException as exc:
                    st.error(f"Failed to connect to API: {exc}")


with tab_image:
    uploaded_file = st.file_uploader("Upload screenshot", type=["jpg", "jpeg", "png"])
    if st.button("Check Image", key="btn_image"):
        if uploaded_file is None:
            st.warning("Please upload an image first.")
        else:
            with st.spinner("Fact-checking..."):
                try:
                    resp = requests.post(
                        f"{api_base}/api/v1/check/image",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        display_results(resp.json())
                    else:
                        st.error(f"API error ({resp.status_code}): {resp.text}")
                except requests.exceptions.RequestException as exc:
                    st.error(f"Failed to connect to API: {exc}")


with tab_url:
    url_input = st.text_input("Enter URL")
    if st.button("Check URL", key="btn_url"):
        if not url_input.strip():
            st.warning("Please enter a URL to check.")
        else:
            with st.spinner("Fact-checking..."):
                try:
                    resp = requests.post(
                        f"{api_base}/api/v1/check",
                        json={"input_type": "url", "content": url_input},
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        display_results(resp.json())
                    else:
                        st.error(f"API error ({resp.status_code}): {resp.text}")
                except requests.exceptions.RequestException as exc:
                    st.error(f"Failed to connect to API: {exc}")


# FOOTER
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