"""PatientWorld package exports.

This package includes the original transparent risk model and the newer
machine-learning pipeline for prediabetes prediction.
"""

from .ml_pipeline import (
    build_prediabetes_pipeline,
    create_synthetic_dataset,
    evaluate_model,
    train_prediabetes_model,
)
from .facial_model import FacePrediabetesModel, train_face_model

__all__ = [
    "build_prediabetes_pipeline",
    "create_synthetic_dataset",
    "evaluate_model",
    "train_prediabetes_model",
    "FacePrediabetesModel",
    "train_face_model",
]

__version__ = "0.1.0"
