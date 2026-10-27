# replicatedgenecrispy2dpatientworld

Version 0 prototype for modeling the relationship between smoking, alcohol use, and diabetes risk.

This repository now includes a machine-learning pipeline for a more formal disease-risk model intended to predict prediabetes risk from smoking and alcohol exposure, with a research-oriented facial-model extension.

## Current status

- Version: 0.1.0 (research prototype)
- Focus: prediabetes risk modeling from lifestyle exposures and optional face-derived features
- Validation: train/validation split included in the workflow
- Scope: exploratory risk modeling and method development, not clinical diagnosis

## Repository goals

This project is designed to evolve in stages:

1. Transparent tabular risk scoring
2. Machine-learning classification with train/validation split
3. Formal disease-risk modeling for prediabetes prediction
4. Facial-model extension using face embedding features when a dataset is available

## Quick start

Generate a synthetic dataset and train a model:

```bash
python3 scripts/generate_training_data.py
python3 scripts/train_prediabetes_model.py
```

You can also run the prototype CLI:

```bash
python3 -m patientworld.cli --input examples/sample_patients.csv
```

## Model workflow

The ML workflow includes:

- data generation for smoking, alcohol, and metabolic-risk signals
- train/validation splitting with stratification
- preprocessing for numeric and categorical variables
- logistic regression classification for prediabetes prediction
- optional facial embedding features in a fusion-style research model

## Formal disease-risk model

The implemented model estimates the probability of prediabetes using exposures such as:

- smoking exposure
- alcohol use
- age
- BMI
- sex
- family history
- optional face-derived features or embeddings

The model is intentionally structured for extension to real healthcare datasets.

## Important limitation

This repository does not yet include a real clinical or facial-image dataset. The facial-model component is a research scaffold that can accept embeddings from a real image model when such data are available. It is not a validated clinical detector.

## Directory structure

- `patientworld/` — model and risk-scoring code
- `scripts/` — dataset generation and training scripts
- `examples/` — sample input files
- `artifacts/` — trained models and metrics

## Next steps

The next layer would include:

- real patient data imports and EHR schema mapping
- external validation with temporal splits
- calibration curves and clinical decision thresholds
- a true face-image pipeline using embeddings from a pretrained vision model
