from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database.models import EvaluationRun, EvaluationSample


def create_evaluation_run(db: Session, run_name: str, model_name: str, config: dict = None, tags: list = None) -> EvaluationRun:
    run = EvaluationRun(
        run_name=run_name,
        model_name=model_name,
        config=config or {},
        tags=tags or [],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def update_run_metrics(db: Session, run_id: int, metrics: dict) -> EvaluationRun:
    run = db.query(EvaluationRun).filter(EvaluationRun.id == run_id).first()
    if run:
        for key, val in metrics.items():
            setattr(run, key, val)
        db.commit()
        db.refresh(run)
    return run


def create_sample(db: Session, sample_data: dict) -> EvaluationSample:
    sample = EvaluationSample(**sample_data)
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


def get_all_runs(db: Session, limit: int = 50) -> List[EvaluationRun]:
    return db.query(EvaluationRun).order_by(desc(EvaluationRun.created_at)).limit(limit).all()


def get_run_by_id(db: Session, run_id: int) -> Optional[EvaluationRun]:
    return db.query(EvaluationRun).filter(EvaluationRun.id == run_id).first()


def get_samples_by_run(db: Session, run_id: int) -> List[EvaluationSample]:
    return db.query(EvaluationSample).filter(EvaluationSample.run_id == run_id).all()


def get_hallucinated_samples(db: Session, run_id: int) -> List[EvaluationSample]:
    return (
        db.query(EvaluationSample)
        .filter(EvaluationSample.run_id == run_id, EvaluationSample.is_hallucinated == True)
        .all()
    )


def get_trend_data(db: Session, days: int = 30) -> List[EvaluationRun]:
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(EvaluationRun)
        .filter(EvaluationRun.created_at >= cutoff)
        .order_by(EvaluationRun.created_at)
        .all()
    )


def delete_run(db: Session, run_id: int) -> bool:
    db.query(EvaluationSample).filter(EvaluationSample.run_id == run_id).delete()
    deleted = db.query(EvaluationRun).filter(EvaluationRun.id == run_id).delete()
    db.commit()
    return deleted > 0
