# GENE CRISpy local analysis agent

This adds an initial, deterministic agent for descriptive analysis of common
sequence and structure text files. It currently supports:

- FASTA: one or more DNA, RNA, or protein records; length and symbol composition;
  canonical-base GC percentage for nucleic acids.
- PDB: atom and residue counts, chain IDs, and coordinate bounds in angstroms.

The agent is deliberately local-only: it does not call an LLM, access the
network, persist submitted sequence data, or infer variant pathogenicity,
clinical risk, diagnoses, or treatment. Its output is a research-oriented
summary and should not be used for clinical decisions. Inputs are limited to
5 MiB. PDB output is a basic coordinate-file summary, not a structural
validation or molecular-dynamics result.

## Python usage

```python
from patientworld.genecrispy_agent import GeneCrispyAgent

agent = GeneCrispyAgent()
result = agent.analyze(">sample\nACGTGC\n")  # auto-detects FASTA
print(result)
```

Pass `input_format="fasta"` or `input_format="pdb"` to select the parser
explicitly. Invalid or unsupported input raises `ValueError`. This initial
version is a Python module rather than an HTTP endpoint; API integration should
be added only with authentication, strict input validation, and an explicit
privacy/data-retention policy.

Run the focused tests with:

```bash
python -m unittest discover -s tests
```
