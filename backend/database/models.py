from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean
from backend.database.connection import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_name = Column(String(255), nullable=False)
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_samples = Column(Integer, default=0)
    avg_faithfulness = Column(Float, nullable=True)
    avg_answer_relevancy = Column(Float, nullable=True)
    avg_context_precision = Column(Float, nullable=True)
    avg_context_recall = Column(Float, nullable=True)
    avg_hallucination_rate = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    config = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)


class EvaluationSample(Base):
    __tablename__ = "evaluation_samples"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    ground_truth = Column(Text, nullable=True)
    contexts = Column(JSON, nullable=True)
    faithfulness = Column(Float, nullable=True)
    answer_relevancy = Column(Float, nullable=True)
    context_precision = Column(Float, nullable=True)
    context_recall = Column(Float, nullable=True)
    hallucination_rate = Column(Float, nullable=True)
    is_hallucinated = Column(Boolean, default=False)
    llm_judge_verdict = Column(Text, nullable=True)
    llm_judge_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)
