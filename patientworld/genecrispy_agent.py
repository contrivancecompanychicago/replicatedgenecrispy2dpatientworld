"""Local, deterministic sequence and coordinate-file analysis for GENE CRISpy.

This module reports descriptive properties only. It does not interpret variants,
make clinical claims, or send submitted data to an external service.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

MAX_INPUT_BYTES = 5 * 1024 * 1024
DNA_ALPHABET = set("ACGTNRYSWKMBDHV")
RNA_ALPHABET = set("ACGUNRYSWKMBDHV")
PROTEIN_ALPHABET = set("ACDEFGHIKLMNPQRSTVWYBXZJUO*")


class GeneCrispyAgent:
    """A small analysis agent that routes FASTA or PDB text to local tools."""

    def analyze(self, content: str, input_format: str = "auto") -> dict[str, Any]:
        """Analyze FASTA sequence text or PDB coordinate text.

        ``input_format`` may be ``auto``, ``fasta``, or ``pdb``. Input is
        processed locally and is never persisted by this class.
        """
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Input must be non-empty text.")
        if len(content.encode("utf-8")) > MAX_INPUT_BYTES:
            raise ValueError(f"Input exceeds the {MAX_INPUT_BYTES}-byte limit.")

        selected = input_format.lower().strip()
        if selected == "auto":
            selected = _detect_format(content)
        if selected == "fasta":
            result = _analyze_fasta(content)
        elif selected == "pdb":
            result = _analyze_pdb(content)
        else:
            raise ValueError("input_format must be 'auto', 'fasta', or 'pdb'.")

        result["safety_notice"] = (
            "Descriptive research output only; not a diagnosis, clinical interpretation, "
            "or treatment recommendation."
        )
        return result


def _detect_format(content: str) -> str:
    first_line = next((line.strip() for line in content.splitlines() if line.strip()), "")
    if first_line.startswith(">"):
        return "fasta"
    if any(line.startswith(("ATOM  ", "HETATM")) for line in content.splitlines()):
        return "pdb"
    raise ValueError("Could not detect format. Specify 'fasta' or 'pdb'.")


def _analyze_fasta(content: str) -> dict[str, Any]:
    records: list[tuple[str, str]] = []
    identifier: str | None = None
    sequence_parts: list[str] = []

    def finish_record() -> None:
        nonlocal identifier, sequence_parts
        if identifier is not None:
            sequence = "".join(sequence_parts).upper()
            if not sequence:
                raise ValueError(f"FASTA record {identifier!r} has no sequence.")
            records.append((identifier, sequence))
        sequence_parts = []

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith(">"):
            finish_record()
            identifier = line[1:].strip()
            if not identifier:
                raise ValueError(f"FASTA header on line {line_number} is empty.")
        else:
            if identifier is None:
                raise ValueError("FASTA sequence data must follow a '>' header.")
            sequence_parts.append("".join(line.split()))
    finish_record()

    if not records:
        raise ValueError("No FASTA records were found.")
    return {
        "analysis_type": "sequence_descriptive",
        "record_count": len(records),
        "records": [_summarize_sequence(name, sequence) for name, sequence in records],
    }


def _summarize_sequence(identifier: str, sequence: str) -> dict[str, Any]:
    letters = set(sequence)
    if letters <= DNA_ALPHABET:
        molecule_type = "RNA" if "U" in letters else ("DNA" if "T" in letters else "nucleic_acid_unspecified")
        if molecule_type == "RNA" and not letters <= RNA_ALPHABET:
            raise ValueError(f"Sequence {identifier!r} contains symbols invalid for RNA.")
        if molecule_type == "DNA" and not letters <= DNA_ALPHABET:
            raise ValueError(f"Sequence {identifier!r} contains symbols invalid for DNA.")
        counts = Counter(sequence)
        result: dict[str, Any] = {
            "id": identifier,
            "molecule_type": molecule_type,
            "length": len(sequence),
            "composition": dict(sorted(counts.items())),
        }
        if molecule_type in ("DNA", "nucleic_acid_unspecified"):
            canonical = sum(counts.get(base, 0) for base in "ACGT")
            gc = counts.get("G", 0) + counts.get("C", 0)
        else:
            canonical = sum(counts.get(base, 0) for base in "ACGU")
            gc = counts.get("G", 0) + counts.get("C", 0)
        result["gc_percent_of_canonical_bases"] = round(gc * 100 / canonical, 2) if canonical else None
        result["ambiguous_symbol_count"] = len(sequence) - canonical
        return result

    if letters <= PROTEIN_ALPHABET:
        return {
            "id": identifier,
            "molecule_type": "protein",
            "length": len(sequence),
            "composition": dict(sorted(Counter(sequence).items())),
            "stop_symbol_count": sequence.count("*"),
        }

    invalid = "".join(sorted(letters - DNA_ALPHABET - PROTEIN_ALPHABET))
    raise ValueError(f"Sequence {identifier!r} contains unsupported symbols: {invalid!r}.")


def _analyze_pdb(content: str) -> dict[str, Any]:
    atoms = 0
    residues: set[tuple[str, str, str, str]] = set()
    chains: set[str] = set()
    coordinates: list[tuple[float, float, float]] = []

    for line_number, line in enumerate(content.splitlines(), start=1):
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        if len(line) < 54:
            raise ValueError(f"PDB atom record on line {line_number} is too short.")
        try:
            x, y, z = (float(line[start:end]) for start, end in ((30, 38), (38, 46), (46, 54)))
        except ValueError as exc:
            raise ValueError(f"PDB coordinates on line {line_number} are invalid.") from exc
        atoms += 1
        chains.add(line[21:22].strip() or "_")
        residues.add((line[21:22], line[22:26].strip(), line[26:27], line[17:20].strip()))
        coordinates.append((x, y, z))

    if not atoms:
        raise ValueError("No ATOM or HETATM records were found in the PDB input.")
    bounds = {
        axis: {"min": round(min(point[index] for point in coordinates), 3),
               "max": round(max(point[index] for point in coordinates), 3)}
        for index, axis in enumerate(("x", "y", "z"))
    }
    return {
        "analysis_type": "structure_descriptive",
        "format": "pdb",
        "atom_count": atoms,
        "residue_count": len(residues),
        "chain_ids": sorted(chains),
        "coordinate_bounds_angstrom": bounds,
    }


__all__ = ["GeneCrispyAgent", "MAX_INPUT_BYTES"]
