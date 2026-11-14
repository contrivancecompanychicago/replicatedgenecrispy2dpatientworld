# GENE CRISpy Python package

GENE CRISpy is an installable Python package (version **0.2.0**) for local,
descriptive analysis of common genetic sequence and molecular coordinate text.

## Install from a source checkout

```bash
python -m pip install .
```

For the FastAPI service and Firebase integration, install the optional API
dependencies:

```bash
python -m pip install '.[api]'
```

## Use the Python API

```python
from genecrispy import GeneCrispyAgent, __version__

agent = GeneCrispyAgent()
print(__version__)  # 0.2.0
result = agent.analyze(">sample gene\nACGTGC\n")
print(result)
```

The agent supports FASTA DNA/RNA/protein records and PDB coordinate text. Set
`input_format="fasta"` or `input_format="pdb"` to choose a parser explicitly;
`"auto"` detects either format. Input is processed locally, limited to 5 MiB,
and not persisted by the agent. Invalid inputs raise `ValueError`.

## FastAPI service

Install the API extra and run from the repository root:

```bash
python -m pip install '.[api]'
uvicorn backend:app --reload
```

The analysis endpoint is `POST /genecrispy/analyze`; interactive API
documentation is available at `/docs`. The FastAPI metadata declares GENE
CRISpy version 0.2.0.

## Scope and safety

The package reports descriptive properties, such as sequence length,
composition, canonical-base GC percentage, atom/residue counts, chain IDs, and
coordinate bounds. It does not interpret variants, make diagnoses, estimate
clinical risk, or recommend treatment. Results are research output only and
must not be used as clinical advice. This initial package does not call an LLM
or send submitted molecular data to an external service.

## Tests

```bash
python -m unittest discover -s tests
```
