# LLM Evaluation & Hallucination Detection Framework

> Enterprise-grade RAG pipeline evaluation with Claude-powered LLM judging, hallucination heatmaps, and real-time metric dashboards.

## Features

- **5 Core Metrics** — Faithfulness, Answer Relevancy, Context Precision, Context Recall, Hallucination Rate
- **Claude LLM Judge** — Uses Claude Opus 4.8 as an expert evaluator with adaptive thinking
- **Hallucination Heatmap** — Per-sample visual breakdown of hallucination intensity
- **Built-in RAG Simulator** — Test evaluations without needing your own pipeline
- **Trend Dashboard** — Track metric evolution across evaluation runs
- **Multi-Model Comparison** — Radar overlay and bar charts across models
- **Export** — Download results as CSV or JSON
- **PostgreSQL Storage** — Persistent evaluation history (optional)

## Quick Start

```bash
# 1. Clone and install
cd llm-eval-framework
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. (Optional) Initialize DB
python init_db.py

# 4. Run
streamlit run app/main.py
```

## Docker

```bash
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
docker-compose up --build
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit + Plotly |
| LLM Judge | Claude Opus 4.8 (Anthropic) |
| RAG Framework | LangChain |
| Evaluation | RAGAS-inspired metrics |
| Database | PostgreSQL + SQLAlchemy |
| Deployment | Docker + Docker Compose |

## Project Structure

```
llm-eval-framework/
├── app/
│   ├── main.py              # Home page
│   ├── components/
│   │   ├── styles.py        # Dark UI theme & CSS
│   │   └── charts.py        # Plotly visualizations
│   └── pages/
│       ├── 1_Dashboard.py   # Metrics overview
│       ├── 2_Evaluate.py    # Run evaluations
│       ├── 3_Heatmap.py     # Hallucination heatmap
│       ├── 4_Trends.py      # Historical trends
│       └── 5_Compare.py     # Multi-model comparison
├── backend/
│   ├── evaluator.py         # Core evaluation engine
│   ├── metrics.py           # RAGAS-style metric computation
│   ├── llm_judge.py         # Claude LLM judge
│   ├── rag_pipeline.py      # Built-in RAG simulator
│   └── database/
│       ├── models.py        # SQLAlchemy ORM models
│       ├── crud.py          # Database operations
│       └── connection.py    # DB connection
├── config/settings.py       # Configuration
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Metrics Explained

| Metric | Description | Good Score |
|--------|-------------|-----------|
| **Faithfulness** | Are all claims grounded in the retrieved context? | > 0.80 |
| **Answer Relevancy** | How well does the answer address the question? | > 0.75 |
| **Context Precision** | How relevant are the retrieved contexts? | > 0.70 |
| **Context Recall** | How much of the ground truth is in the context? | > 0.65 |
| **Hallucination Rate** | Fraction of answer not supported by context | < 0.20 |
