from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = [
    "age",
    "bmi",
    "pack_years",
    "alcohol_drinks_per_week",
    "family_history",
    "sleep_hours",
    "waist_circumference",
    "blood_pressure",
]

CATEGORICAL_FEATURES = ["sex", "smoking_status"]
OPTIONAL_FACE_FEATURES = [
    "face_embedding_1",
    "face_embedding_2",
    "face_embedding_3",
    "face_embedding_4",
    "face_embedding_5",
    "face_embedding_6",
    "face_embedding_7",
    "face_embedding_8",
]
TARGET_COLUMN = "prediabetes"

COLUMN_ALIASES = {
    "age": ["age", "patient_age", "age_years"],
    "bmi": ["bmi", "body_mass_index", "bmi_value"],
    "smoking_status": ["smoking_status", "smoker_status", "tobacco_status", "current_smoker"],
    "pack_years": ["pack_years", "smoking_pack_years", "packs_year"],
    "alcohol_drinks_per_week": ["alcohol_drinks_per_week", "drinks_per_week", "alcohol_use_per_week"],
    "sex": ["sex", "gender"],
    "family_history": ["family_history", "diabetes_family_history"],
    "sleep_hours": ["sleep_hours", "hours_sleep"],
    "waist_circumference": ["waist_circumference", "waist_cm"],
    "blood_pressure": ["blood_pressure", "systolic_bp", "bp"],
    "prediabetes": ["prediabetes", "prediabetes_flag", "diabetes_risk", "outcome"],
    "diabetes": ["diabetes", "diabetes_status", "has_diabetes"],
}


def _normalize_target(value: object) -> int:
    if pd.isna(value):
        return 0
    value = str(value).strip().lower()
    if value in {"1", "true", "yes", "y", "positive", "case"}:
        return 1
    if value in {"0", "false", "no", "n", "negative", "control"}:
        return 0
    try:
        return int(float(value))
    except ValueError:
        return 0


def normalize_smoking_status(value: object) -> str:
    if pd.isna(value):
        return "never"
    lowered = str(value).strip().lower()
    mapping = {
        "never": "never",
        "non-smoker": "never",
        "nonsmoker": "never",
        "former": "former",
        "previous": "former",
        "ex-smoker": "former",
        "current": "current",
        "smoker": "current",
        "active": "current",
        "yes": "current",
    }
    return mapping.get(lowered, lowered)


def normalize_sex(value: object) -> str:
    if pd.isna(value):
        return "unknown"
    lowered = str(value).strip().lower()
    if lowered in {"m", "male", "man"}:
        return "male"
    if lowered in {"f", "female", "woman"}:
        return "female"
    if lowered in {"other", "nonbinary", "nb"}:
        return "other"
    return lowered


def _resolve_column_name(columns: Iterable[str], candidates: Sequence[str]) -> Optional[str]:
    normalized = {str(c).strip().lower(): c for c in columns}
    for candidate in candidates:
        key = str(candidate).strip().lower()
        if key in normalized:
            return normalized[key]
    return None


def load_cohort_csv(
    path: str | Path,
    target_column: str = TARGET_COLUMN,
    required_columns: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Load a hospital or cohort dataset and standardize columns to the model schema.

    This is the real-data ingestion workflow. It supports common hospital CSV
    naming conventions and converts labels into the expected model-ready form.
    """
    data = pd.read_csv(path)
    columns = list(data.columns)

    required = list(required_columns or [
        "age",
        "bmi",
        "smoking_status",
        "pack_years",
        "alcohol_drinks_per_week",
        "sex",
        "family_history",
        "sleep_hours",
        "waist_circumference",
        "blood_pressure",
    ])

    resolved = {}
    for field in required:
        alias_candidates = COLUMN_ALIASES.get(field, [field])
        resolved[field] = _resolve_column_name(columns, alias_candidates)

    missing = [field for field in required if resolved[field] is None]
    if missing:
        raise ValueError(f"Missing required columns for model input: {missing}")

    for field, source in resolved.items():
        if field == "prediabetes":
            continue
        data[field] = data[source]

    # target mapping
    target_name = _resolve_column_name(columns, COLUMN_ALIASES.get(target_column, [target_column]))
    if target_name is None:
        if target_column in {"prediabetes", "diabetes"} and "diabetes" in columns:
            target_name = "diabetes"
        else:
            raise ValueError(f"Could not find target column: {target_column}")

    if target_column not in data.columns:
        data[target_column] = data[target_name]
    data[target_column] = data[target_column].map(_normalize_target)

    if "smoking_status" in data.columns:
        data["smoking_status"] = data["smoking_status"].map(normalize_smoking_status)
    if "sex" in data.columns:
        data["sex"] = data["sex"].map(normalize_sex)

    # Fill common blank labels and cast numerics
    numeric_cols = [
        "age",
        "bmi",
        "pack_years",
        "alcohol_drinks_per_week",
        "family_history",
        "sleep_hours",
        "waist_circumference",
        "blood_pressure",
    ]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    data["smoking_status"] = data.get("smoking_status", "never").fillna("never")
    data["sex"] = data.get("sex", "unknown").fillna("unknown")

    if "prediabetes" in data.columns:
        data["prediabetes"] = data["prediabetes"].map(_normalize_target)

    return data


def create_synthetic_dataset(path: str | Path, n_samples: int = 2000, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic prediabetes dataset with lifestyle and face-like features."""
    rng = np.random.default_rng(seed)

    sex = rng.choice(["male", "female"], size=n_samples, p=[0.52, 0.48])
    smoking_status = rng.choice(["never", "former", "current"], size=n_samples, p=[0.45, 0.25, 0.30])
    age = rng.integers(20, 75, size=n_samples)
    bmi = rng.normal(27.5, 5.0, size=n_samples)
    bmi = np.clip(bmi, 18.0, 45.0)
    pack_years = rng.gamma(2.0, 12.0, size=n_samples)
    alcohol_drinks = rng.gamma(1.6, 6.0, size=n_samples)
    family_history = rng.binomial(1, 0.25, size=n_samples)
    sleep_hours = rng.normal(7.0, 1.2, size=n_samples)
    sleep_hours = np.clip(sleep_hours, 4.0, 10.0)
    waist_circumference = rng.normal(90.0, 15.0, size=n_samples)
    waist_circumference = np.clip(waist_circumference, 60.0, 140.0)
    blood_pressure = rng.normal(120.0, 18.0, size=n_samples)
    blood_pressure = np.clip(blood_pressure, 90.0, 170.0)

    smoking_factor = np.where(smoking_status == "never", 0.0, np.where(smoking_status == "former", 0.7, 1.5))
    alcohol_factor = np.log1p(alcohol_drinks) / 2.5

    linear_score = (
        0.03 * age
        + 0.18 * (bmi - 25)
        + 0.6 * smoking_factor
        + 0.8 * alcohol_factor
        + 0.9 * family_history
        + 0.2 * (waist_circumference - 90) / 10
        + 0.05 * (blood_pressure - 120) / 10
        - 0.15 * (sleep_hours - 7)
    )
    prob = 1 / (1 + np.exp(-linear_score))
    prediabetes = rng.random(n_samples) < prob

    face_embedding = np.column_stack([
        rng.normal(0.3, 0.15, size=n_samples),
        rng.normal(0.2, 0.12, size=n_samples),
        rng.normal(0.25, 0.14, size=n_samples),
        rng.normal(0.28, 0.1, size=n_samples),
        rng.normal(0.35, 0.12, size=n_samples),
        rng.normal(0.4, 0.1, size=n_samples),
        0.2 + 0.4 * prob + rng.normal(0.0, 0.05, size=n_samples),
        0.1 + 0.5 * prob + rng.normal(0.0, 0.05, size=n_samples),
    ])

    df = pd.DataFrame(
        {
            "sex": sex,
            "smoking_status": smoking_status,
            "age": age,
            "bmi": bmi,
            "pack_years": pack_years,
            "alcohol_drinks_per_week": alcohol_drinks,
            "family_history": family_history,
            "sleep_hours": sleep_hours,
            "waist_circumference": waist_circumference,
            "blood_pressure": blood_pressure,
            "prediabetes": prediabetes.astype(int),
            **{f"face_embedding_{i + 1}": face_embedding[:, i] for i in range(8)},
        }
    )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def train_test_split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_df, val_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df[TARGET_COLUMN],
    )
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True)


def build_prediabetes_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    features = NUMERIC_FEATURES + OPTIONAL_FACE_FEATURES + CATEGORICAL_FEATURES
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES + OPTIONAL_FACE_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def evaluate_model(model: Pipeline, X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, float]:
    probabilities = model.predict_proba(X_val)[:, 1]
    predictions = model.predict(X_val)

    return {
        "roc_auc": float(roc_auc_score(y_val, probabilities)),
        "brier_score": float(brier_score_loss(y_val, probabilities)),
        "accuracy": float(accuracy_score(y_val, predictions)),
        "precision": float(precision_score(y_val, predictions, zero_division=0)),
        "recall": float(recall_score(y_val, predictions, zero_division=0)),
        "f1": float(f1_score(y_val, predictions, zero_division=0)),
    }


def select_probability_threshold(y_true: pd.Series, probabilities: np.ndarray) -> Tuple[float, Dict[str, float]]:
    """Select the threshold that maximizes the Youden J statistic.

    This is a common calibration + thresholding step in risk classification.
    """
    thresholds = np.linspace(0.05, 0.95, 181)
    best_threshold = 0.5
    best_score = -1.0
    best_metrics: Dict[str, float] = {}

    y_true = np.asarray(y_true).astype(int)
    for threshold in thresholds:
        preds = (probabilities >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, preds)
        sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
        specificity = tn / (tn + fp) if (tn + fp) else 0.0
        j_stat = sensitivity + specificity - 1.0
        if j_stat > best_score:
            best_score = float(j_stat)
            best_threshold = float(threshold)
            best_metrics = {
                "threshold": float(threshold),
                "sensitivity": float(sensitivity),
                "specificity": float(specificity),
                "youden_j": float(j_stat),
            }

    return best_threshold, best_metrics


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[int, int, int, int]:
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    return tn, fp, fn, tp


def calibrate_probability_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    method: str = "sigmoid",
) -> Tuple[Pipeline, Dict[str, float], float, Dict[str, float]]:
    """Fit a base logistic regression pipeline, calibrate probabilities, and return metrics and threshold."""
    base_model = build_prediabetes_pipeline()
    base_model.fit(X_train, y_train)

    calibrator = CalibratedClassifierCV(estimator=base_model, method=method, cv=3)
    calibrator.fit(X_train, y_train)

    probabilities = calibrator.predict_proba(X_val)[:, 1]
    threshold, threshold_metrics = select_probability_threshold(y_val, probabilities)

    pred_labels = (probabilities >= threshold).astype(int)
    metrics = {
        "roc_auc": float(roc_auc_score(y_val, probabilities)),
        "brier_score": float(brier_score_loss(y_val, probabilities)),
        "accuracy": float(accuracy_score(y_val, pred_labels)),
        "precision": float(precision_score(y_val, pred_labels, zero_division=0)),
        "recall": float(recall_score(y_val, pred_labels, zero_division=0)),
        "f1": float(f1_score(y_val, pred_labels, zero_division=0)),
        "threshold": float(threshold),
    }
    return calibrator, metrics, threshold, threshold_metrics


def train_prediabetes_model(train_df: pd.DataFrame, val_df: pd.DataFrame, target_column: str = TARGET_COLUMN) -> Tuple[Pipeline, Dict[str, float], float, Dict[str, float]]:
    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES + OPTIONAL_FACE_FEATURES
    if target_column not in train_df.columns:
        raise ValueError(f"Target column '{target_column}' not found in training data.")

    X_train = train_df[features]
    y_train = train_df[target_column].astype(int)
    X_val = val_df[features]
    y_val = val_df[target_column].astype(int)

    calibrator, metrics, threshold, threshold_metrics = calibrate_probability_model(X_train, y_train, X_val, y_val)
    return calibrator, metrics, threshold, threshold_metrics


def save_model(model: Pipeline, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_and_prepare_data(data_path: str | Path, target_column: str = TARGET_COLUMN) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Convenience wrapper for hospital/cohort ingestion plus train/validation split."""
    df = load_cohort_csv(data_path, target_column=target_column)
    train_df, val_df = train_test_split_data(df, test_size=0.2, random_state=42)
    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES + OPTIONAL_FACE_FEATURES
    X_train = train_df[feature_cols]
    y_train = train_df[target_column].astype(int)
    X_val = val_df[feature_cols]
    y_val = val_df[target_column].astype(int)
    return train_df, val_df, X_train, y_train, X_val, y_val


def score_dataset(model: Pipeline, df: pd.DataFrame, threshold: Optional[float] = None) -> pd.DataFrame:
    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES + OPTIONAL_FACE_FEATURES
    probabilities = model.predict_proba(df[features])[:, 1]
    output = df.copy()
    output["predicted_probability"] = probabilities
    output["predicted_label"] = (probabilities >= (threshold if threshold is not None else 0.5)).astype(int)
    return output


if __name__ == "__main__":
    print("patientworld.ml_pipeline")
