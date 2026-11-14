# GENE CRISpy 0.2.0

GENE CRISpy is a Python package and local analysis service for **descriptive analysis** of genetic sequence text and molecular structure coordinate text. This guide is written for first-time users and starts with a safe, sample-data workflow in Google Colab.

> **Important: GENE CRISpy 0.2.0 is not an AI model or an AI-powered interpretation system.** The current analyzer uses deterministic Python code to summarize supported FASTA and PDB text. It does not use an LLM, search biological databases, identify variants, explain disease, diagnose, or recommend treatment. Do not treat the output as clinical guidance.

## Quick Start for first-time users

The easiest way to try GENE CRISpy is the included Google Colab notebook. It uses sample data, so you can learn the workflow without uploading personal or patient data.

### 1. Open the notebook

Open the [GENE CRISpy Colab Quickstart notebook](https://colab.research.google.com/github/contrivancecompanychicago/replicatedgenecrispy2dpatientworld/blob/main/notebooks/GENE_CRISpy_Colab_Quickstart.ipynb) in Google Colab. Alternatively, in Colab choose **File → Open notebook → GitHub** and enter this repository URL:

```text
https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld
```

Choose `notebooks/GENE_CRISpy_Colab_Quickstart.ipynb` from the results.

### 2. Run notebook cells from top to bottom

In Colab, choose **Runtime → Run all**, or run each cell using its play button. The notebook will:

1. Clone this repository into the temporary Colab runtime.
2. Install GENE CRISpy and the optional API/test dependencies.
3. Import the package and show its version (`0.2.0`).
4. Analyze example FASTA and PDB text.
5. Send an example request to the API in-process using FastAPI's test client.
6. Run the tests and optionally build a Python wheel.

No Firebase credentials, API key, public web server, or GPU are needed for these examples. The notebook does not publish the package or deploy the service.

### 3. Understand what the sample results mean

- **FASTA** is a plain-text format for biological sequences. The current tool reports sequence type, length, symbol composition, and canonical-base GC percentage for nucleic acids.
- **PDB** is a text format for molecular structure coordinates. The current tool reports basic atom/residue counts, chain IDs, and coordinate bounds.
- These are file summaries, not biological interpretation, structural validation, or predictions.

### 4. Protect your data

Google Colab runs on a hosted third-party service. For your first use, stick to the synthetic examples in the notebook. Do not upload identifiable, private, patient, or sensitive genomic data unless you have verified that you are authorized to use that data with Colab and have reviewed applicable privacy requirements. Never paste passwords, access tokens, or Firebase service-account keys into notebook cells.

For more details, see [the Colab guide](docs/GENE_CRISpy_COLAB.md) and [the package guide](docs/GENE_CRISpy_PYTHON_PACKAGE.md).

## What this repository contains

- `genecrispy/` — installable GENE CRISpy Python package
- `patientworld/` — PatientWorld ML utilities and compatibility code
- `backend/` — FastAPI application and `/genecrispy/analyze` endpoint
- `tests/` — package and API tests
- `notebooks/` — Google Colab quickstart notebook
- `docs/` — usage guides
- `pyproject.toml` — package metadata and build configuration

The repository also includes optional Firebase/Firestore integration patterns. They are separate from the local GENE CRISpy sequence/structure analysis workflow.

## Install and use locally

Python 3.10 or later is required. From the repository root, install the package:

```bash
python -m pip install .
```

To install optional FastAPI and test dependencies as well:

```bash
python -m pip install ".[api,test]"
```

Use the Python API:

```python
from genecrispy import GeneCrispyAgent, __version__

print(__version__)  # 0.2.0
agent = GeneCrispyAgent()

result = agent.analyze(">sample_gene\nACGTGC\n")
print(result)
```

`input_format` can be `"auto"`, `"fasta"`, or `"pdb"`. The parser has a 5 MiB input limit. Invalid or unsupported input raises `ValueError`.

## Local FastAPI endpoint

The API exposes a descriptive analysis route:

```http
POST /genecrispy/analyze
Content-Type: application/json
```

Example JSON request:

```json
{
  "content": ">sample_gene\nACGTGC\n",
  "input_format": "auto"
}
```

Run the development server from the repository root:

```bash
python -m pip install ".[api]"
uvicorn backend:app --reload
```

Open `http://localhost:8000/docs` to try the endpoint interactively. Invalid input returns HTTP 422. The analysis route runs the local analyzer and does not persist the submitted sequence or coordinate text. Do not expose a development server publicly without appropriate authentication and security controls.

The FastAPI metadata identifies the service as **GENE CRISpy 0.2.0**. Existing PatientWorld routes (`/health`, `/predict`, `/patients`, and `/predict-and-save`) are also present; patient persistence and prediction workflows may require Firebase configuration.

## Tests

Run the test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

## Package build (optional)

Build a wheel locally; this does not publish it to PyPI:

```bash
python -m pip install build
python -m build --wheel
```

## Scope and safety

GENE CRISpy 0.2.0 reports descriptive file properties only. It does not:

- use artificial intelligence or an LLM to interpret results
- annotate genes or variants from an external database
- classify variants as pathogenic or benign
- diagnose disease, estimate clinical risk, or recommend treatment
- replace a qualified genetics professional, clinician, or molecular biologist

Do not use these summaries to make healthcare decisions. The software processes input locally in the analysis function; deployments, notebooks, or surrounding applications may have their own data handling and retention behavior, which you should review separately.

## Version and project information

- Project name: GENE CRISpy
- Python import/package name: `genecrispy`
- Version: `0.2.0`
- Supported Python: 3.10+
- Repository: <https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld>
