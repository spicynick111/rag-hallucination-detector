<div align="center">

# RAG Hallucination Detector

### Production-grade RAG pipeline evaluation & hallucination detection framework

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://rag-hallucination-detector.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-F55036?style=for-the-badge)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

**[🚀 Live Demo](https://rag-hallucination-detector.streamlit.app/) · [Report Bug](https://github.com/spicynick111/rag-hallucination-detector/issues) · [Request Feature](https://github.com/spicynick111/rag-hallucination-detector/issues)**

</div>

---

## Overview

Most engineers build LLMs. Few can **measure their quality**.

This framework evaluates the output of any RAG (Retrieval-Augmented Generation) pipeline across 5 production-grade metrics — automatically detecting hallucinations, scoring faithfulness, and visualizing results in a real-time dashboard.

Built for **LLMOps engineers** and **AI practitioners** who need to go beyond model accuracy and into **answer quality assurance**.

---

## Live Demo

> **Try it now → [https://rag-hallucination-detector.streamlit.app](https://rag-hallucination-detector.streamlit.app/)**

No setup needed. The demo includes a built-in RAG simulator and 5 sample Q&A pairs covering RAG, hallucinations, LLMOps, RAGAS, and vector databases.

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🔬 **Evaluation Engine** | Run Q&A datasets through a full evaluation pipeline with one click |
| 🤖 **LLM Judge** | Llama 3.3 70B via Groq evaluates each answer for faithfulness & hallucinations |
| 🌡️ **Hallucination Heatmap** | Per-sample grid visualization — instantly spot weak answers |
| 📈 **Trend Dashboard** | Track metric evolution across multiple evaluation runs |
| ⚖️ **Model Comparison** | Side-by-side radar charts and scorecards across models |
| 🔌 **RAG Simulator** | Built-in retrieval pipeline — no external setup needed |
| 📤 **Export** | Download full results as CSV or JSON |
| 🗃️ **PostgreSQL** | Optional persistent storage for evaluation history |

---

## Evaluation Metrics

| Metric | What it measures | Target |
|--------|-----------------|--------|
| **Faithfulness** | Are all claims in the answer grounded in retrieved context? | > 0.80 |
| **Answer Relevancy** | Does the answer actually address the question? | > 0.75 |
| **Context Precision** | How relevant are the retrieved chunks to the question? | > 0.70 |
| **Context Recall** | Does the context cover all info needed to answer? | > 0.65 |
| **Hallucination Rate** | Fraction of answer NOT supported by context *(lower = better)* | < 0.20 |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit · Plotly · Custom CSS |
| **LLM Judge** | Llama 3.3 70B via Groq (free tier) |
| **Evaluation** | RAGAS-inspired metric engine |
| **RAG Pipeline** | LangChain · Built-in knowledge base |
| **Database** | PostgreSQL · SQLAlchemy · Alembic |
| **Deployment** | Streamlit Cloud · Docker · Docker Compose |

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/spicynick111/rag-hallucination-detector.git
cd rag-hallucination-detector

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (free at https://console.groq.com)

# 4. Run the app
streamlit run app/main.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Docker

```bash
cp .env.example .env
# Add GROQ_API_KEY to .env
docker-compose up --build
```

---

## Get a Free API Key

This project uses **Groq** for LLM inference — completely free, no credit card required.

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → API Keys → Create API Key
3. Copy your key (starts with `gsk_`)
4. Paste into `.env` as `GROQ_API_KEY`

**Free tier:** 6,000 requests/day · 100 requests/minute

---

## Project Structure

```
rag-hallucination-detector/
├── app/
│   ├── main.py                  # Home page
│   ├── components/
│   │   ├── styles.py            # Dark UI theme & CSS
│   │   └── charts.py            # Plotly visualizations
│   └── pages/
│       ├── 1_Dashboard.py       # Aggregate metrics & radar chart
│       ├── 2_Evaluate.py        # Run evaluations
│       ├── 3_Heatmap.py         # Hallucination heatmap
│       ├── 4_Trends.py          # Historical trend analysis
│       └── 5_Compare.py         # Multi-model comparison
├── backend/
│   ├── evaluator.py             # Core evaluation engine
│   ├── metrics.py               # Metric computation (faithfulness, relevancy, etc.)
│   ├── llm_judge.py             # Groq LLM judge integration
│   ├── rag_pipeline.py          # Built-in RAG simulator
│   └── database/
│       ├── models.py            # SQLAlchemy ORM models
│       ├── crud.py              # Database operations
│       └── connection.py        # Connection management
├── config/
│   └── settings.py              # Centralized configuration
├── .env.example                 # Environment variable template
├── docker-compose.yml
├── Dockerfile
├── packages.txt                 # System deps for Streamlit Cloud
└── requirements.txt
```

---

## How It Works

```
User provides Q&A pairs (or uses built-in RAG simulator)
              ↓
RAG Pipeline retrieves relevant context chunks
              ↓
Llama 3.3 70B judges each answer:
   · Is every claim supported by the context?
   · Is the answer relevant to the question?
   · What specific claims are hallucinated?
              ↓
Metric engine computes 5 scores per sample
              ↓
Dashboard renders heatmaps, radar charts, trends
```

---

## Why This Project

Production AI teams don't just ship models — they **monitor output quality**.

This tool demonstrates:
- **LLMOps thinking** — evaluation pipelines, not just model training
- **Hallucination detection** — a core concern in enterprise RAG deployments
- **End-to-end ownership** — from metric design to deployed dashboard

---

## License

MIT © [spicynick111](https://github.com/spicynick111)
