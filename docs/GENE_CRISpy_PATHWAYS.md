# GENE CRISpy 0.2.0

GENE CRISpy is a Python package and local analysis service for **descriptive analysis** of genetic sequence text and molecular structure coordinate text. This guide is written for first-time users [...]

> **Important: GENE CRISpy 0.2.0 is not an AI model or an AI-powered interpretation system.** The current analyzer uses deterministic Python code to summarize supported FASTA and PDB text. It does [...]

## KEGG pathway API

A compact, offline KGML excerpt for the human Type II diabetes pathway is bundled for read-only exploration. `GET /pathways/hsa04930` returns its entries and relationships as JSON; `GET /pathways/hsa04930/render` serves an SVG visualization that can be displayed in Google Colab. See [the pathway and Colab guide](docs/GENE_CRISpy_PATHWAYS.md) for a notebook snippet and limitations. This is reference data, not patient-specific interpretation.
