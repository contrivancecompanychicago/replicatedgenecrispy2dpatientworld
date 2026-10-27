from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from patientworld.ml_pipeline import (
    load_cohort_csv,
    save_model,
    score_dataset,
    train_prediabetes_model,
    train_test_split_data,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and score a prediabetes risk model from CSV data.")
    parser.add_argument("--input", required=True, help="Path to a cohort CSV file.")
    parser.add_argument("--target", default="prediabetes", help="Target column to predict.")
    parser.add_argument("--output", default="artifacts/prediabetes_model.joblib", help="Where to save the model.")
    args = parser.parse_args()

    df = load_cohort_csv(args.input, target_column=args.target)
    train_df, val_df = train_test_split_data(df, test_size=0.2, random_state=42)

    model, metrics, threshold, threshold_metrics = train_prediabetes_model(train_df, val_df, target_column=args.target)
    save_model(model, args.output)

    print("Validation metrics:")
    for key, value in metrics.items():
        print(f"- {key}: {value:.4f}")
    print(f"Selected threshold: {threshold:.4f}")
    print(f"Threshold metrics: {threshold_metrics}")

    sample_predictions = score_dataset(model, val_df.head(10), threshold=threshold)
    print("\nExample predictions:")
    print(sample_predictions[["age", "bmi", "smoking_status", "alcohol_drinks_per_week", "predicted_probability", "predicted_label"]].to_string(index=False))


if __name__ == "__main__":
    main()
