"""PatientWorld package exports.

This package includes the risk-scoring utilities, machine-learning workflow,
and research-oriented face-feature extension.
"""

from .facial_model import FacePrediabetesModel, train_face_model
from .ml_pipeline import (
    build_prediabetes_pipeline,
    calibrate_probability_model,
    create_synthetic_dataset,
    evaluate_model,
    load_cohort_csv,
    save_model,
    score_dataset,
    select_probability_threshold,
    train_prediabetes_model,
    train_test_split_data,
)

__all__ = [
    "build_prediabetes_pipeline",
    "calibrate_probability_model",
    "create_synthetic_dataset",
    "evaluate_model",
    "load_cohort_csv",
    "save_model",
    "score_dataset",
    "select_probability_threshold",
    "train_prediabetes_model",
    "train_test_split_data",
    "FacePrediabetesModel",
    "train_face_model",
    "__version__",
]

__version__ = "0.1.0"
