import time
from typing import Optional, Callable
from datetime import datetime
from backend.metrics import compute_all_metrics
from backend.llm_judge import judge_sample
from backend.rag_pipeline import run_rag_pipeline
from config.settings import HALLUCINATION_THRESHOLD


class EvaluationResult:
    def __init__(self):
        self.run_id: Optional[int] = None
        self.run_name: str = ""
        self.model_name: str = ""
        self.samples: list[dict] = []
        self.aggregate_metrics: dict = {}
        self.created_at: datetime = datetime.utcnow()
        self.duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "run_name": self.run_name,
            "model_name": self.model_name,
            "samples": self.samples,
            "aggregate_metrics": self.aggregate_metrics,
            "created_at": self.created_at.isoformat(),
            "duration_seconds": self.duration_seconds,
        }


def evaluate_samples(
    samples: list[dict],
    run_name: str,
    model_name: str,
    use_llm_judge: bool = True,
    use_rag_pipeline: bool = False,
    progress_callback: Optional[Callable] = None,
    db_session=None,
    run_id: Optional[int] = None,
) -> EvaluationResult:
    result = EvaluationResult()
    result.run_name = run_name
    result.model_name = model_name
    result.run_id = run_id
    start_time = time.time()

    evaluated_samples = []
    total = len(samples)

    for idx, sample in enumerate(samples):
        if progress_callback:
            progress_callback(idx, total, f"Evaluating sample {idx + 1}/{total}...")

        question = sample.get("question", "")
        answer = sample.get("answer", "")
        ground_truth = sample.get("ground_truth")
        contexts = sample.get("contexts", [])

        if use_rag_pipeline and not answer:
            pipeline_output = run_rag_pipeline(question, top_k=3, model=model_name)
            answer = pipeline_output["answer"]
            contexts = pipeline_output["contexts"]

        if not contexts:
            contexts = [answer]

        llm_judge_result = None
        llm_verdict = None
        llm_reasoning = None
        if use_llm_judge and question and answer and contexts:
            try:
                llm_judge_result = judge_sample(question, answer, contexts, ground_truth)
                llm_verdict = llm_judge_result.get("verdict", "UNKNOWN")
                llm_reasoning = llm_judge_result.get("reasoning", "")
            except Exception as e:
                llm_verdict = "ERROR"
                llm_reasoning = str(e)

        metrics = compute_all_metrics(
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth,
            llm_judge_result=llm_judge_result,
        )

        is_hallucinated = metrics["hallucination_rate"] >= HALLUCINATION_THRESHOLD

        evaluated_sample = {
            "idx": idx,
            "question": question,
            "answer": answer,
            "ground_truth": ground_truth,
            "contexts": contexts,
            **metrics,
            "is_hallucinated": is_hallucinated,
            "llm_judge_verdict": llm_verdict,
            "llm_judge_reasoning": llm_reasoning,
        }
        evaluated_samples.append(evaluated_sample)

        if db_session and run_id:
            from backend.database.crud import create_sample
            create_sample(db_session, {
                "run_id": run_id,
                "question": question,
                "answer": answer,
                "ground_truth": ground_truth,
                "contexts": contexts,
                "faithfulness": metrics["faithfulness"],
                "answer_relevancy": metrics["answer_relevancy"],
                "context_precision": metrics["context_precision"],
                "context_recall": metrics["context_recall"],
                "hallucination_rate": metrics["hallucination_rate"],
                "is_hallucinated": is_hallucinated,
                "llm_judge_verdict": llm_verdict,
                "llm_judge_reasoning": llm_reasoning,
            })

    result.samples = evaluated_samples
    result.duration_seconds = time.time() - start_time

    if evaluated_samples:
        metric_keys = ["faithfulness", "answer_relevancy", "context_precision", "context_recall", "hallucination_rate", "overall_score"]
        result.aggregate_metrics = {
            k: round(sum(s[k] for s in evaluated_samples) / len(evaluated_samples), 4)
            for k in metric_keys
            if all(k in s for s in evaluated_samples)
        }
        result.aggregate_metrics["total_samples"] = len(evaluated_samples)
        result.aggregate_metrics["hallucinated_count"] = sum(1 for s in evaluated_samples if s["is_hallucinated"])

        if db_session and run_id:
            from backend.database.crud import update_run_metrics
            update_run_metrics(db_session, run_id, {
                "total_samples": result.aggregate_metrics["total_samples"],
                "avg_faithfulness": result.aggregate_metrics.get("faithfulness"),
                "avg_answer_relevancy": result.aggregate_metrics.get("answer_relevancy"),
                "avg_context_precision": result.aggregate_metrics.get("context_precision"),
                "avg_context_recall": result.aggregate_metrics.get("context_recall"),
                "avg_hallucination_rate": result.aggregate_metrics.get("hallucination_rate"),
                "overall_score": result.aggregate_metrics.get("overall_score"),
            })

    if progress_callback:
        progress_callback(total, total, "Evaluation complete!")

    return result
