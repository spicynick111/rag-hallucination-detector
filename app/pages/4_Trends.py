import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
from app.components.styles import inject_css
from app.components.charts import metric_trend_chart, comparison_bar_chart

st.set_page_config(page_title="Trends · RAG Eval", page_icon="📈", layout="wide")
inject_css()

st.markdown("""
<div style="padding: 1.5rem 0 1rem;">
    <span class="tag">Historical Analysis</span>
    <h2 style="font-size: 1.9rem; font-weight: 800; color: #F9FAFB; margin: 0.5rem 0 0.2rem;
               letter-spacing: -0.02em;">Metric Trends</h2>
    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">Track evaluation quality across runs over time</p>
</div>
""", unsafe_allow_html=True)

history = st.session_state.get("eval_history", [])

if len(history) < 2:
    st.markdown("<div class='info-box'>Run at least 2 evaluations to see trends. Showing demo data.</div>", unsafe_allow_html=True)
    random.seed(0)
    base = datetime.utcnow() - timedelta(days=14)
    history = [{
        "run_name": f"run-{i+1:02d}",
        "model_name": "llama-3.3-70b-versatile",
        "created_at": (base + timedelta(days=i*1.5)).isoformat(),
        "avg_faithfulness":     min(1, 0.60 + i*0.022 + random.uniform(-0.04,0.04)),
        "avg_answer_relevancy": min(1, 0.55 + i*0.020 + random.uniform(-0.04,0.04)),
        "avg_context_precision":min(1, 0.52 + i*0.018 + random.uniform(-0.04,0.04)),
        "avg_context_recall":   min(1, 0.50 + i*0.015 + random.uniform(-0.04,0.04)),
        "avg_hallucination_rate":max(0,0.40 - i*0.022 + random.uniform(-0.03,0.03)),
        "avg_overall_score":    min(1, 0.57 + i*0.019 + random.uniform(-0.03,0.03)),
    } for i in range(10)]

df = pd.DataFrame(history)
df["created_at"] = pd.to_datetime(df["created_at"])
latest  = df.iloc[-1]
oldest  = df.iloc[0]

# ── Stats ──
c1,c2,c3,c4 = st.columns(4)
with c1:
    d = latest.get("avg_faithfulness",0) - oldest.get("avg_faithfulness",0)
    st.metric("Latest Faithfulness", f"{latest.get('avg_faithfulness',0):.1%}", f"{d:+.1%}")
with c2:
    d = latest.get("avg_answer_relevancy",0) - oldest.get("avg_answer_relevancy",0)
    st.metric("Latest Relevancy", f"{latest.get('avg_answer_relevancy',0):.1%}", f"{d:+.1%}")
with c3:
    d = latest.get("avg_hallucination_rate",0) - oldest.get("avg_hallucination_rate",0)
    st.metric("Hallucination Rate", f"{latest.get('avg_hallucination_rate',0):.1%}", f"{d:+.1%}", delta_color="inverse")
with c4:
    st.metric("Total Runs", len(df))

st.markdown("<div class='section-header'>Trend Chart</div>", unsafe_allow_html=True)
st.plotly_chart(metric_trend_chart(history), use_container_width=True)

st.markdown("<div class='section-header'>Run History</div>", unsafe_allow_html=True)
disp = df.copy()
for col in ["avg_faithfulness","avg_answer_relevancy","avg_context_precision","avg_context_recall","avg_hallucination_rate","avg_overall_score"]:
    if col in disp.columns:
        disp[col] = disp[col].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "—")
disp["created_at"] = disp["created_at"].dt.strftime("%Y-%m-%d %H:%M")
st.dataframe(
    disp[["run_name","model_name","created_at","avg_faithfulness","avg_answer_relevancy","avg_hallucination_rate","avg_overall_score"]].rename(columns={
        "run_name":"Run","model_name":"Model","created_at":"Date",
        "avg_faithfulness":"Faithfulness","avg_answer_relevancy":"Relevancy",
        "avg_hallucination_rate":"Hallucination↓","avg_overall_score":"Score",
    }),
    use_container_width=True, hide_index=True,
)

# ── Best vs Worst ──
if "avg_overall_score" in df.columns and len(df) > 1:
    st.markdown("<div class='section-header'>Best vs Worst Run</div>", unsafe_allow_html=True)
    best  = df.loc[df["avg_overall_score"].idxmax()].to_dict()
    worst = df.loc[df["avg_overall_score"].idxmin()].to_dict()
    b1,b2 = st.columns(2)
    with b1:
        st.markdown(f"""
        <div class="metric-card" style="border-color: rgba(34,197,94,0.35);">
            <div class="metric-label">🏆 Best Run</div>
            <div style="font-size:1.15rem; font-weight:800; color:#22C55E;">{best.get('run_name','')}</div>
            <div class="metric-delta">Score: {float(best.get('avg_overall_score',0)):.1%}</div>
        </div>""", unsafe_allow_html=True)
    with b2:
        st.markdown(f"""
        <div class="metric-card" style="border-color: rgba(239,68,68,0.35);">
            <div class="metric-label">⚠ Worst Run</div>
            <div style="font-size:1.15rem; font-weight:800; color:#EF4444;">{worst.get('run_name','')}</div>
            <div class="metric-delta">Score: {float(worst.get('avg_overall_score',0)):.1%}</div>
        </div>""", unsafe_allow_html=True)
    st.plotly_chart(comparison_bar_chart([best, worst]), use_container_width=True)
