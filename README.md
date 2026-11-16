# GENE CRISpy 0.2.0

GENE CRISpy is a Python package and local API for descriptive analysis of genetic sequence text and molecular-structure coordinate text. The repository also contains PatientWorld utilities and a read-only API for exploring a bundled KEGG pathway reference excerpt.

> **Scope:** GENE CRISpy is not an AI-powered interpretation system. Its sequence and structure analyzer reports descriptive properties; the pathway routes serve reference data. These features do not diagnose disease, interpret patient variants, estimate clinical risk, or recommend treatment.

## What’s in this repository

- `genecrispy/` — installable GENE CRISpy package, including FASTA/PDB summaries and pathway helpers
- `patientworld/` — PatientWorld ML utilities and compatibility code
- `backend/` — FastAPI application
- `data/pathways/` — bundled KGML pathway reference data
- `data/schemas/` — JSON Schema for pathway API responses
- `tests/` — package and API tests
- `notebooks/` — Google Colab quickstart
- `docs/` — usage guides, including [KEGG pathways and Colab](docs/GENE_CRISpy_PATHWAYS.md)

PatientWorld prediction and optional Firebase/Firestore workflows are separate from the GENE CRISpy sequence/structure analyzer and pathway reference API.

## Install and run

Python 3.10 or later is required. From the repository root:

```bash
python -m pip install ".[api,test]"
uvicorn backend:app --reload
```

Open `http://localhost:8000/docs` to explore the API documentation. Do not expose a development server publicly without appropriate authentication and security controls.

## Sequence and structure analysis

Use the Python API locally:

```python
from genecrispy import GeneCrispyAgent

agent = GeneCrispyAgent()
result = agent.analyze(">sample_gene\nACGTGC\n")
print(result)
```

The analyzer accepts FASTA sequence text or PDB coordinate text. `input_format` may be `"auto"`, `"fasta"`, or `"pdb"`; the input limit is 5 MiB. Results include basic summaries such as sequence type, length, composition, GC percentage for nucleic acids, or atom/residue counts and coordinate bounds for PDB. Input is processed locally by the analysis function and is not persisted by that function.

The API endpoint is `POST /genecrispy/analyze`. Example request:

```json
{
  "content": ">sample_gene\\nACGTGC\\n",
  "input_format": "auto"
}
```

Unsupported input returns HTTP 422. For details, see [the API guide](docs/GENE_CRISpy_API.md).

## KEGG pathway reference API

A compact, offline KGML excerpt for the human Type II diabetes mellitus pathway (`hsa04930`) is bundled for read-only exploration. All pathway routes use the `/genecrispy/pathways` namespace:

| Method and route | Purpose |
| --- | --- |
| `GET /genecrispy/pathways` | List bundled pathways and basic metadata. |
| `GET /genecrispy/pathways/{pathway_id}` | Get pathway metadata, entries, and relations as JSON. |
| `GET /genecrispy/pathways/{pathway_id}/render` | Get a self-contained HTML page with a basic SVG graph, suitable for Colab display. |
| `GET /genecrispy/pathways/schema` | Get the JSON Schema for pathway responses. |

For example, with the server running locally:

```bash
curl http://localhost:8000/genecrispy/pathways
curl http://localhost:8000/genecrispy/pathways/hsa04930
curl http://localhost:8000/genecrispy/pathways/schema
```

The response schema is also stored at `data/schemas/pathway-response.schema.json`. Each relation has `entry1` and `entry2` identifiers referring to pathway entry IDs, a KGML relation `type`, and a list of `subtypes`. A relation can connect genes, compounds, or other pathway entries; it should not automatically be interpreted as a gene-to-gene relationship. The schema describes response structure and does not by itself validate that every relation endpoint resolves to an entry.

### Display the pathway in Google Colab

The API needs to be reachable from the Colab runtime. Colab cannot connect to a server available only at `localhost` on your computer. Use a protected, reachable development deployment or an appropriately secured temporary tunnel.

```python
import requests
from IPython.display import HTML, display

API_BASE = "https://your-reachable-api.example"  # no trailing slash
response = requests.get(
    f"{API_BASE}/genecrispy/pathways/hsa04930/render", timeout=30
)
response.raise_for_status()
display(HTML(response.text))
```

For structured data:

```python
pathway = requests.get(
    f"{API_BASE}/genecrispy/pathways/hsa04930", timeout=30
).json()
print(pathway["title"], pathway["gene_count"], pathway["relation_count"])
```

See [the full pathway guide](docs/GENE_CRISpy_PATHWAYS.md) for additional usage notes.

**Important limitations:** The bundled file is a compact pathway excerpt, not necessarily the complete KEGG map. The API serves locally bundled data and does not fetch KEGG at request time. It does not annotate patient genes or variants, and it does not feed the PatientWorld prediction model. Check KEGG’s terms before redistributing pathway data or images. Do not submit identifiable patient information or sensitive genomic/clinical data to hosted notebooks or unprotected services.

## Tests

Run the test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

## Safety and intended use

- FASTA/PDB outputs are descriptive file summaries, not biological interpretation or structural validation.
- The pathway is static reference information, not patient-specific evidence or a clinical interpretation.
- This software does not classify variants as pathogenic or benign, diagnose disease, estimate clinical risk, or recommend treatment.
- Do not use the outputs to make healthcare decisions.
- Google Colab is a hosted third-party service. Use synthetic examples unless you have reviewed the data-handling and privacy requirements for your use case.

Deployments, notebooks, and surrounding applications may have data-handling behavior beyond the local analysis function; review those separately.

## Project information

- Project name: GENE CRISpy
- Python import/package name: `genecrispy`
- Version: `0.2.0`
- Supported Python: 3.10+
- Repository: <https://github.com/contrivancecompanychicago/replicatedgenecrispy2dpatientworld>
