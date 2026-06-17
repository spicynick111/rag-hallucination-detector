import numpy as np
from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity


def compute_token_overlap(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


def compute_faithfulness(answer: str, contexts: list[str]) -> float:
    if not answer or not contexts:
        return 0.0
    scores = [compute_token_overlap(answer, ctx) for ctx in contexts]
    return float(np.max(scores))


def compute_answer_relevancy(question: str, answer: str) -> float:
    if not question or not answer:
        return 0.0
    q_words = set(question.lower().split())
    a_words = set(answer.lower().split())
    if not q_words:
        return 0.0
    overlap = len(q_words & a_words) / len(q_words)
    length_bonus = min(1.0, len(answer.split()) / 30)
    return float(min(1.0, overlap * 0.6 + length_bonus * 0.4))


def compute_context_precision(question: str, contexts: list[str]) -> float:
    if not contexts or not question:
        return 0.0
    scores = [compute_token_overlap(question, ctx) for ctx in contexts]
    return float(np.mean(scores))


def compute_context_recall(answer: str, ground_truth: Optional[str], contexts: list[str]) -> float:
    if not ground_truth or not contexts:
        if answer and contexts:
            scores = [compute_token_overlap(answer, ctx) for ctx in contexts]
            return float(np.mean(scores))
        return 0.5
    scores = [compute_token_overlap(ground_truth, ctx) for ctx in contexts]
    return float(np.mean(scores))


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
