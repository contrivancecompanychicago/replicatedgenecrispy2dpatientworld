# replicatedgenecrispy2dpatientworld

Version 0 prototype for modeling the relationship between smoking, alcohol use, and diabetes risk.

This repository now includes an initial implementation that connects three health signals:

- smoking exposure
- alcohol intake
- diabetes risk

The project is intentionally lightweight and designed as an early-stage research and decision-support prototype. It does not replace clinical diagnosis or formal epidemiological modeling.

## What is included

- A small Python package for risk scoring
- CSV-based analysis for patient or cohort records
- A prototype summary report that highlights combined risk contributors
- Sample patient data to test the workflow

## Project status

- Status: version 0 (prototype / MVP)
- Scope: exploratory health-risk linking
- Intended use: education, prototyping, internal research, and extension toward larger datasets

## Quick start

```bash
python3 -m patientworld.cli --input examples/sample_patients.csv
```

## Example output

The tool reports:

- smoking burden score
- alcohol burden score
- diabetes risk score
- combined association summary
- cohort-level aggregate metrics

## Notes

This prototype is informed by the general literature indicating that smoking and heavy alcohol use are associated with increased risk for metabolic and cardiovascular burden, and that diabetes risk rises when these exposures cluster with higher age, obesity, and other comorbid factors. It is not a validated clinical prediction model.

## Repository goals

This version is a starting point for building a more advanced patient-health model that can later include:

- broader clinical datasets
- machine-learning models
- longitudinal patient tracking
- subgroup analysis by age, sex, and diagnosis
- integration with other risk factors
