"""FastAPI backend for the PatientWorld model and Firestore persistence."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from patientworld.firebase_backend import PatientWorldFirestoreClient, predict_patient_record

app = FastAPI(title="UICPAVLS PatientWorld Backend", version="0.1.0")

_firebase_client: Optional[PatientWorldFirestoreClient] = None


class PatientPayload(BaseModel):
    patientId: str = Field(..., description="Unique patient identifier")
    age: Optional[float] = 45.0
    bmi: Optional[float] = 27.5
    pack_years: Optional[float] = 0.0
    alcohol_drinks_per_week: Optional[float] = 0.0
    family_history: Optional[int] = 0
    sleep_hours: Optional[float] = 7.0
    waist_circumference: Optional[float] = 90.0
    blood_pressure: Optional[float] = 120.0
    sex: Optional[str] = "unknown"
    smoking_status: Optional[str] = "never"
    face_embedding_1: Optional[float] = 0.0
    face_embedding_2: Optional[float] = 0.0
    face_embedding_3: Optional[float] = 0.0
    face_embedding_4: Optional[float] = 0.0
    face_embedding_5: Optional[float] = 0.0
    face_embedding_6: Optional[float] = 0.0
    face_embedding_7: Optional[float] = 0.0
    face_embedding_8: Optional[float] = 0.0


class PredictionRequest(PatientPayload):
    threshold: Optional[float] = 0.5


@app.on_event("startup")
def startup() -> None:
    global _firebase_client
    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    if service_account:
        try:
            _firebase_client = PatientWorldFirestoreClient(service_account_path=service_account, project_id=project_id)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Failed to initialize Firebase client: {exc}") from exc


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: PredictionRequest) -> Dict[str, Any]:
    record = payload.model_dump(exclude_none=True)
    result = predict_patient_record(record, threshold=float(payload.threshold or 0.5))
    return {
        "patientId": payload.patientId,
        **result,
    }


@app.post("/patients")
def save_patient(payload: PatientPayload) -> Dict[str, Any]:
    if _firebase_client is None:
        raise HTTPException(status_code=503, detail="Firebase Firestore is not configured.")

    record = payload.model_dump(exclude_none=True)
    saved = _firebase_client.save_patient(payload.patientId, record)
    return {"patientId": payload.patientId, "saved": saved}


@app.post("/predict-and-save")
def predict_and_save(payload: PredictionRequest) -> Dict[str, Any]:
    if _firebase_client is None:
        raise HTTPException(status_code=503, detail="Firebase Firestore is not configured.")

    record = payload.model_dump(exclude_none=True)
    prediction = predict_patient_record(record, threshold=float(payload.threshold or 0.5))
    firestore_payload = {
        "patientId": payload.patientId,
        **record,
        **prediction,
    }
    _firebase_client.save_patient(payload.patientId, firestore_payload)
    prediction_doc = _firebase_client.save_prediction(
        patient_id=payload.patientId,
        predicted_probability=prediction["predictedProbability"],
        predicted_label=prediction["predictedLabel"],
        threshold=prediction["threshold"],
        metadata={"source": "fastapi"},
    )
    return {"patientId": payload.patientId, "prediction": prediction, "stored": prediction_doc}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
