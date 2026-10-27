# replicatedgenecrispy2dpatientworld

Version 0 prototype for modeling relationships between smoking, alcohol use, diabetes, and prediabetes risk.

## What is implemented now

This repository now includes:

1. Real CSV ingestion workflow for hospital or cohort datasets
2. Train/validation split for model development
3. Probability calibration using a calibrated logistic model
4. Threshold selection to convert risk scores into binary predictions
5. A research-oriented face-feature extension for later use with facial embeddings

## Why these steps matter

Step 1: real CSV ingestion
- Lets you use real hospital or cohort tables instead of only synthetic toy data.
- Handles common naming variants for age, BMI, smoking, and alcohol columns.
- Standardizes inputs so the model can consume the data reliably.

Step 2: train/validation split
- Reserves a validation set to check whether the model is learning useful patterns.
- Prevents overfitting and gives a more honest estimate of performance.

Step 3: probability calibration
- Raw model probabilities can be poorly calibrated.
- Calibration adjusts the risk score so it matches real-world probabilities more closely.
- This is important when using the output as a risk estimate rather than a simple flag.

Step 4: thresholding
- Once probabilities are calibrated, you choose a cutoff such as 0.30, 0.40, or 0.50.
- This decides when a patient is flagged as high risk versus low risk.
- Threshold choice depends on your clinical or operational goal: sensitivity, specificity, or balanced performance.

## Quick start

Generate synthetic data and train a model:

```bash
python3 scripts/generate_training_data.py
python3 scripts/train_prediabetes_model.py
```

Train on a real cohort CSV:

```bash
python3 -m patientworld.cli --input path/to/cohort.csv --target prediabetes --output artifacts/prediabetes_model.joblib
```

The CSV should include columns such as:

- age
- bmi
- smoking_status
- pack_years
- alcohol_drinks_per_week
- sex
- family_history
- sleep_hours
- waist_circumference
- blood_pressure
- prediabetes (or diabetes)

## Example workflow

1. Load the CSV with `load_cohort_csv()`
2. Split into train/validation partitions
3. Train a logistic-risk model
4. Calibrate probabilities
5. Select a threshold using the validation set
6. Save the model
7. Score new patients

## Important limitation

This is still a research prototype. A real facial-model component is not yet connected to actual patient photographs or a validated image dataset. It is a research scaffold for later expansion.

## Project version

Version 0.1.0
