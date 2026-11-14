# GENE CRISpy 0.2.0

GENE CRISpy is a Python package and local analysis service for descriptive analysis of genetic sequence text and molecular structure coordinate text.

This repository combines:
- GENE CRISpy, an installable Python package for FASTA and PDB analysis
- PatientWorld compatibility utilities for a patient risk-modeling workflow
- a FastAPI backend exposing the analysis endpoint locally
- optional Firebase/Firestore integration for broader application use
- a Colab-ready quickstart workflow for running the project in a hosted notebook environment

The project is intended for research and descriptive analysis only. It does not diagnose, recommend treatment, or provide clinical interpretation.

## Project status

- Package name: genecrispy
- Version: 0.2.0
- API title: GENE CRISpy
- API version: 0.2.0
- Python requirement: 3.10+

## Repository layout

- genecrispy/ — installable Python package
- patientworld/ — PatientWorld ML utilities and compatibility layer
- backend/ — FastAPI application
- tests/ — unit and API tests
- docs/ — usage and reference guides
- notebooks/ — Colab notebook quickstart
- requirements.txt — base Python dependencies
- pyproject.toml — package metadata and build configuration

## Install from the repo

Install the package in editable mode:

```bash
python -m pip install -e .
```

Install the optional API and test dependencies:

```bash
python -m pip install -e ".[api,test]"
```

## Python usage

```python
from genecrispy import GeneCrispyAgent, __version__

agent = GeneCrispyAgent()
print(__version__)  # 0.2.0

result = agent.analyze(">sample_gene\nACGTGC\n")
print(result)
```

You can also specify the parser explicitly:

```python
result = agent.analyze(">sample_gene\nACGTGC\n", input_format="fasta")
```

For PDB text:

```python
pdb_text = (
    "ATOM      1  N   GLY A   1      11.104  13.207   9.223  1.00 20.00           N\n"
    "ATOM      2  CA  GLY A   1      12.000  14.000  10.000  1.00 20.00           C\n"
)
print(agent.analyze(pdb_text, input_format="pdb"))
```

The agent supports:
- FASTA DNA/RNA/protein records
- PDB coordinate text
- length and composition summaries
- canonical-base GC percentage for nucleic sequences
- atom/residue counts and chain IDs for PDB data

Invalid or unsupported input raises a ValueError.

## Local API

The backend provides a local descriptive analysis endpoint:

```http
POST /genecrispy/analyze
Content-Type: application/json
```

Example request:

```json
{
  "content": ">sample_gene\nACGTGC\n",
  "input_format": "auto"
}
```

Run the API from the repository root:

```bash
python -m pip install -e ".[api]"
uvicorn backend:app --reload
```

Then open the Swagger docs:

```text
http://localhost:8000/docs
```

This endpoint is local-only and does not persist submitted sequence or coordinate text.

## Firebase and backend integration

The repository also includes Firebase-ready patterns for PatientWorld-style workflows, including:
- Firestore save/get helpers
- patient record schema compatibility
- prediction storage and retrieval helpers
- optional Firebase initialization for deployment environments

The backend still supports the original patient-risk model endpoints:
- /health
- /predict
- /patients
- /predict-and-save

These are optional and require a valid Firebase configuration if enabled.

## Google Colab quickstart

A Colab notebook is included in the repo for a browser-based workflow.

### Step-by-step Colab flow

1. Open a new notebook in Google Colab.
2. Clone the repository:

```python
!git clone https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld.git
%cd replicatedgenecrispy2dpatientworld
```

3. Install the project and API/test dependencies:

```python
!python -m pip install -e ".[api,test]"
```

4. Import the package and verify the version:

```python
import genecrispy
from genecrispy import GeneCrispyAgent
print(genecrispy.__version__)
agent = GeneCrispyAgent()
```

5. Analyze a FASTA sample:

```python
result = agent.analyze(">sample_gene\nACGTGC\n")
print(result)
```

6. Analyze a PDB sample:

```python
pdb_text = (
    "ATOM      1  N   GLY A   1      11.104  13.207   9.223  1.00 20.00           N\n"
    "ATOM      2  CA  GLY A   1      12.000  14.000  10.000  1.00 20.00           C\n"
)
print(agent.analyze(pdb_text, input_format="pdb"))
```

7. Exercise the local API with FastAPI's test client:

```python
from fastapi.testclient import TestClient
from backend import app

client = TestClient(app)
response = client.post(
    "/genecrispy/analyze",
    json={"content": ">sample_gene\nACGTGC\n", "input_format": "auto"},
)
print(response.status_code)
print(response.json())
```

8. Run the repo tests:

```bash
python -m unittest discover -s tests -v
```

9. Optional: build a wheel locally:

```bash
python -m pip install build
python -m build --wheel
```

Important Colab security note:
- Colab is a hosted third-party runtime.
- Do not upload sensitive patient, genomic, or credential data to a notebook without explicit authorization.
- Do not place Firebase service-account keys or tokens in notebook cells.

## Safety and scope

This project is intentionally limited to descriptive analysis:
- sequence length
- composition summary
- GC percentage for canonical nucleic bases
- atom/residue count and coordinate bounds for PDB text

It does not:
- diagnose disease
- interpret genomic variants as pathogenic or benign
- provide medical or clinical guidance
- make treatment recommendations
- persist uploaded data outside the runtime unless explicitly configured by the user in a separate environment

All outputs are research-oriented summaries only.

## Tests

Run the included tests with:

```bash
python -m unittest discover -s tests
```

## Versioning

This repo identifies the package and API as:
- Project name: GENE CRISpy
- Package: genecrispy
- Version: 0.2.0

## Notes

This repository is structured to support both research workflows and a lightweight API layer. It is suitable for:
- local sequence and structure analysis
- notebook prototyping in Colab
- integration into an application or service with explicit security controls
- experimentation with genomic and molecular data in a controlled environment

Repository:
https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld.git
