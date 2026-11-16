# GENE CRISpy pathway API and Colab display

The API bundles a compact, offline KGML excerpt for the human KEGG Type II diabetes mellitus pathway (`hsa04930`). All pathway routes live under the `/genecrispy/pathways` namespace:

- `GET /genecrispy/pathways` returns the list of bundled pathways and their metadata.
- `GET /genecrispy/pathways/hsa04930` returns pathway metadata, entries, and relations as JSON.
- `GET /genecrispy/pathways/hsa04930/render` returns a self-contained HTML page containing an SVG graph.
- `GET /genecrispy/pathways/schema` returns the JSON Schema for pathway responses, including relation endpoints and subtype fields. The schema is also stored at `data/schemas/pathway-response.schema.json`.

KGML relations use `entry1` and `entry2` identifiers that reference `entries[].id`; their `type` identifies the KGML relation class, and `subtypes` carry details such as activation, inhibition, or phosphorylation. A relation may connect genes, compounds, or other pathway entries, so the schema describes KGML pathway relationships rather than asserting every relation is gene-to-gene. The schema validates structure; it does not currently enforce that every relationship endpoint resolves to an entry ID.

The bundled KGML excerpt is for pathway exploration only. The graph is reference visualization, not patient-specific data, a risk prediction, or clinical interpretation. Only pathways present under `data/pathways/` are available. The parser limits XML size and validates IDs; it does not fetch KEGG or external DTDs at request time.

## Display the graph in Google Colab

The API must be running at a URL reachable from the Colab runtime. Colab cannot reach a server running only on your laptop's `localhost`.

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

To inspect the structured pathway data and schema:

```python
pathway = requests.get(
    f"{API_BASE}/genecrispy/pathways/hsa04930", timeout=30
).json()
pathways = requests.get(f"{API_BASE}/genecrispy/pathways", timeout=30).json()
schema = requests.get(f"{API_BASE}/genecrispy/pathways/schema", timeout=30).json()
print(pathways["count"], pathway["title"], pathway["gene_count"], pathway["relation_count"])
```

Do not put patient identifiers or private genomic/clinical data in these requests. These routes serve static reference data and do not accept or analyze patient information.
