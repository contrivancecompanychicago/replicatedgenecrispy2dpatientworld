# GENE CRISpy in Google Colab

A runnable, cell-by-cell Colab notebook for GENE CRISpy 0.2.0 is available here:

- [Open the quickstart notebook on GitHub](https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld/blob/main/notebooks/GENE_CRISpy_Colab_Quickstart.ipynb)
- In GitHub, choose **Open in Colab** (or open Colab and use **File → Open notebook → GitHub** and paste the repository URL).

## What the notebook walks through

1. Clone the repository into the Colab runtime.
2. Install the editable Python package and optional API/test dependencies.
3. Import GENE CRISpy and verify version 0.2.0.
4. Run descriptive example analysis on FASTA and PDB samples.
5. Call `POST /genecrispy/analyze` in-process using FastAPI's `TestClient`.
6. Check invalid-input handling and run the test suite.
7. Optionally build a wheel without publishing it.

The notebook avoids public tunnels and does not configure Firebase. Colab is a hosted third-party runtime: do not upload sensitive patient/genomic data or place credentials in notebook cells. The analyses are descriptive research output, not clinical interpretation or medical advice.
