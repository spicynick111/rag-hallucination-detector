import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
from app.components.styles import inject_css, verdict_badge, score_pill
from app.components.charts import radar_chart, gauge_chart, metric_trend_chart

st.set_page_config(page_title="Dashboard · RAG Eval", page_icon="📊", layout="wide")
inject_css()

st.markdown("""
<div style="padding: 1.5rem 0 1rem;">
    <span class="tag">Overview</span>
    <h2 style="font-size: 1.9rem; font-weight: 800; color: #F9FAFB; margin: 0.5rem 0 0.2rem;
               letter-spacing: -0.02em;">Evaluation Dashboard</h2>
    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">Aggregate metrics for the latest evaluation run</p>
</div>
""", unsafe_allow_html=True)

results = st.session_state.get("eval_results")
history = st.session_state.get("eval_history", [])

if not results:
    st.markdown("""
    <div class="info-box">
        No evaluation run yet — go to <strong>Evaluate</strong> page and click Run Evaluation.
        Showing demo data below.
    </div>""", unsafe_allow_html=True)

    demo = {"faithfulness":0.82,"answer_relevancy":0.76,"context_precision":0.71,
            "context_recall":0.68,"hallucination_rate":0.18,"overall_score":0.75}

    st.markdown("<div class='section-header'>Demo Metrics</div>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col,(label,key,color) in zip([c1,c2,c3,c4,c5,c6],[
        ("Faithfulness","faithfulness","#22C55E"),
        ("Relevancy","answer_relevancy","#6366F1"),
        ("Ctx Precision","context_precision","#F59E0B"),
        ("Ctx Recall","context_recall","#EC4899"),
        ("Hallucination↓","hallucination_rate","#EF4444"),
        ("Overall","overall_score","#818CF8"),
    ]):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{demo[key]:.0%}</div>
                <div class="metric-delta">demo data</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Performance Radar (Demo)</div>", unsafe_allow_html=True)
    st.plotly_chart(radar_chart(demo, "Sample RAG Pipeline"), use_container_width=True)
    st.stop()

agg     = results.get("aggregate_metrics", {})
samples = results.get("samples", [])
run_nm  = results.get("run_name","—")

# ── Metric row ──
st.markdown("<div class='section-header'>Metrics</div>", unsafe_allow_html=True)
c1,c2,c3,c4,c5,c6 = st.columns(6)
for col,(label,key,color) in zip([c1,c2,c3,c4,c5,c6],[
    ("Faithfulness","faithfulness","#22C55E"),
    ("Relevancy","answer_relevancy","#6366F1"),
    ("Ctx Precision","context_precision","#F59E0B"),
    ("Ctx Recall","context_recall","#EC4899"),
    ("Hallucination↓","hallucination_rate","#EF4444"),
    ("Overall","overall_score","#818CF8"),
]):
    with col:
        val = agg.get(key,0)
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{val:.0%}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns([1,1])

with left:
    st.markdown("<div class='section-header'>Radar Chart</div>", unsafe_allow_html=True)
    st.plotly_chart(radar_chart(agg, run_nm), use_container_width=True)

with right:
    st.markdown("<div class='section-header'>Gauges</div>", unsafe_allow_html=True)
    g1,g2 = st.columns(2)
    with g1:
        st.plotly_chart(gauge_chart(agg.get("faithfulness",0), "Faithfulness", "#22C55E"), use_container_width=True)
        st.plotly_chart(gauge_chart(agg.get("context_precision",0), "Ctx Precision", "#F59E0B"), use_container_width=True)
    with g2:
        st.plotly_chart(gauge_chart(agg.get("answer_relevancy",0), "Relevancy", "#6366F1"), use_container_width=True)
        st.plotly_chart(gauge_chart(1-agg.get("hallucination_rate",0), "Trust Score", "#22C55E"), use_container_width=True)

if len(history) > 1:
    st.markdown("<div class='section-header'>Trend</div>", unsafe_allow_html=True)
    st.plotly_chart(metric_trend_chart(history), use_container_width=True)

if samples:
    st.markdown("<div class='section-header'>Sample Results</div>", unsafe_allow_html=True)
    rows = []
    for s in samples:
        verdict = s.get("llm_judge_verdict","—")
        rows.append({
            "Question": s["question"][:80]+"…" if len(s["question"])>80 else s["question"],
            "Faithfulness": f"{s.get('faithfulness',0):.0%}",
            "Relevancy":    f"{s.get('answer_relevancy',0):.0%}",
            "Hallucination":f"{s.get('hallucination_rate',0):.0%}",
            "Verdict":      verdict,
            "Flag":         "⚠️" if s.get("is_hallucinated") else "✓",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
