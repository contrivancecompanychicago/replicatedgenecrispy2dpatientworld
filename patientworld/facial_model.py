from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
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


def create_synthetic_dataset(path: str | Path, n_samples: int = 2000, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic prediabetes dataset that includes smoking, alcohol, and facial-style embeddings."""
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

    df.to_csv(path, index=False)
    return df


def train_test_split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_df, val_df = train_test_split(df, test_size=test_size, random_state=random_state, stratify=df[TARGET_COLUMN])
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
        "accuracy": float(accuracy_score(y_val, predictions)),
        "precision": float(precision_score(y_val, predictions, zero_division=0)),
        "recall": float(recall_score(y_val, predictions, zero_division=0)),
        "f1": float(f1_score(y_val, predictions, zero_division=0)),
    }


def train_prediabetes_model(train_df: pd.DataFrame, val_df: pd.DataFrame) -> Tuple[Pipeline, Dict[str, float]]:
    X_train = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + OPTIONAL_FACE_FEATURES]
    y_train = train_df[TARGET_COLUMN]
    X_val = val_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + OPTIONAL_FACE_FEATURES]
    y_val = val_df[TARGET_COLUMN]

    model = build_prediabetes_pipeline()
    model.fit(X_train, y_train)
    metrics = evaluate_model(model, X_val, y_val)
    return model, metrics


def save_model(model: Pipeline, output_path: str | Path) -> None:
    folder = Path(output_path).parent
    folder.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
