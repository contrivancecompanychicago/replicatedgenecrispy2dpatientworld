# PatientWorld + UICPAVLS Firebase Integration

This repository contains the PatientWorld risk-modeling package and a Firebase/Firestore-ready backend integration for the UICPAVLS project.

The project combines:
- PatientWorld Python ML workflow for patient risk prediction
- Firestore as the database layer for patient records and prediction results
- Gemini as the natural-language explanation layer for patient summaries and risk education
- Firebase Functions and/or a lightweight backend API for orchestration

This repository is designed for a clinical or care-support workflow where patient data can be stored in Firestore, scored by the PatientWorld model, and summarized by Gemini in patient-friendly language.

Project goals:
- keep the Python model logic in this repository
- keep Firestore as the backend data store
- use Firebase Functions to trigger Gemini summaries when new prediction records are created
- provide a structure that can be connected to a Firebase app or a web/mobile frontend

## Repository overview

The package includes ML utilities for:
- loading and normalizing cohort data
- creating a synthetic dataset
- training a prediabetes risk model
- calibrating probability models
- scoring patient records
- exporting model artifacts

Core modules:
- patientworld/cli.py — primary ML pipeline and patient data handling
- patientworld/facial_model.py — face-feature model experiments
- patientworld/ml_pipeline.py — compatibility layer and workflow access
- patientworld/firebase_backend.py — Firestore-ready model and patient helpers
- backend/main.py — FastAPI backend for prediction endpoints
- backend/__init__.py — backend package entrypoint

## Architecture

The recommended architecture for UICPAVLS is:

1. Patient data is stored in Firestore
2. The backend reads patient data and runs the PatientWorld model
3. Prediction records are saved into Firestore
4. A Firestore trigger calls Gemini
5. Gemini produces a patient-friendly summary and stores it in Firestore
6. The frontend app reads the summary for display

This is the intended flow:

- patients/collection
- predictions/collection
- insights/collection

## Firestore schema

Recommended collections:

patients/{patientId}
- age
- sex
- bmi
- smoking_status
- alcohol_drinks_per_week
- sleep_hours
- blood_pressure
- waist_circumference
- family_history
- createdAt

predictions/{predictionId}
- patientId
- predictedProbability
- predictedLabel
- threshold
- source
- createdAt

insights/{predictionId}
- patientId
- predictionId
- summary
- generatedAt
- modelVersion

## Gemini prompt for UICPAVLS

The recommended Gemini prompt is:

You are the UICPAVLS clinical support assistant for a patient risk assessment and education platform.

Your role is to:
- review the patient’s health and lifestyle data
- summarize risk-relevant information in clear, patient-friendly language
- identify possible risk factors associated with prediabetes, diabetes, or lifestyle-related chronic disease
- suggest evidence-based lifestyle coaching and prevention steps
- ask for missing information only when necessary
- maintain safety, empathy, and nonjudgmental communication

Important rules:
- Do not diagnose.
- Do not prescribe treatment.
- Do not replace a licensed clinician.
- If the information is incomplete, say so clearly.
- If severe symptoms are described, advise the user to contact a healthcare professional or emergency services immediately.
- Keep the tone supportive and understandable.

Use only the data provided. If values are missing, say “Missing data” and ask for them.

Return output in this format:
1. Patient Summary
2. Risk Signals Identified
3. Lifestyle Advice
4. Recommended Next Steps
5. Missing Information Needed
6. Safety Note

Keep all answers plain-language and easy to understand.

## Firebase setup

1. Create or open your Firebase project
2. Enable Firestore Database
3. Enable Firebase Functions
4. Add the Firebase web app if needed
5. Install the Firebase CLI

Commands:

npm install -g firebase-tools
firebase login
firebase init

Choose the Firebase services you need for your project, including:
- Firestore
- Functions
- Hosting if desired
- Storage if desired

## Secret setup for Gemini

Set the Gemini API key as a Firebase secret:

firebase functions:secrets:set GEMINI_API_KEY

This keeps the key out of client code and away from direct browser exposure.

## Quick start

Clone the repository:

git clone https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld.git
cd replicatedgenecrispy2dpatientworld

Install dependencies:

pip install -r requirements.txt

Optional backend runtime dependencies include:
- firebase-admin
- fastapi
- uvicorn

## Running the backend

The backend is designed to provide prediction endpoints and Firebase integration.

Start the API locally:

uvicorn backend.main:app --reload

This exposes endpoints such as:
- /health
- /predict
- /patients
- /predict-and-save

## Firestore + Gemini pipeline

The recommended pipeline is:

1. Save a patient record to Firestore
2. A backend service reads the patient record and runs PatientWorld model logic
3. Save the prediction results to Firestore
4. A Firestore trigger calls Gemini
5. Gemini writes a patient-friendly summary to Firestore
6. The app reads the summary and displays it to the user

This is the core orchestration pattern for UICPAVLS.

## Model capabilities

The repo includes utilities for:
- dataset normalization
- synthetic data generation
- feature engineering
- on-demand prediction scoring
- probability threshold selection
- model calibration
- optional face-feature experiments

It is intended to be a data-science and model-engine layer for patient risk estimation, rather than a standalone Firebase app by itself.

## Notes on architecture

This repository should be thought of as the risk-model engine, while Firestore acts as the operational data store. The app is not simply “the repo as a database”; rather, the repo provides the model logic and backend service, while Firebase provides the persistent runtime storage and trigger workflow.

## Security guidance

For production usage:
- store model keys and API keys in environment variables or Firebase secrets
- do not expose sensitive credentials in frontend bundles
- use Firestore security rules to restrict access to patient records
- authenticate API and frontend access appropriately
- validate patient inputs before model inference

## Existing implementation included in this repo

This repository includes a Firestore-friendly backend and compatibility layer, including:
- patientworld/ml_pipeline.py compatibility exports
- patientworld/firebase_backend.py for Firestore and model orchestration
- backend/main.py for FastAPI endpoints
- Firebase-ready integration patterns for Gemini-triggered summaries

## Summary

This project is a Python-based patient risk model integrated with Firebase/UICPAVLS infrastructure. The long-term intended design is:

- Firestore for data persistence
- PatientWorld model for risk prediction
- Firebase Functions triggers for orchestration
- Gemini for plain-language patient explanation and coaching support

This setup is well suited for a patient-facing digital care platform where model predictions must be stored, reviewed, explained, and surfaced in an understandable way.

## Repository information

Repository:
https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld.git

This README reflects the combined workflow discussed across the implementation and Firebase integration steps: PatientWorld model logic, Firestore backend, and Gemini summarization pipeline for UICPAVLS.
