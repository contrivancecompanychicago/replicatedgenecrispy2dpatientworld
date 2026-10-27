"""PatientWorld package exports.

This package includes transparent risk tools, a machine-learning workflow, and a
research-oriented face-feature extension for prediabetes risk modeling.
"""

from .facial_model import FacePrediabetesModel, train_face_model
from .ml_pipeline import (
    build_prediabetes_pipeline,
    calibrate_probability_model,
    create_synthetic_dataset,
    evaluate_model,
    load_cohort_csv,
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
    "score_dataset",
    "select_probability_threshold",
    "train_prediabetes_model",
    "train_test_split_data",
    "FacePrediabetesModel",
    "train_face_model",
]

__version__ = "0.1.0"
