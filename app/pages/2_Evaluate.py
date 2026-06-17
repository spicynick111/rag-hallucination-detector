import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import streamlit as st
import pandas as pd
from app.components.styles import inject_css, verdict_badge, score_pill
from backend.evaluator import evaluate_samples
from backend.rag_pipeline import DEMO_SAMPLES, run_rag_pipeline

st.set_page_config(page_title="Evaluate · RAG Eval", page_icon="🔬", layout="wide")
inject_css()

st.markdown("""
<div style="padding: 1.5rem 0 1rem;">
    <span class="tag">Evaluation Engine</span>
    <h2 style="font-size: 1.9rem; font-weight: 800; color: #F9FAFB; margin: 0.5rem 0 0.2rem;
               letter-spacing: -0.02em;">Run Evaluation</h2>
    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">
        Evaluate your RAG pipeline output with Llama 3.3 70B as LLM judge
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### ⚙️ Config")
    run_name = st.text_input("Run Name", value="eval-run-01")
    model_name = st.selectbox(
        "Groq Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        index=0,
        help="All models are FREE on Groq"
    )
    use_llm_judge = st.toggle("Enable LLM Judge", value=True, help="Use Llama 3.3 70B to judge each answer")
    use_rag_sim = st.toggle("RAG Simulator", value=False, help="Auto-generate answers from built-in knowledge base")
    top_k = st.slider("Context chunks (k)", 1, 5, 3) if use_rag_sim else 3
    st.markdown("---")
    st.markdown("### 📂 Input")
    input_mode = st.radio("", ["Demo Dataset", "Manual Input", "Upload CSV/JSON"], label_visibility="collapsed")

samples = []

if input_mode == "Demo Dataset":
    st.markdown("""
    <div class="info-box">
        5 built-in Q&A samples covering RAG, RAGAS, LLMs, hallucinations, and LLMOps.
        Toggle <strong>RAG Simulator</strong> in sidebar to auto-generate answers.
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    df_prev = pd.DataFrame([{"#": i+1, "Question": s["question"], "Ground Truth": s.get("ground_truth","—")} for i, s in enumerate(DEMO_SAMPLES)])
    st.dataframe(df_prev, use_container_width=True, hide_index=True)
    samples = DEMO_SAMPLES

elif input_mode == "Manual Input":
    st.markdown("<div class='section-header'>Add Samples</div>", unsafe_allow_html=True)
    num = st.number_input("Number of samples", 1, 20, 3)
    for i in range(num):
        with st.expander(f"Sample {i+1}", expanded=(i == 0)):
            q   = st.text_area(f"Question",    key=f"q_{i}",   placeholder="Enter question...")
            a   = st.text_area(f"Answer",      key=f"a_{i}",   placeholder="LLM-generated answer...")
            gt  = st.text_input(f"Ground Truth (optional)", key=f"gt_{i}")
            ctx = st.text_area(f"Context chunks (one per line)", key=f"ctx_{i}", placeholder="Paste retrieved context here...")
            if q and a:
                samples.append({
                    "question": q, "answer": a,
                    "ground_truth": gt or None,
                    "contexts": [c.strip() for c in ctx.split("\n") if c.strip()] if ctx else [],
                })

elif input_mode == "Upload CSV/JSON":
    st.markdown("<div class='section-header'>Upload Dataset</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("CSV or JSON file", type=["csv","json"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.DataFrame(json.load(uploaded))
            st.success(f"Loaded {len(df)} rows")
            st.dataframe(df.head(3), use_container_width=True)
            col_q  = st.selectbox("Question column",              df.columns.tolist())
            col_a  = st.selectbox("Answer column",                df.columns.tolist())
            col_gt = st.selectbox("Ground Truth (optional)",      ["—"] + df.columns.tolist())
            col_c  = st.selectbox("Context column (optional)",    ["—"] + df.columns.tolist())
            for _, row in df.iterrows():
                ctx = []
                if col_c != "—":
                    raw = row.get(col_c, "")
                    ctx = [raw] if isinstance(raw, str) else (list(raw) if isinstance(raw, list) else [])
                samples.append({
                    "question": str(row[col_q]), "answer": str(row[col_a]),
                    "ground_truth": str(row[col_gt]) if col_gt != "—" else None,
                    "contexts": ctx,
                })
        except Exception as e:
            st.error(f"Error: {e}")

# ── Run button ──
st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("▶  Run Evaluation", disabled=not bool(samples), use_container_width=True)

if run_btn:
    from config.settings import GROQ_API_KEY
    if not GROQ_API_KEY or not GROQ_API_KEY.startswith("gsk_"):
        st.error("Set GROQ_API_KEY in .env — free key at https://console.groq.com")
        st.stop()

    bar     = st.progress(0, text="Starting...")
    status  = st.empty()

    def update_progress(cur, tot, msg):
        bar.progress(int(cur/max(tot,1)*100), text=msg)

    with st.spinner("Evaluating..."):
        try:
            eval_samples = samples
            if use_rag_sim:
                filled = []
                for s in eval_samples:
                    if not s.get("answer") or not s.get("contexts"):
                        out = run_rag_pipeline(s["question"], top_k=top_k, model=model_name)
                        s["answer"]   = out["answer"]
                        s["contexts"] = out["contexts"]
                    filled.append(s)
                eval_samples = filled

            result = evaluate_samples(
                samples=eval_samples,
                run_name=run_name,
                model_name=model_name,
                use_llm_judge=use_llm_judge,
                progress_callback=update_progress,
            )
            rd = result.to_dict()
            st.session_state["eval_results"] = rd
            if "eval_history" not in st.session_state:
                st.session_state["eval_history"] = []
            st.session_state["eval_history"].append({
                "run_name": run_name, "model_name": model_name,
                "created_at": result.created_at.isoformat(),
                **{f"avg_{k}": v for k, v in result.aggregate_metrics.items()
                   if k not in ("total_samples","hallucinated_count")},
            })
            bar.progress(100, text="Done!")
        except Exception as e:
            st.error(f"Evaluation failed: {e}")
            st.stop()

    # ── Results summary ──
    agg = rd.get("aggregate_metrics", {})
    st.markdown("<div class='section-header'>Summary</div>", unsafe_allow_html=True)

    r1, r2, r3, r4, r5 = st.columns(5)
    for col, (label, key, color) in zip([r1,r2,r3,r4,r5], [
        ("Faithfulness",   "faithfulness",     "#22C55E"),
        ("Relevancy",      "answer_relevancy", "#6366F1"),
        ("Ctx Precision",  "context_precision","#F59E0B"),
        ("Hallucination↓", "hallucination_rate","#EF4444"),
        ("Overall Score",  "overall_score",    "#818CF8"),
    ]):
        val = agg.get(key, 0)
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{val:.0%}</div>
            </div>""", unsafe_allow_html=True)

    hall_ct = agg.get("hallucinated_count", 0)
    total   = agg.get("total_samples", 0)
    st.markdown(f"""
    <div class="info-box" style="margin-top:1rem;">
        ✅ <strong>{total}</strong> samples evaluated in <strong>{result.duration_seconds:.1f}s</strong> —
        <strong style="color:#EF4444;">{hall_ct}</strong> hallucinated
        ({hall_ct/max(total,1):.0%} rate) · Model: <strong>{model_name}</strong>
    </div>""", unsafe_allow_html=True)

    # ── Sample detail ──
    st.markdown("<div class='section-header'>Sample Results</div>", unsafe_allow_html=True)
    for i, s in enumerate(rd.get("samples",[])):
        verdict = s.get("llm_judge_verdict","UNKNOWN")
        hal     = s.get("hallucination_rate", 0)
        border  = "#EF4444" if hal >= 0.5 else "#F59E0B" if hal >= 0.3 else "#22C55E"
        with st.expander(f"#{i+1}  {s['question'][:65]}{'...' if len(s['question'])>65 else ''}  —  Hallucination {hal:.0%}", expanded=False):
            left, right = st.columns([3,1])
            with left:
                st.markdown(f"**Question:** {s['question']}")
                st.markdown(f"**Answer:** {s['answer']}")
                if s.get("ground_truth"):
                    st.markdown(f"**Ground Truth:** {s['ground_truth']}")
                if s.get("llm_judge_reasoning"):
                    st.markdown(f"> *{s['llm_judge_reasoning'][:300]}*")
            with right:
                st.markdown(f"**Verdict** {verdict_badge(verdict)}", unsafe_allow_html=True)
                st.metric("Faithfulness",   f"{s.get('faithfulness',0):.1%}")
                st.metric("Relevancy",      f"{s.get('answer_relevancy',0):.1%}")
                st.metric("Hallucination",  f"{s.get('hallucination_rate',0):.1%}")

    # ── Export ──
    st.markdown("<div class='section-header'>Export</div>", unsafe_allow_html=True)
    e1, e2 = st.columns(2)
    df_exp = pd.DataFrame(rd["samples"])
    with e1:
        st.download_button("⬇ Download CSV",  df_exp.to_csv(index=False),  f"{run_name}.csv",  "text/csv")
    with e2:
        st.download_button("⬇ Download JSON", json.dumps(rd, indent=2, default=str), f"{run_name}.json", "application/json")
