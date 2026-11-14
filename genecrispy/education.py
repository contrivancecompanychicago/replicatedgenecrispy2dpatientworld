"""Independent study support mapped to public UIC Phase 1 objectives.

Mappings are GENE CRISpy's interpretation, not UIC-authored teaching content.
No network calls, patient assessment, genetic testing recommendations or AI.
"""
from copy import deepcopy

SOURCE_URL = "https://medicine.uic.edu/education/md/md-curriculum/phase-1-curriculum/"
SOURCE_REVIEWED = "2026-11-14"
NOTICE = (
    "Independent GENE CRISpy study aid; not affiliated with or endorsed by UIC. "
    "Public-objective mapping only, not a complete syllabus or clinical interpretation."
)
_LESSONS = [
    {
        "id": "sequence_foundations",
        "title": "DNA, RNA and base composition",
        "objective_ids": ["B1.4"],
        "mapping": "Preparatory foundation for genetics; sequence composition is not a disease-risk measure.",
        "explanation": (
            "DNA uses A, C, G and T; RNA uses A, C, G and U. "
            "GC percentage describes the fraction of canonical bases that are G or C. "
            "A short sequence containing neither T nor U may not distinguish DNA from RNA. "
            "Sequence alphabets can also overlap with protein alphabets."
        ),
        "reflection": "Why can GCGCGC have 100% GC without establishing whether it is DNA or RNA?",
        "answer": "G and C occur in both DNA and RNA; molecule identity requires additional context.",
    },
    {
        "id": "inheritance",
        "title": "Inheritance and family history",
        "objective_ids": ["B1.4"],
        "mapping": "Study inheritance principles using a deliberately simplified example.",
        "explanation": (
            "In a simple autosomal recessive Aa by Aa model, each parent contributes "
            "A or a with equal probability. Offspring genotype probabilities are "
            "AA: 25%, Aa: 50%, aa: 25%. This assumes Mendelian segregation; "
            "phenotype also depends on the model's penetrance and other assumptions. "
            "This is not a calculation for an actual family."
        ),
        "reflection": "Does one child's genotype change the probabilities for the next independent conception?",
        "answer": "No. Under these assumptions the genotype probabilities are the same for each conception.",
    },
    {
        "id": "testing_limits",
        "title": "Genetic testing and evidence limits",
        "objective_ids": ["B1.4", "B1.11"],
        "mapping": "Discuss what additional evidence a testing question needs; do not select a test for a patient.",
        "explanation": (
            "A FASTA summary does not identify a gene or a pathogenic variant. "
            "Interpretation needs context such as a reference sequence, genomic location, "
            "validated methods and appropriate evidence. Clinical assessment also needs "
            "personal and family history, consent and professional review."
        ),
        "reflection": "Can matching GC percentages establish that two sequences have the same function?",
        "answer": "No. Matching composition does not establish sequence identity, function or clinical significance.",
    },
    {
        "id": "pharmacogenomics",
        "title": "Pharmacogenomics as a learning connection",
        "objective_ids": ["B1.8"],
        "mapping": "Conceptual connection only; no drug or dose recommendations.",
        "explanation": (
            "Inherited variation can influence drug handling or response. "
            "A descriptive sequence summary cannot establish a pharmacogenomic phenotype "
            "or determine a medication or dose."
        ),
        "reflection": "What is missing between counting bases and predicting a drug response?",
        "answer": "Validated variant identification, relevant evidence and clinical context, among other requirements.",
    },
    {
        "id": "ethics",
        "title": "Genetics, consent and equitable access",
        "objective_ids": ["B1.13"],
        "mapping": "Reflect on ethical and structural factors in genetics education.",
        "explanation": (
            "Genetic information can affect relatives as well as the person tested. "
            "Educational workflows should consider consent, privacy, uncertainty and "
            "barriers to counseling or testing. These exercises use synthetic data."
        ),
        "reflection": "Why should consent and privacy be considered before sharing genetic data?",
        "answer": "Genetic data can reveal sensitive information about individuals and biological relatives.",
    },
]


def get_m1_genetics_curriculum():
    """Return a fresh, JSON-serializable curriculum snapshot."""
    return {
        "title": "GENE CRISpy M1 Genetics Foundations",
        "source_url": SOURCE_URL,
        "source_reviewed": SOURCE_REVIEWED,
        "notice": NOTICE,
        "coverage": "Selected Block 1 connections only; not full Phase 1 or M1 coverage.",
        "lessons": deepcopy(_LESSONS),
    }


def get_genetics_lesson(lesson_id):
    """Return one lesson, raising ValueError for an unknown ID."""
    for lesson in _LESSONS:
        if lesson["id"] == lesson_id:
            return deepcopy(lesson)
    raise ValueError(f"Unknown genetics lesson: {lesson_id!r}")
