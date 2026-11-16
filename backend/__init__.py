"""FastAPI backend for GENE CRISpy 0.2.0 and PatientWorld."""

from __future__ import annotations

import os
from typing import Any, Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from patientworld.firebase_backend import PatientWorldFirestoreClient, predict_patient_record
from patientworld.genecrispy_agent import GeneCrispyAgent
from genecrispy.pathway import (
    PathwayNotFoundError,
    load_pathway,
    load_pathway_schema,
    render_pathway_html,
)

app = FastAPI(title="GENE CRISpy", version="0.2.0", description="GENE CRISpy genetic and molecular structure analysis API")

_firebase_client: Optional[PatientWorldFirestoreClient] = None
_genecrispy_agent = GeneCrispyAgent()


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


class GeneCrispyAnalysisRequest(BaseModel):
    """Sequence or coordinate text to analyze locally."""

    content: str = Field(..., min_length=1, description="FASTA sequence or PDB coordinate text")
    input_format: Literal["auto", "fasta", "pdb"] = Field(
        default="auto", description="Input format, or auto-detect FASTA/PDB"
    )


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


@app.post("/genecrispy/analyze")
def analyze_genecrispy(payload: GeneCrispyAnalysisRequest) -> Dict[str, Any]:
    """Return a descriptive FASTA or PDB summary; input is not persisted."""
    try:
        return _genecrispy_agent.analyze(payload.content, input_format=payload.input_format)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/genecrispy/pathways/schema")
def get_pathway_schema() -> Dict[str, Any]:
    """Return the JSON Schema for pathway summaries and KGML relationships."""
    return load_pathway_schema()


@app.get("/genecrispy/pathways/{pathway_id}")
def get_pathway(pathway_id: str) -> Dict[str, Any]:
    """Return descriptive metadata, entries, and relations for a bundled KEGG pathway."""
    try:
        return load_pathway(pathway_id)
    except PathwayNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Pathway {pathway_id!r} is not bundled.") from exc
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/genecrispy/pathways/{pathway_id}/render", response_class=HTMLResponse)
def render_pathway(pathway_id: str) -> HTMLResponse:
    """Return a self-contained SVG pathway page that can be displayed in Colab."""
    try:
        return HTMLResponse(content=render_pathway_html(load_pathway(pathway_id)))
    except PathwayNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Pathway {pathway_id!r} is not bundled.") from exc
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/predict")
def predict(payload: PredictionRequest) -> Dict[str, Any]:
    record = payload.model_dump(exclude_none=True)
    result = predict_patient_record(record, threshold=float(payload.threshold or 0.5))
    return {"patientId": payload.patientId, **result}


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
    firestore_payload = {"patientId": payload.patientId, **record, **prediction}
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

    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
