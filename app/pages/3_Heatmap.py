import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from app.components.styles import inject_css, verdict_badge
from app.components.charts import hallucination_heatmap, distribution_histogram

st.set_page_config(page_title="Heatmap · RAG Eval", page_icon="🌡️", layout="wide")
inject_css()

st.markdown("""
<div style="padding: 1.5rem 0 1rem;">
    <span class="tag">Hallucination Analysis</span>
    <h2 style="font-size: 1.9rem; font-weight: 800; color: #F9FAFB; margin: 0.5rem 0 0.2rem;
               letter-spacing: -0.02em;">Hallucination Heatmap</h2>
    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">
        Each cell = 1 sample · Green = faithful · Red = hallucinated
    </p>
</div>
""", unsafe_allow_html=True)

results = st.session_state.get("eval_results")

if not results:
    st.markdown("<div class='info-box'>No evaluation yet — showing synthetic demo data.</div>", unsafe_allow_html=True)
    import random; random.seed(42)
    demo = [{"question":f"Demo Q{i+1}","hallucination_rate":random.uniform(0,1),
             "llm_judge_verdict":random.choice(["FAITHFUL","HALLUCINATED","PARTIALLY_FAITHFUL"])} for i in range(20)]
    st.plotly_chart(hallucination_heatmap(demo), use_container_width=True)
    st.plotly_chart(distribution_histogram(demo, "hallucination_rate"), use_container_width=True)
    st.stop()

samples = results.get("samples", [])

with st.sidebar:
    st.markdown("### 🔍 Filters")
    threshold = st.slider("Hallucination threshold", 0.0, 1.0, 0.3, 0.05)
    verdicts  = st.multiselect("Verdict filter",
        ["FAITHFUL","HALLUCINATED","PARTIALLY_FAITHFUL","UNKNOWN"],
        default=["FAITHFUL","HALLUCINATED","PARTIALLY_FAITHFUL","UNKNOWN"])
    min_hal = st.slider("Min hallucination rate", 0.0, 1.0, 0.0, 0.05)

filtered = [s for s in samples
            if s.get("hallucination_rate",0) >= min_hal
            and s.get("llm_judge_verdict","UNKNOWN") in verdicts]

# ── Stats row ──
c1,c2,c3 = st.columns(3)
total = len(filtered)
hallucinated = sum(1 for s in filtered if s.get("hallucination_rate",0) >= threshold)
avg_hal = sum(s.get("hallucination_rate",0) for s in filtered) / max(total,1)

with c1:
    st.markdown(f"""<div class="metric-card" style="text-align:center;">
        <div class="metric-label">Filtered Samples</div>
        <div class="metric-value" style="color:#818CF8;">{total}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card" style="text-align:center;">
        <div class="metric-label">Hallucinated (≥{threshold:.0%})</div>
        <div class="metric-value" style="color:#EF4444;">{hallucinated}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    col = "#EF4444" if avg_hal >= 0.5 else "#F59E0B" if avg_hal >= 0.3 else "#22C55E"
    st.markdown(f"""<div class="metric-card" style="text-align:center;">
        <div class="metric-label">Avg Hallucination</div>
        <div class="metric-value" style="color:{col};">{avg_hal:.0%}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.plotly_chart(hallucination_heatmap(filtered), use_container_width=True)

col_l, col_r = st.columns([1,1])
with col_l:
    st.markdown("<div class='section-header'>Distribution</div>", unsafe_allow_html=True)
    metric_choice = st.selectbox("Metric", ["hallucination_rate","faithfulness","answer_relevancy","context_precision"])
    st.plotly_chart(distribution_histogram(filtered, metric_choice), use_container_width=True)

with col_r:
    st.markdown("<div class='section-header'>High-Risk Samples</div>", unsafe_allow_html=True)
    high_risk = sorted(filtered, key=lambda x: x.get("hallucination_rate",0), reverse=True)[:8]
    for s in high_risk:
        rate    = s.get("hallucination_rate",0)
        verdict = s.get("llm_judge_verdict","UNKNOWN")
        border  = "#EF4444" if rate >= 0.5 else "#F59E0B" if rate >= 0.3 else "#22C55E"
        st.markdown(f"""
        <div class="sample-card" style="border-left: 3px solid {border};">
            <div style="font-size:0.82rem; color:#D1D5DB; margin-bottom:0.35rem;">
                {s['question'][:75]}{'…' if len(s['question'])>75 else ''}
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                <span style="color:{border}; font-weight:700; font-size:0.8rem;
                             font-family:'JetBrains Mono',monospace;">{rate:.0%}</span>
                {verdict_badge(verdict)}
            </div>
        </div>""", unsafe_allow_html=True)
