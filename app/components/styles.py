GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.stApp { background: #0C0C0F; }
.block-container { padding: 1.5rem 2.5rem 3rem; max-width: 1380px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0C0C0F; }
::-webkit-scrollbar-thumb { background: #2D2D35; border-radius: 3px; }

/* ── Hero gradient orbs ── */
.hero-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.12;
    pointer-events: none;
    z-index: 0;
}

/* ── Metric cards ── */
.metric-card {
    background: #16161C;
    border: 1px solid #2A2A35;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.25s;
}
.metric-card:hover {
    border-color: rgba(99,102,241,0.5);
    transform: translateY(-2px);
}
.metric-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(99,102,241,0.04) 0%, transparent 60%);
    pointer-events: none;
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
}
.metric-delta {
    font-size: 0.76rem;
    color: #4B5563;
    margin-top: 0.3rem;
}

/* ── Feature cards ── */
.feature-card {
    background: linear-gradient(145deg, #16161C, #1C1C24);
    border: 1px solid #2A2A35;
    border-radius: 20px;
    padding: 1.75rem 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.feature-card:hover {
    border-color: rgba(99,102,241,0.6);
    background: linear-gradient(145deg, #1C1C28, #22223A);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(99,102,241,0.12);
}
.feature-card .icon {
    font-size: 2.2rem;
    margin-bottom: 0.75rem;
    display: block;
}
.feature-card .title {
    font-size: 1rem;
    font-weight: 700;
    color: #F1F0FF;
    margin-bottom: 0.5rem;
}
.feature-card .desc {
    font-size: 0.8rem;
    color: #6B7280;
    line-height: 1.55;
}

/* ── Badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.22rem 0.7rem;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-green  { background: rgba(34,197,94,0.12);  color: #22C55E; border: 1px solid rgba(34,197,94,0.25); }
.badge-red    { background: rgba(239,68,68,0.12);   color: #EF4444; border: 1px solid rgba(239,68,68,0.25); }
.badge-yellow { background: rgba(245,158,11,0.12);  color: #F59E0B; border: 1px solid rgba(245,158,11,0.25); }
.badge-blue   { background: rgba(99,102,241,0.12);  color: #818CF8; border: 1px solid rgba(99,102,241,0.25); }

/* ── Section header ── */
.section-header {
    font-size: 0.95rem;
    font-weight: 700;
    color: #D1D5DB;
    border-left: 3px solid #6366F1;
    padding-left: 0.75rem;
    margin: 1.75rem 0 1rem;
    letter-spacing: -0.01em;
}

/* ── Info box ── */
.info-box {
    background: rgba(99,102,241,0.06);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    color: #A5B4FC;
    font-size: 0.87rem;
    line-height: 1.6;
}

/* ── Sample card (high-risk) ── */
.sample-card {
    background: #16161C;
    border: 1px solid #2A2A35;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s;
}
.sample-card:hover { border-color: #6366F1; }

/* ── Score bar ── */
.score-bar-wrap { background: #1E1E28; border-radius: 4px; height: 5px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 4px; }

/* ── Streamlit overrides ── */
div[data-testid="metric-container"] {
    background: #16161C !important;
    border: 1px solid #2A2A35 !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.1rem !important;
}
div[data-testid="metric-container"] label { color: #6B7280 !important; font-size: 0.76rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
div[data-testid="metric-container"] [data-testid="metric-value"] { color: #A5B4FC !important; font-family: 'JetBrains Mono', monospace !important; }

div[data-testid="stDataFrame"] { border: 1px solid #2A2A35; border-radius: 12px; overflow: hidden; }
div[data-testid="stDataFrame"] th { background: #16161C !important; color: #6B7280 !important; font-size: 0.76rem !important; text-transform: uppercase; letter-spacing: 0.08em; }

.stButton > button {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    padding: 0.6rem 1.2rem !important;
    transition: opacity 0.2s, transform 0.2s !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }

[data-testid="stSidebar"] {
    background: #0F0F13 !important;
    border-right: 1px solid #1E1E28 !important;
}
[data-testid="stSidebar"] .stMarkdown { color: #9CA3AF; }
[data-testid="stSidebar"] label { color: #9CA3AF !important; font-size: 0.82rem !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #16161C;
    border-radius: 10px;
    padding: 3px;
    border: 1px solid #2A2A35;
}
.stTabs [data-baseweb="tab"] { color: #6B7280; border-radius: 8px; font-weight: 500; }
.stTabs [aria-selected="true"] {
    background: #6366F1 !important;
    color: white !important;
}

.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: #16161C !important;
    border: 1px solid #2A2A35 !important;
    border-radius: 8px !important;
    color: #E5E7EB !important;
}
.stToggle { accent-color: #6366F1; }
.stSlider > div > div > div { background: #6366F1 !important; }

.stProgress > div > div > div > div { background: linear-gradient(90deg, #6366F1, #8B5CF6) !important; }
.stExpander { border: 1px solid #2A2A35 !important; border-radius: 12px !important; background: #16161C !important; }
.stExpander summary { color: #D1D5DB !important; font-weight: 600; }

/* ── Tag / pill ── */
.tag {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    background: rgba(99,102,241,0.1);
    color: #818CF8;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    border: 1px solid rgba(99,102,241,0.2);
}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = "", color: str = "#6366F1") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color};">{value}</div>
        {f'<div class="metric-delta">{delta}</div>' if delta else ''}
    </div>"""


def verdict_badge(verdict: str) -> str:
    mapping = {
        "FAITHFUL":           ("badge-green",  "✓ Faithful"),
        "HALLUCINATED":       ("badge-red",    "✗ Hallucinated"),
        "PARTIALLY_FAITHFUL": ("badge-yellow", "~ Partial"),
        "UNKNOWN":            ("badge-blue",   "? Unknown"),
        "ERROR":              ("badge-red",    "! Error"),
    }
    cls, label = mapping.get(verdict, ("badge-blue", verdict))
    return f'<span class="badge {cls}">{label}</span>'


def score_pill(value: float) -> str:
    color = "#22C55E" if value >= 0.7 else "#F59E0B" if value >= 0.4 else "#EF4444"
    return f'<span style="color:{color}; font-family:JetBrains Mono,monospace; font-weight:700; font-size:0.9rem;">{value:.0%}</span>'
