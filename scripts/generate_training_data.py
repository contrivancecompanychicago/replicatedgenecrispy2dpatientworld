from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TABULAR_FEATURES = [
    "age",
    "bmi",
    "pack_years",
    "alcohol_drinks_per_week",
    "family_history",
    "sleep_hours",
    "waist_circumference",
    "blood_pressure",
    "sex",
    "smoking_status",
]

FACE_FEATURES = [f"face_embedding_{i}" for i in range(1, 9)]
TARGET = "prediabetes"


class FacePrediabetesModel:
    def __init__(self) -> None:
        self.model: Pipeline | None = None

    def fit(self, df: pd.DataFrame) -> "FacePrediabetesModel":
        X = df[TABULAR_FEATURES + FACE_FEATURES]
        y = df[TARGET]

        numeric_cols = [c for c in TABULAR_FEATURES if c not in {"sex", "smoking_status"}] + FACE_FEATURES
        categorical_cols = ["sex", "smoking_status"]

        numeric_transformer = Pipeline(
            steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
        )
        categorical_transformer = Pipeline(
            steps=[("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_cols),
                ("cat", categorical_transformer, categorical_cols),
            ]
        )

        self.model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced")),
            ]
        )
        self.model.fit(X, y)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model has not been fit yet.")
        return self.model.predict_proba(df[TABULAR_FEATURES + FACE_FEATURES])[:, 1]

    def evaluate(self, df: pd.DataFrame) -> Dict[str, float]:
        if self.model is None:
            raise ValueError("Model has not been fit yet.")
        y_true = df[TARGET]
        probs = self.predict_proba(df)
        preds = (probs >= 0.5).astype(int)
        return {
            "roc_auc": float(roc_auc_score(y_true, probs)),
            "accuracy": float(accuracy_score(y_true, preds)),
            "precision": float(precision_score(y_true, preds, zero_division=0)),
            "recall": float(recall_score(y_true, preds, zero_division=0)),
            "f1": float(f1_score(y_true, preds, zero_division=0)),
        }


def train_face_model(train_df: pd.DataFrame, val_df: pd.DataFrame) -> Tuple[FacePrediabetesModel, Dict[str, float]]:
    model = FacePrediabetesModel().fit(train_df)
    metrics = model.evaluate(val_df)
    return model, metrics


def save_face_model(model: FacePrediabetesModel, output_path: str | Path) -> None:
    folder = Path(output_path).parent
    folder.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
