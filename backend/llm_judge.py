import json
from typing import Optional
from openai import OpenAI
from config.settings import GROQ_API_KEY, GROQ_BASE_URL, LLM_JUDGE_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
    return _client


JUDGE_SYSTEM = """You are an expert LLM Evaluator and hallucination detection specialist.
Assess whether the AI answer is faithful to the given context, relevant to the question, and hallucination-free.

Return ONLY valid JSON — no markdown, no extra text:
{
  "verdict": "FAITHFUL" | "HALLUCINATED" | "PARTIALLY_FAITHFUL",
  "hallucination_score": <float 0.0-1.0, 1.0 = fully hallucinated>,
  "faithfulness_score": <float 0.0-1.0, 1.0 = fully faithful>,
  "relevancy_score": <float 0.0-1.0, 1.0 = perfectly relevant>,
  "reasoning": "<brief explanation>",
  "hallucinated_claims": ["<claim not in context>"],
  "supported_claims": ["<claim supported by context>"]
}"""


def judge_sample(question: str, answer: str, contexts: list[str], ground_truth: Optional[str] = None) -> dict:
    context_text = "\n\n".join([f"[Context {i+1}]: {c}" for i, c in enumerate(contexts)])
    user_msg = f"""QUESTION: {question}

RETRIEVED CONTEXTS:
{context_text}

AI-GENERATED ANSWER: {answer}
{"GROUND TRUTH: " + ground_truth if ground_truth else ""}

Evaluate faithfulness, relevancy, and identify hallucinated claims."""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=LLM_JUDGE_MODEL,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.0,
            max_tokens=1024,
        )
        text = response.choices[0].message.content.strip()

        if "```" in text:
            for part in text.split("```"):
                part = part.strip().lstrip("json").strip()
                if part.startswith("{"):
                    text = part
                    break

        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])

    except Exception as e:
        err = str(e)
        if "429" in err or "rate" in err.lower():
            return {
                "verdict": "UNKNOWN",
                "hallucination_score": 0.5,
                "faithfulness_score": 0.5,
                "relevancy_score": 0.5,
                "reasoning": "Rate limit hit — metrics computed without LLM judge.",
                "hallucinated_claims": [],
                "supported_claims": [],
            }

    return {
        "verdict": "UNKNOWN",
        "hallucination_score": 0.5,
        "faithfulness_score": 0.5,
        "relevancy_score": 0.5,
        "reasoning": "Judge evaluation failed — check GROQ_API_KEY.",
        "hallucinated_claims": [],
        "supported_claims": [],
    }


def batch_judge(samples: list[dict]) -> list[dict]:
    return [
        judge_sample(
            question=s.get("question", ""),
            answer=s.get("answer", ""),
            contexts=s.get("contexts", []),
            ground_truth=s.get("ground_truth"),
        )
        for s in samples
    ]
