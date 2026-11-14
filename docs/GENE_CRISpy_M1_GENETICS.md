# M1 Genetics Foundations

Independent GENE CRISpy study aid mapped to selected public UIC College of Medicine Block 1 objectives. No UIC affiliation or endorsement is implied. This is not the official syllabus, exam preparation assurance, or complete M1/Phase 1 coverage.

## Public sources reviewed 2026-11-14
- https://medicine.uic.edu/education/md/md-curriculum/phase-1-curriculum/
- https://chicago.medicine.uic.edu/education/md/curriculum/phase-1/

Phase 1 spans M1 and M2. UIC places foundational genetics within Block 1 (MDC 601). Public objectives connect inheritance and genetic testing (B1.4), pharmacogenomics (B1.8), evidence appraisal (B1.11), and ethical/structural context (B1.13). These are paraphrased anchors, not a reproduced course syllabus. The Chicago page points to Blackboard for additional course materials.

## Our selected learning connections
| Lesson | Public objective connection | Exercise |
| --- | --- | --- |
| Sequence foundations | B1.4 preparatory foundation | Compare synthetic FASTA base composition |
| Inheritance | B1.4 | Explain a simplified Aa × Aa example |
| Testing limits | B1.4, B1.11 | Identify evidence absent from a file summary |
| Pharmacogenomics | B1.8 | Explain why base counts cannot guide dosing |
| Ethics | B1.13 | Reflect on consent, relatives and access |

The lessons and answers are original GENE CRISpy content. These connections are the project's interpretation of broad public objectives, not UIC's certification of coverage.

## Colab
Open `notebooks/GENE_CRISpy_M1_Genetics.ipynb` in Google Colab. Run cells in order on CPU. It loads the core package directly, without the legacy API/PatientWorld import path. The notebook clones the reviewed main commit into a separate runtime directory and applies the tested source update embedded in the notebook. The notebook contains its matching source update so it can also run when uploaded directly to Colab. Download the optional results bundle and save the notebook to Drive.

## Package
```python
from genecrispy import get_m1_genetics_curriculum, get_genetics_lesson
curriculum = get_m1_genetics_curriculum()
lesson = get_genetics_lesson("inheritance")
```

These functions return fresh dictionaries, make no network requests and collect no learner data. The core version remains 0.2.0; the printed commit identifies this source update.

## Validation and limits
Run `python -m unittest discover -s tests -p 'test_m1_education.py' -v`.
RNA handling now checks the RNA alphabet as well as DNA. Alphabet-based typing remains heuristic: DNA/RNA/protein alphabets overlap, so real molecule identity requires context.
The pre-existing full test suite/API imports remain blocked by unrelated PatientWorld issues. This update does not configure Firebase or repair those paths.
No clinical risk, pathogenicity, genetic testing recommendation, drug/dose selection, CRISPR design, AI interpretation or patient data processing is added.
