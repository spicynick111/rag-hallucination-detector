import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/llm_eval_db")
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Groq free models (6000 requests/day FREE)
LLM_JUDGE_MODEL = "llama-3.3-70b-versatile"
EVALUATOR_TEMPERATURE = 0.0

METRICS = [
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
    "hallucination_rate",
]

HALLUCINATION_THRESHOLD = 0.3
FAITHFULNESS_THRESHOLD = 0.7
RELEVANCY_THRESHOLD = 0.6
