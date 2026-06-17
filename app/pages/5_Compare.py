import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
from app.components.styles import inject_css
from app.components.charts import comparison_bar_chart

st.set_page_config(page_title="Compare · RAG Eval", page_icon="⚖️", layout="wide")
inject_css()

st.markdown("""
<div style="padding: 1.5rem 0 1rem;">
    <span class="tag">Benchmarking</span>
    <h2 style="font-size: 1.9rem; font-weight: 800; color: #F9FAFB; margin: 0.5rem 0 0.2rem;
               letter-spacing: -0.02em;">Model Comparison</h2>
    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">Side-by-side performance across runs</p>
</div>
""", unsafe_allow_html=True)

history = st.session_state.get("eval_history", [])

if len(history) < 1:
    st.markdown("<div class='info-box'>Run evaluations first to compare. Showing demo data.</div>", unsafe_allow_html=True)
    history = [
        {"run_name":"llama-3.3-70b","model_name":"llama-3.3-70b-versatile","avg_faithfulness":0.87,"avg_answer_relevancy":0.83,"avg_context_precision":0.79,"avg_context_recall":0.75,"avg_hallucination_rate":0.13,"avg_overall_score":0.82},
        {"run_name":"llama-3.1-8b", "model_name":"llama-3.1-8b-instant",   "avg_faithfulness":0.74,"avg_answer_relevancy":0.70,"avg_context_precision":0.66,"avg_context_recall":0.63,"avg_hallucination_rate":0.26,"avg_overall_score":0.69},
        {"run_name":"mixtral-8x7b", "model_name":"mixtral-8x7b-32768",     "avg_faithfulness":0.79,"avg_answer_relevancy":0.74,"avg_context_precision":0.71,"avg_context_recall":0.68,"avg_hallucination_rate":0.21,"avg_overall_score":0.74},
    ]

with st.sidebar:
    st.markdown("### Select Runs")
    names    = [r["run_name"] for r in history]
    selected = st.multiselect("Runs", names, default=names[:min(3,len(names))])

runs = [r for r in history if r["run_name"] in selected]
if not runs:
    st.warning("Select at least one run.")
    st.stop()

# ── Scoreboard ──
st.markdown("<div class='section-header'>Scoreboard</div>", unsafe_allow_html=True)
COLS = [
    ("avg_faithfulness",    "Faithfulness",  "#22C55E"),
    ("avg_answer_relevancy","Relevancy",     "#6366F1"),
    ("avg_context_precision","Ctx Precision","#F59E0B"),
    ("avg_context_recall",  "Ctx Recall",    "#EC4899"),
    ("avg_hallucination_rate","Hallucin↓",   "#EF4444"),
    ("avg_overall_score",   "Overall",       "#818CF8"),
]

cols = st.columns(len(runs))
for col, run in zip(cols, runs):
    with col:
        st.markdown(f"""
        <div style="background:#16161C; border:1px solid #2A2A35; border-radius:14px;
                    padding:1.1rem; text-align:center; margin-bottom:0.5rem;">
            <div style="font-size:0.82rem; font-weight:700; color:#F1F0FF;
                        margin-bottom:0.75rem; word-break:break-word;">{run['run_name']}</div>
        """, unsafe_allow_html=True)
        for key, label, color in COLS:
            val = run.get(key, 0)
            inv = key == "avg_hallucination_rate"
            display = 1 - val if inv else val
            c = color if display >= 0.7 else "#F59E0B" if display >= 0.5 else "#EF4444"
            st.markdown(f"""
            <div style="margin-bottom:0.55rem;">
                <div style="font-size:0.68rem; color:#6B7280; letter-spacing:0.06em; text-transform:uppercase;">{label}</div>
                <div style="font-size:1rem; font-weight:800; color:{c};
                            font-family:'JetBrains Mono',monospace;">{val:.1%}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ── Bar chart ──
st.markdown("<div class='section-header'>Bar Comparison</div>", unsafe_allow_html=True)
st.plotly_chart(comparison_bar_chart(runs), use_container_width=True)

# ── Radar overlay ──
st.markdown("<div class='section-header'>Radar Overlay</div>", unsafe_allow_html=True)
COLORS = ["#6366F1","#22C55E","#F59E0B","#EC4899","#EF4444"]
labels = ["Faithfulness","Relevancy","Ctx Precision","Ctx Recall","Trust"]

fig = go.Figure()
for run, color in zip(runs, COLORS):
    vals = [
        run.get("avg_faithfulness",0),
        run.get("avg_answer_relevancy",0),
        run.get("avg_context_precision",0),
        run.get("avg_context_recall",0),
        1 - run.get("avg_hallucination_rate",0),
    ]
    v = vals + [vals[0]]; l = labels + [labels[0]]
    r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    fig.add_trace(go.Scatterpolar(
        r=v, theta=l, fill="toself",
        fillcolor=f"rgba({r},{g},{b},0.1)",
        line=dict(color=color, width=2),
        name=run["run_name"],
    ))

fig.update_layout(
    paper_bgcolor="#0C0C0F",
    polar=dict(
        bgcolor="#16161C",
        radialaxis=dict(visible=True, range=[0,1], gridcolor="#2A2A35", tickfont=dict(size=10,color="#6B7280")),
        angularaxis=dict(gridcolor="#2A2A35", tickfont=dict(size=11,color="#D1D5DB")),
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9CA3AF",size=11)),
    margin=dict(l=20,r=20,t=20,b=20), height=420,
)
st.plotly_chart(fig, use_container_width=True)

# ── Winner cards ──
if len(runs) > 1:
    st.markdown("<div class='section-header'>Winners</div>", unsafe_allow_html=True)
    best  = max(runs, key=lambda x: x.get("avg_overall_score",0))
    safest= min(runs, key=lambda x: x.get("avg_hallucination_rate",1))
    faith = max(runs, key=lambda x: x.get("avg_faithfulness",0))
    w1,w2,w3 = st.columns(3)
    for col,(icon,title,run,note_key,better) in zip([w1,w2,w3],[
        ("🏆","Best Overall",     best,  "avg_overall_score",    True),
        ("🛡️","Least Hallucination",safest,"avg_hallucination_rate",False),
        ("✓", "Most Faithful",   faith, "avg_faithfulness",     True),
    ]):
        val = run.get(note_key,0)
        disp = 1-val if not better else val
        color = "#22C55E" if disp >= 0.7 else "#F59E0B"
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; border-color:rgba(99,102,241,0.3);">
                <div style="font-size:1.6rem; margin-bottom:0.3rem;">{icon}</div>
                <div class="metric-label">{title}</div>
                <div style="font-size:1rem; font-weight:800; color:{color}; margin-top:0.2rem;">
                    {run['run_name']}
                </div>
                <div class="metric-delta">{val:.1%}</div>
            </div>""", unsafe_allow_html=True)
