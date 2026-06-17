import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.components.styles import inject_css

st.set_page_config(
    page_title="RAG Eval — Hallucination Detector",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Hero ──
st.markdown("""
<div style="padding: 3rem 0 2rem; text-align: center; position: relative;">
    <div style="display:inline-block; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.25);
                border-radius: 99px; padding: 0.3rem 1rem; font-size: 0.72rem; font-weight: 700;
                color: #818CF8; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 1.2rem;">
        LLMOps · RAG Evaluation · Hallucination Detection
    </div>
    <h1 style="font-size: 3rem; font-weight: 800; color: #F9FAFB; margin: 0 0 0.75rem;
               letter-spacing: -0.03em; line-height: 1.1;">
        RAG Hallucination<br>
        <span style="background: linear-gradient(135deg, #6366F1, #EC4899);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                     background-clip: text;">Detection Framework</span>
    </h1>
    <p style="color: #6B7280; font-size: 1rem; max-width: 560px; margin: 0 auto;
              line-height: 1.7;">
        Evaluate your RAG pipeline's output quality — faithfulness scoring,
        hallucination detection, and LLMOps metrics in one dashboard.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Feature cards ──
c1, c2, c3, c4 = st.columns(4)
features = [
    ("🔬", "Evaluate", "Run Q&A datasets through the evaluation engine with live Groq LLM judging"),
    ("🌡️", "Heatmap", "See hallucination intensity per sample — instantly spot weak answers"),
    ("📈", "Trends", "Track faithfulness & hallucination rate across multiple evaluation runs"),
    ("⚖️", "Compare", "Side-by-side model benchmarking with radar charts and scorecards"),
]
for col, (icon, title, desc) in zip([c1, c2, c3, c4], features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <span class="icon">{icon}</span>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── How it works ──
st.markdown("<div class='section-header'>How It Works</div>", unsafe_allow_html=True)
h1, h2, h3, h4 = st.columns(4)
steps = [
    ("01", "Input", "Provide Q&A pairs manually, upload CSV, or use the built-in RAG simulator"),
    ("02", "Retrieve", "Built-in RAG pipeline retrieves relevant context chunks per question"),
    ("03", "Judge", "Llama 3.3 70B via Groq evaluates each answer for faithfulness & hallucinations"),
    ("04", "Dashboard", "View scores, heatmaps, trends and export full evaluation reports"),
]
for col, (num, title, desc) in zip([h1, h2, h3, h4], steps):
    with col:
        st.markdown(f"""
        <div style="padding: 1.2rem; background: #16161C; border: 1px solid #2A2A35;
                    border-radius: 14px; height: 100%;">
            <div style="font-size: 0.72rem; font-weight: 800; color: #6366F1;
                        letter-spacing: 0.12em; margin-bottom: 0.5rem;">{num}</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #E5E7EB;
                        margin-bottom: 0.4rem;">{title}</div>
            <div style="font-size: 0.8rem; color: #6B7280; line-height: 1.55;">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Metrics reference ──
with st.expander("📐 Metrics Reference", expanded=False):
    mc1, mc2, mc3 = st.columns(3)
    metrics_info = [
        ("Faithfulness", "#22C55E", "Are all claims in the answer grounded in retrieved context? 1.0 = perfectly faithful."),
        ("Answer Relevancy", "#6366F1", "Does the answer actually address the question asked?"),
        ("Context Precision", "#F59E0B", "How relevant are the retrieved chunks to the question?"),
        ("Context Recall", "#EC4899", "Does the context cover all information needed to answer?"),
        ("Hallucination Rate", "#EF4444", "Fraction of the answer NOT supported by context. Lower is better."),
        ("Overall Score", "#818CF8", "Weighted average of all metrics. Above 0.75 is production-ready."),
    ]
    for i, (name, color, desc) in enumerate(metrics_info):
        col = [mc1, mc2, mc3][i % 3]
        with col:
            st.markdown(f"""
            <div style="background:#16161C; border:1px solid #2A2A35; border-left:3px solid {color};
                        border-radius:10px; padding:0.85rem 1rem; margin-bottom:0.6rem;">
                <div style="font-size:0.82rem; font-weight:700; color:{color}; margin-bottom:0.3rem;">{name}</div>
                <div style="font-size:0.78rem; color:#6B7280; line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

# ── System status ──
st.markdown("<div class='section-header'>System Status</div>", unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)

from config.settings import GROQ_API_KEY

with s1:
    ok = bool(GROQ_API_KEY and GROQ_API_KEY.startswith("gsk_"))
    dot = "🟢" if ok else "🔴"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Groq API</div>
        <div style="font-size:1.05rem; font-weight:700; color:{'#22C55E' if ok else '#EF4444'};">
            {dot} {'Connected — Free Tier' if ok else 'Missing — add to .env'}
        </div>
        <div class="metric-delta">Llama 3.3 70B · 6,000 req/day free</div>
    </div>""", unsafe_allow_html=True)

with s2:
    try:
        from backend.database.connection import check_db_connection
        db_ok = check_db_connection()
    except Exception:
        db_ok = False
    dot = "🟢" if db_ok else "🟡"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">PostgreSQL</div>
        <div style="font-size:1.05rem; font-weight:700; color:{'#22C55E' if db_ok else '#F59E0B'};">
            {dot} {'Connected' if db_ok else 'Offline — running in demo mode'}
        </div>
        <div class="metric-delta">Results stored in session when offline</div>
    </div>""", unsafe_allow_html=True)

with s3:
    runs = len(st.session_state.get("eval_history", []))
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Session Runs</div>
        <div style="font-size:1.8rem; font-weight:800; color:#818CF8;
                    font-family:'JetBrains Mono',monospace;">{runs}</div>
        <div class="metric-delta">Evaluations run this session</div>
    </div>""", unsafe_allow_html=True)
