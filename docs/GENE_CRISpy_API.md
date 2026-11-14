# GENE CRISpy FastAPI endpoint

The existing Python FastAPI application exposes a local analysis endpoint:

```http
POST /genecrispy/analyze
Content-Type: application/json
```

Request body:

```json
{
  "content": ">sample gene\nACGTGC\n",
  "input_format": "auto"
}
```

`input_format` accepts `auto`, `fasta`, or `pdb`. Successful responses contain
sequence composition and canonical-base GC percentage for FASTA nucleic acids,
or atom/residue counts, chain IDs, and coordinate bounds for PDB. Invalid or
unsupported input returns HTTP 422. The analyzer applies its 5 MiB input limit.

Run the API from the repository root with:

```bash
uvicorn backend:app --reload
```

Interactive API documentation is available at `/docs`. Analysis runs locally;
submitted sequence/coordinate text is not stored or sent to an external model.
Results are descriptive research output only, not medical or clinical advice.

Run tests with:

```bash
python -m unittest discover -s tests
```
