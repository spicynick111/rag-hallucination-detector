import os
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


GROQ_API_KEY  = _get_secret("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DATABASE_URL  = _get_secret("DATABASE_URL", "postgresql://postgres:password@localhost:5432/llm_eval_db")
APP_ENV       = _get_secret("APP_ENV", "development")
LOG_LEVEL     = _get_secret("LOG_LEVEL", "INFO")

LLM_JUDGE_MODEL      = "llama-3.3-70b-versatile"
EVALUATOR_TEMPERATURE = 0.0

METRICS = [
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
    "hallucination_rate",
]

HALLUCINATION_THRESHOLD = 0.3
FAITHFULNESS_THRESHOLD  = 0.7
RELEVANCY_THRESHOLD     = 0.6
