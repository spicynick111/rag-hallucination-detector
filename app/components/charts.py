import plotly.graph_objects as go
import pandas as pd


CHART_BG = "#0C0C0F"
GRID_COLOR = "rgba(255,255,255,0.05)"
FONT_COLOR = "#6B7280"
ACCENT = "#6366F1"
PURPLE = "#EC4899"
GREEN = "#22C55E"
RED = "#EF4444"
AMBER = "#F59E0B"

# Base layout WITHOUT xaxis/yaxis so callers can override freely
_BASE = dict(
    paper_bgcolor=CHART_BG,
    plot_bgcolor="#16161C",
    font=dict(family="Inter, sans-serif", color=FONT_COLOR, size=12),
    margin=dict(l=20, r=20, t=40, b=20),
)

_AXIS = dict(gridcolor=GRID_COLOR, showline=False, tickfont=dict(size=11))


def _layout(**extra):
    """Merge _BASE with caller-supplied overrides (no duplicate key risk)."""
    return {**_BASE, **extra}


def radar_chart(metrics: dict, title: str = "Evaluation Radar") -> go.Figure:
    labels = ["Faithfulness", "Answer Relevancy", "Context Precision", "Context Recall", "Trustworthiness"]
    values = [
        metrics.get("faithfulness", 0),
        metrics.get("answer_relevancy", 0),
        metrics.get("context_precision", 0),
        metrics.get("context_recall", 0),
        1 - metrics.get("hallucination_rate", 0),
    ]
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed, theta=labels_closed,
        fill="toself",
        fillcolor="rgba(0,212,255,0.12)",
        line=dict(color=ACCENT, width=2),
        name="Score",
    ))
    fig.update_layout(**_layout(
        polar=dict(
            bgcolor="#111827",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID_COLOR, tickfont=dict(size=10, color=FONT_COLOR)),
            angularaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=11, color="#E2E8F0")),
        ),
        title=dict(text=title, font=dict(color="#E2E8F0", size=14), x=0.5),
        showlegend=False,
    ))
    return fig


def gauge_chart(value: float, title: str, color: str = ACCENT) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,
        number={"suffix": "%", "font": {"size": 28, "color": color, "family": "JetBrains Mono, monospace"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": GRID_COLOR, "tickfont": {"size": 10, "color": FONT_COLOR}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#1E2535",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(239,68,68,0.15)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.12)"},
                {"range": [70, 100], "color": "rgba(16,185,129,0.12)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.8, "value": value * 100},
        },
        title={"text": title, "font": {"color": "#E2E8F0", "size": 13}},
    ))
    fig.update_layout(paper_bgcolor=CHART_BG, margin=dict(l=10, r=10, t=50, b=10), height=200)
    return fig


def hallucination_heatmap(samples: list[dict]) -> go.Figure:
    if not samples:
        return go.Figure()

    n = len(samples)
    cols = min(10, n)
    rows = (n + cols - 1) // cols

    z, hover = [], []
    for r in range(rows):
        z_row, h_row = [], []
        for c in range(cols):
            idx = r * cols + c
            if idx < n:
                rate = samples[idx].get("hallucination_rate", 0)
                z_row.append(rate)
                q = samples[idx].get("question", "")[:60]
                h_row.append(f"Q: {q}<br>Hallucination: {rate:.1%}<br>Verdict: {samples[idx].get('llm_judge_verdict','N/A')}")
            else:
                z_row.append(None)
                h_row.append("")
        z.append(z_row)
        hover.append(h_row)

    fig = go.Figure(go.Heatmap(
        z=z, text=hover,
        hovertemplate="%{text}<extra></extra>",
        colorscale=[[0, GREEN], [0.3, AMBER], [1, RED]],
        zmin=0, zmax=1, showscale=True,
        colorbar=dict(
            title=dict(text="Hallucination Rate", font=dict(color=FONT_COLOR, size=11)),
            tickfont=dict(color=FONT_COLOR, size=10), thickness=12,
        ),
    ))
    fig.update_layout(**_layout(
        title=dict(text="Hallucination Heatmap — Each Cell = 1 Sample", font=dict(color="#E2E8F0", size=14), x=0.5),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        height=max(200, rows * 60 + 80),
    ))
    return fig


def metric_trend_chart(runs: list[dict]) -> go.Figure:
    if not runs:
        return go.Figure()

    df = pd.DataFrame(runs)
    df["created_at"] = pd.to_datetime(df["created_at"])

    fig = go.Figure()
    traces = [
        ("avg_faithfulness", "Faithfulness", ACCENT),
        ("avg_answer_relevancy", "Answer Relevancy", GREEN),
        ("avg_context_precision", "Context Precision", PURPLE),
        ("avg_hallucination_rate", "Hallucination Rate", RED),
    ]
    for col, name, color in traces:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["created_at"], y=df[col],
                name=name, line=dict(color=color, width=2),
                mode="lines+markers", marker=dict(size=6, color=color),
                hovertemplate=f"<b>{name}</b><br>%{{y:.1%}}<extra></extra>",
            ))

    fig.update_layout(**_layout(
        title=dict(text="Metric Trends Over Time", font=dict(color="#E2E8F0", size=14), x=0.5),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_COLOR, size=11)),
        hovermode="x unified",
        xaxis=dict(**_AXIS),
        yaxis=dict(**_AXIS, tickformat=".0%", range=[0, 1.05]),
    ))
    return fig


def comparison_bar_chart(runs: list[dict]) -> go.Figure:
    if not runs:
        return go.Figure()

    metrics = ["avg_faithfulness", "avg_answer_relevancy", "avg_context_precision", "avg_context_recall"]
    labels = ["Faithfulness", "Ans. Relevancy", "Ctx Precision", "Ctx Recall"]

    fig = go.Figure()
    for run in runs:
        fig.add_trace(go.Bar(
            name=run.get("run_name", "Run"),
            x=labels,
            y=[run.get(m, 0) for m in metrics],
            text=[f"{run.get(m, 0):.1%}" for m in metrics],
            textposition="outside",
            textfont=dict(size=10, color="#E2E8F0"),
        ))

    fig.update_layout(**_layout(
        title=dict(text="Multi-Run Comparison", font=dict(color="#E2E8F0", size=14), x=0.5),
        barmode="group",
        bargap=0.15, bargroupgap=0.05,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_COLOR)),
        xaxis=dict(**_AXIS),
        yaxis=dict(**_AXIS, tickformat=".0%", range=[0, 1.2]),
    ))
    return fig


def distribution_histogram(samples: list[dict], metric: str = "hallucination_rate") -> go.Figure:
    values = [s.get(metric, 0) for s in samples if metric in s]
    if not values:
        return go.Figure()

    label_map = {
        "hallucination_rate": "Hallucination Rate",
        "faithfulness": "Faithfulness",
        "answer_relevancy": "Answer Relevancy",
        "context_precision": "Context Precision",
        "context_recall": "Context Recall",
    }
    human_label = label_map.get(metric, metric)

    fig = go.Figure(go.Histogram(
        x=values, nbinsx=20,
        marker_color=ACCENT,
        marker_line=dict(color=CHART_BG, width=0.5),
        opacity=0.85,
    ))
    fig.update_layout(**_layout(
        title=dict(text=f"{human_label} Distribution", font=dict(color="#E2E8F0", size=14), x=0.5),
        xaxis=dict(**_AXIS, title=human_label, title_font=dict(color=FONT_COLOR)),
        yaxis=dict(**_AXIS, title="Count", title_font=dict(color=FONT_COLOR)),
    ))
    return fig
