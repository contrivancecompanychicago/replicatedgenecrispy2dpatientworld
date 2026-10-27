"""PatientWorld package for version 0 risk analysis.

This package provides a lightweight model for exploring relationships between
smoking, alcohol consumption, and diabetes risk.
"""

from .risk_model import (
    PatientRecord,
    RiskSummary,
    calculate_diabetes_risk,
    summarize_population,
    read_patients_csv,
)

__all__ = [
    "PatientRecord",
    "RiskSummary",
    "calculate_diabetes_risk",
    "summarize_population",
    "read_patients_csv",
]

__version__ = "0.0.0"
