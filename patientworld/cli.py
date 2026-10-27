from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import csv


@dataclass
class PatientRecord:
    patient_id: str
    age: int
    bmi: float = 0.0
    smoking_status: str = "never"
    pack_years: float = 0.0
    alcohol_drinks_per_week: float = 0.0
    diabetes: bool = False

    @property
    def smoking_label(self) -> str:
        return (self.smoking_status or "never").lower().strip() or "never"

    @property
    def alcohol_label(self) -> str:
        drinks = self.alcohol_drinks_per_week
        if drinks <= 0:
            return "none"
        if drinks <= 7:
            return "light"
        if drinks <= 14:
            return "moderate"
        return "heavy"


@dataclass
class RiskSummary:
    patient_id: str
    smoking_score: float
    alcohol_score: float
    diabetes_risk_score: float
    combined_risk_signal: str


def _normalize_status(value: Optional[str]) -> str:
    if value is None:
        return "never"
    return str(value).lower().strip() or "never"


def smoking_score(smoking_status: Optional[str], pack_years: float = 0.0) -> float:
    """Score smoking burden from 0.0 to 1.0.

    This deliberately uses a simple additive model so that the prototype remains
    transparent and explainable.
    """
    status = _normalize_status(smoking_status)
    pack_years = max(0.0, float(pack_years))

    status_weight = {
        "never": 0.0,
        "former": 0.18,
        "current": 0.32,
    }.get(status, 0.0)

    pack_weight = min(pack_years / 40.0, 1.0) * 0.35
    return round(min(1.0, status_weight + pack_weight), 3)


def alcohol_score(drinks_per_week: float = 0.0) -> float:
    """Score alcohol burden from 0.0 to 1.0."""
    drinks = max(0.0, float(drinks_per_week))
    # Light drinking is low risk; heavy drinking is a stronger contributor.
    if drinks <= 1:
        return 0.0
    if drinks <= 7:
        return round(min(0.35, drinks / 20.0), 3)
    if drinks <= 14:
        return round(min(0.65, 0.35 + (drinks - 7) / 28.0), 3)
    return round(min(1.0, 0.65 + (drinks - 14) / 35.0), 3)


def calculate_diabetes_risk(
    age: int,
    bmi: float,
    smoking_status: Optional[str] = "never",
    pack_years: float = 0.0,
    alcohol_drinks_per_week: float = 0.0,
    diabetes: bool = False,
) -> Dict[str, float]:
    """Return a transparent diabetes-risk signal based on smoking, alcohol, age, and BMI.

    The risk is scaled from 0.0 to 1.0 and is intended for exploratory risk
    communication, not clinical diagnosis.
    """
    age_component = min(1.0, max(0.0, (age - 20) / 80.0)) * 0.30
    bmi_component = min(1.0, max(0.0, (bmi - 18) / 22.0)) * 0.30
    smoking_component = smoking_score(smoking_status, pack_years) * 0.25
    alcohol_component = alcohol_score(alcohol_drinks_per_week) * 0.20

    combined_signal = 0.0
    if smoking_score(smoking_status, pack_years) > 0.35 and alcohol_score(alcohol_drinks_per_week) > 0.35:
        combined_signal = 0.15

    raw_score = age_component + bmi_component + smoking_component + alcohol_component + combined_signal
    if diabetes:
        raw_score += 0.10

    score = max(0.0, min(1.0, raw_score))

    return {
        "age_component": round(age_component, 3),
        "bmi_component": round(bmi_component, 3),
        "smoking_component": round(smoking_component, 3),
        "alcohol_component": round(alcohol_component, 3),
        "combined_signal": round(combined_signal, 3),
        "diabetes_risk_score": round(score, 3),
    }


def summarize_record(record: PatientRecord) -> RiskSummary:
    smoking = smoking_score(record.smoking_status, record.pack_years)
    alcohol = alcohol_score(record.alcohol_drinks_per_week)
    risk = calculate_diabetes_risk(
        age=record.age,
        bmi=record.bmi,
        smoking_status=record.smoking_status,
        pack_years=record.pack_years,
        alcohol_drinks_per_week=record.alcohol_drinks_per_week,
        diabetes=record.diabetes,
    )

    if smoking > 0.35 and alcohol > 0.35:
        combined_risk_signal = "strong combined risk"
    elif smoking > 0.35 or alcohol > 0.35:
        combined_risk_signal = "moderate combined risk"
    else:
        combined_risk_signal = "low combined risk"

    return RiskSummary(
        patient_id=record.patient_id,
        smoking_score=smoking,
        alcohol_score=alcohol,
        diabetes_risk_score=risk["diabetes_risk_score"],
        combined_risk_signal=combined_risk_signal,
    )


def summarize_population(records: Iterable[PatientRecord]) -> Dict[str, float]:
    records = list(records)
    if not records:
        return {
            "average_smoking_score": 0.0,
            "average_alcohol_score": 0.0,
            "average_diabetes_risk": 0.0,
            "diabetes_prevalence": 0.0,
        }

    smoking_scores = [smoking_score(r.smoking_status, r.pack_years) for r in records]
    alcohol_scores = [alcohol_score(r.alcohol_drinks_per_week) for r in records]
    diabetes_scores = [
        calculate_diabetes_risk(
            age=r.age,
            bmi=r.bmi,
            smoking_status=r.smoking_status,
            pack_years=r.pack_years,
            alcohol_drinks_per_week=r.alcohol_drinks_per_week,
            diabetes=r.diabetes,
        )["diabetes_risk_score"]
        for r in records
    ]

    return {
        "average_smoking_score": round(sum(smoking_scores) / len(smoking_scores), 3),
        "average_alcohol_score": round(sum(alcohol_scores) / len(alcohol_scores), 3),
        "average_diabetes_risk": round(sum(diabetes_scores) / len(diabetes_scores), 3),
        "diabetes_prevalence": round(sum(1 for r in records if r.diabetes) / len(records), 3),
    }


def read_patients_csv(path: str) -> List[PatientRecord]:
    """Read patient data from a CSV file.

    Expected columns include:
    - patient_id
    - age
    - bmi
    - smoking_status
    - pack_years
    - alcohol_drinks_per_week
    - diabetes
    """
    result: List[PatientRecord] = []
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            patient = PatientRecord(
                patient_id=row.get("patient_id", "unknown"),
                age=int(float(row.get("age", 0) or 0)),
                bmi=float(row.get("bmi", 0) or 0),
                smoking_status=str(row.get("smoking_status", "never") or "never"),
                pack_years=float(row.get("pack_years", 0) or 0),
                alcohol_drinks_per_week=float(row.get("alcohol_drinks_per_week", 0) or 0),
                diabetes=str(row.get("diabetes", "false")).strip().lower() in {"1", "true", "yes", "y"},
            )
            result.append(patient)
    return result
