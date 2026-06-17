import re
import numpy as np
from typing import Optional

# Common English stopwords — excluded so overlap reflects meaningful terms
_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "but", "if", "then", "of", "to", "in", "on", "at", "by",
    "for", "with", "as", "from", "how", "what", "why", "when", "where",
    "which", "who", "does", "do", "did", "this", "that", "these", "those",
    "it", "its", "can", "will", "would", "should", "could", "may", "might",
}


def _tokens(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}


def compute_token_overlap(text1: str, text2: str) -> float:
    """Jaccard similarity (symmetric) — used for general matching."""
    w1, w2 = _tokens(text1), _tokens(text2)
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def _coverage(needle: str, haystack: str) -> float:
    """Directional: fraction of `needle` terms found in `haystack`.
    Better than Jaccard when the two texts differ a lot in length."""
    n, h = _tokens(needle), _tokens(haystack)
    if not n:
        return 0.0
    return len(n & h) / len(n)


def compute_faithfulness(answer: str, contexts: list[str]) -> float:
    """How much of the answer is supported by the best-matching context."""
    if not answer or not contexts:
        return 0.0
    return float(np.max([_coverage(answer, ctx) for ctx in contexts]))


def compute_answer_relevancy(question: str, answer: str) -> float:
    """How well the answer covers the question's key terms (+ length signal)."""
    if not question or not answer:
        return 0.0
    coverage = _coverage(question, answer)
    length_bonus = min(1.0, len(answer.split()) / 30)
    return float(min(1.0, coverage * 0.7 + length_bonus * 0.3))


def compute_context_precision(question: str, contexts: list[str]) -> float:
    """Are the retrieved contexts relevant to the question?
    Best context's coverage of the question, blended with the mean."""
    if not contexts or not question:
        return 0.0
    scores = [_coverage(question, ctx) for ctx in contexts]
    return float(0.6 * np.max(scores) + 0.4 * np.mean(scores))


def compute_context_recall(answer: str, ground_truth: Optional[str], contexts: list[str]) -> float:
    """Does the context cover the information in the ground truth (or answer)?"""
    if not contexts:
        return 0.0
    reference = ground_truth or answer
    if not reference:
        return 0.5
    joined = " ".join(contexts)
    return float(_coverage(reference, joined))


def compute_hallucination_rate(faithfulness: float, llm_judge_score: Optional[float] = None) -> float:
    base = 1.0 - faithfulness
    if llm_judge_score is not None:
        return float((base * 0.4) + (llm_judge_score * 0.6))
    return float(base)


def compute_overall_score(metrics: dict) -> float:
    weights = {
        "faithfulness": 0.30,
        "answer_relevancy": 0.25,
        "context_precision": 0.20,
        "context_recall": 0.15,
        "hallucination_rate": 0.10,
    }
    score = 0.0
    for metric, weight in weights.items():
        val = metrics.get(metric, 0.0)
        if metric == "hallucination_rate":
            val = 1.0 - val
        score += val * weight
    return round(float(score), 4)


def compute_all_metrics(
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: Optional[str] = None,
    llm_judge_result: Optional[dict] = None,
) -> dict:
    faithfulness = compute_faithfulness(answer, contexts)
    answer_relevancy = compute_answer_relevancy(question, answer)
    context_precision = compute_context_precision(question, contexts)
    context_recall = compute_context_recall(answer, ground_truth, contexts)

    judge_hallucination = None
    if llm_judge_result:
        faithfulness = faithfulness * 0.4 + llm_judge_result.get("faithfulness_score", faithfulness) * 0.6
        answer_relevancy = answer_relevancy * 0.4 + llm_judge_result.get("relevancy_score", answer_relevancy) * 0.6
        judge_hallucination = llm_judge_result.get("hallucination_score")

    hallucination_rate = compute_hallucination_rate(faithfulness, judge_hallucination)

    metrics = {
        "faithfulness": round(faithfulness, 4),
        "answer_relevancy": round(answer_relevancy, 4),
        "context_precision": round(context_precision, 4),
        "context_recall": round(context_recall, 4),
        "hallucination_rate": round(hallucination_rate, 4),
    }
    metrics["overall_score"] = compute_overall_score(metrics)
    return metrics
