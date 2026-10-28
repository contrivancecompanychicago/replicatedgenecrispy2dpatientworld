"""Firestore integration helpers for the PatientWorld ML workflow."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import pandas as pd

try:  # pragma: no cover - optional dependency for runtime deployment
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:  # pragma: no cover
    firebase_admin = None  # type: ignore[assignment]
    credentials = None  # type: ignore[assignment]
    firestore = None  # type: ignore[assignment]

from .cli import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    OPTIONAL_FACE_FEATURES,
    build_prediabetes_pipeline,
    create_synthetic_dataset,
)

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES + OPTIONAL_FACE_FEATURES


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def normalize_patient_record(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Firebase or API patient payload into the model feature schema."""
    record = dict(raw_record)
    normalized = {
        "sex": str(record.get("sex", "unknown") or "unknown").strip().lower(),
        "smoking_status": str(record.get("smoking_status", "never") or "never").strip().lower(),
        "age": _safe_float(record.get("age"), 45.0),
        "bmi": _safe_float(record.get("bmi"), 27.5),
        "pack_years": _safe_float(record.get("pack_years"), 0.0),
        "alcohol_drinks_per_week": _safe_float(record.get("alcohol_drinks_per_week"), 0.0),
        "family_history": _safe_int(record.get("family_history"), 0),
        "sleep_hours": _safe_float(record.get("sleep_hours"), 7.0),
        "waist_circumference": _safe_float(record.get("waist_circumference"), 90.0),
        "blood_pressure": _safe_float(record.get("blood_pressure"), 120.0),
    }

    for i in range(1, 9):
        key = f"face_embedding_{i}"
        normalized[key] = _safe_float(record.get(key), 0.0)

    return normalized


def initialize_firebase(service_account_path: Optional[str | Path] = None, project_id: Optional[str] = None):
    """Initialize Firebase Admin SDK for Firestore access."""
    path = service_account_path or os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if firebase_admin is None:
        raise ImportError("firebase-admin is not installed. Add firebase-admin to the project dependencies.")

    if not firebase_admin._apps:
        if path:
            cred = credentials.Certificate(str(path))
            firebase_admin.initialize_app(cred, {"projectId": project_id} if project_id else {})
        else:
            firebase_admin.initialize_app()

    if firestore is None:
        raise ImportError("google-cloud-firestore is not installed.")

    return firestore.client()


class PatientWorldFirestoreClient:
    """Convenience wrapper for saving patient and prediction records to Firestore."""

    def __init__(self, service_account_path: Optional[str | Path] = None, project_id: Optional[str] = None):
        self.db = initialize_firebase(service_account_path=service_account_path, project_id=project_id)

    def patients(self):
        return self.db.collection("patients")

    def predictions(self):
        return self.db.collection("predictions")

    def save_patient(self, patient_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        document = dict(payload)
        document["updatedAt"] = document.get("updatedAt") or pd.Timestamp.utcnow().isoformat()
        self.patients().document(str(patient_id)).set(document, merge=True)
        return document

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        doc = self.patients().document(str(patient_id)).get()
        return doc.to_dict() if doc.exists else None

    def save_prediction(
        self,
        patient_id: str,
        predicted_probability: float,
        predicted_label: int,
        threshold: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "patientId": str(patient_id),
            "predictedProbability": float(predicted_probability),
            "predictedLabel": int(predicted_label),
            "threshold": float(threshold),
            "createdAt": pd.Timestamp.utcnow().isoformat(),
        }
        if metadata:
            record.update(metadata)
        doc_ref = self.predictions().document()
        doc_ref.set(record)
        return {"id": doc_ref.id, **record}


def build_default_model() -> Any:
    """Train a lightweight default model at runtime when no model artifact exists."""
    df = create_synthetic_dataset("/tmp/patientworld_synthetic_data.csv", n_samples=1500, seed=42)
    X = df[FEATURES]
    y = df["prediabetes"]
    model = build_prediabetes_pipeline()
    model.fit(X, y)
    return model


def predict_patient_record(raw_record: Dict[str, Any], model: Optional[Any] = None, threshold: float = 0.5) -> Dict[str, Any]:
    """Generate a risk prediction for a single patient payload."""
    model = model or build_default_model()
    normalized = normalize_patient_record(raw_record)
    feature_frame = pd.DataFrame([normalized])
    probabilities = model.predict_proba(feature_frame[FEATURES])[:, 1]
    probability = float(probabilities[0])
    label = int(probability >= threshold)
    return {
        "predictedProbability": probability,
        "predictedLabel": label,
        "threshold": float(threshold),
    }
