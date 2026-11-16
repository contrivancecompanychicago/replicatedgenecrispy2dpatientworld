"""Read and render a bundled subset of KEGG KGML pathway data."""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

_PATHWAY_ID = re.compile(r"^hsa\d{5}$")
_MAX_KGML_BYTES = 1024 * 1024
_PATHWAY_DIR = Path(__file__).resolve().parent.parent / "data" / "pathways"
_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "data" / "schemas" / "pathway-response.schema.json"


class PathwayNotFoundError(FileNotFoundError):
    """Raised when a pathway is not bundled with the application."""


def load_pathway_schema() -> dict[str, Any]:
    """Load the JSON Schema describing pathway API responses."""
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def list_pathways() -> list[dict[str, str]]:
    """List the bundled KGML pathways with basic metadata."""
    pathways: list[dict[str, str]] = []
    for xml_path in sorted(_PATHWAY_DIR.glob("*.xml")):
        try:
            root = ET.fromstring(xml_path.read_bytes())
        except ET.ParseError:
            continue
        pathways.append(
            {
                "pathway_id": xml_path.stem,
                "title": root.get("title", xml_path.stem),
                "organism": root.get("org", ""),
            }
        )
    return pathways


def load_pathway(pathway_id: str) -> dict[str, Any]:
    """Return a descriptive JSON-ready summary of a bundled KGML file."""
    if not _PATHWAY_ID.fullmatch(pathway_id):
        raise ValueError("pathway_id must be a KEGG human pathway ID, e.g. hsa04930.")

    path = _PATHWAY_DIR / f"{pathway_id}.xml"
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise PathwayNotFoundError(pathway_id) from exc
    if len(raw) > _MAX_KGML_BYTES:
        raise ValueError("Pathway KGML exceeds the 1 MiB size limit.")

    root = ET.fromstring(raw)
    entries: list[dict[str, Any]] = []
    for element in root.findall("entry"):
        graphics = element.find("graphics")
        item: dict[str, Any] = {
            "id": element.get("id", ""),
            "name": element.get("name", ""),
            "type": element.get("type", "other"),
        }
        if graphics is not None:
            item["label"] = graphics.get("name", item["name"])
            for key in ("x", "y", "width", "height"):
                value = graphics.get(key)
                if value is not None:
                    item[key] = int(value)
        entries.append(item)

    relations = []
    for element in root.findall("relation"):
        relations.append({
            "entry1": element.get("entry1", ""),
            "entry2": element.get("entry2", ""),
            "type": element.get("type", "other"),
            "subtypes": [
                {"name": subtype.get("name", ""), "value": subtype.get("value", "")}
                for subtype in element.findall("subtype")
            ],
        })

    if not root.get("title") or not entries:
        raise ValueError("KGML is missing a pathway title or entries.")
    return {
        "pathway_id": pathway_id,
        "title": root.get("title"),
        "organism": root.get("org", ""),
        "entries": entries,
        "gene_count": sum(entry["type"] == "gene" for entry in entries),
        "compound_count": sum(entry["type"] == "compound" for entry in entries),
        "relations": relations,
        "relation_count": len(relations),
        "safety_notice": "Reference pathway data only; not patient-specific or clinical interpretation.",
    }


def render_pathway_svg(pathway: dict[str, Any]) -> str:
    """Render a compact, self-contained SVG suitable for a Colab HTML cell."""
    nodes = {
        entry["id"]: entry for entry in pathway["entries"]
        if all(key in entry for key in ("x", "y"))
    }
    lines = []
    for relation in pathway["relations"]:
        source = nodes.get(relation["entry1"])
        target = nodes.get(relation["entry2"])
        if source and target:
            lines.append(
                f'<line x1="{source["x"]}" y1="{source["y"]}" '
                f'x2="{target["x"]}" y2="{target["y"]}" '
                'stroke="#667085" stroke-width="1.5" marker-end="url(#arrow)" />'
            )

    shapes = []
    for node in nodes.values():
        label = html.escape(node.get("label", node["name"]))
        width, height = node.get("width", 52), node.get("height", 22)
        x, y = node["x"] - width / 2, node["y"] - height / 2
        if node["type"] == "gene":
            shape = (f'<rect x="{x:g}" y="{y:g}" width="{width}" height="{height}" '
                     'rx="2" fill="#bfffbf" stroke="#344054"/>')
        else:
            shape = (f'<ellipse cx="{node["x"]}" cy="{node["y"]}" '
                     f'rx="{max(width / 2, 5):g}" ry="{max(height / 2, 5):g}" '
                     'fill="#fff" stroke="#344054"/>')
        shapes.append(shape + f'<text x="{node["x"]}" y="{node["y"] + 4}" '
                       f'text-anchor="middle" font-size="11">{label}</text>')

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 820" '
        'role="img" aria-label="KEGG pathway graph" style="width:100%;height:auto">'
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" '
        'refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#667085"/>'
        '</marker></defs><rect width="100%" height="100%" fill="white"/>'
        + "".join(lines) + "".join(shapes) + "</svg>"
    )


def render_pathway_html(pathway: dict[str, Any]) -> str:
    title = html.escape(pathway["title"])
    notice = html.escape(pathway["safety_notice"])
    return (
        '<div style="font-family:Arial,sans-serif;max-width:900px">'
        f'<h3>{title} ({html.escape(pathway["pathway_id"])})</h3>'
        f'{render_pathway_svg(pathway)}'
        f'<p style="color:#475467;font-size:12px">{notice}</p></div>'
    )


__all__ = [
    "PathwayNotFoundError",
    "list_pathways",
    "load_pathway",
    "load_pathway_schema",
    "render_pathway_html",
    "render_pathway_svg",
]
