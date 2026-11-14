import unittest
from genecrispy import GeneCrispyAgent, get_m1_genetics_curriculum, get_genetics_lesson


class M1EducationTests(unittest.TestCase):
    def test_snapshot_is_independent_and_source_traceable(self):
        curriculum = get_m1_genetics_curriculum()
        self.assertIn("medicine.uic.edu", curriculum["source_url"])
        self.assertIn("not affiliated", curriculum["notice"])
        curriculum["lessons"][0]["objective_ids"].append("changed")
        self.assertNotIn("changed", get_m1_genetics_curriculum()["lessons"][0]["objective_ids"])

    def test_lesson_lookup_and_unknown_lesson(self):
        self.assertEqual(get_genetics_lesson("inheritance")["objective_ids"], ["B1.4"])
        with self.assertRaises(ValueError):
            get_genetics_lesson("missing")

    def test_rna_and_unresolved_nucleic_acid(self):
        agent = GeneCrispyAgent()
        rna = agent.analyze(">rna\nACGU\n")["records"][0]
        self.assertEqual(rna["molecule_type"], "RNA")
        self.assertEqual(rna["gc_percent_of_canonical_bases"], 50.0)
        ambiguous = agent.analyze(">unknown\nGCGCGC\n")["records"][0]
        self.assertEqual(ambiguous["molecule_type"], "nucleic_acid_unspecified")

    def test_original_samples_and_protein(self):
        agent = GeneCrispyAgent()
        records = agent.analyze(">A\nACGTGC\n>B\nATATAT\n>C\nGCGCGC\n")["records"]
        self.assertEqual([r["gc_percent_of_canonical_bases"] for r in records], [66.67, 0.0, 100.0])
        self.assertEqual(agent.analyze(">protein\nMPEPTIDE\n")["records"][0]["molecule_type"], "protein")


if __name__ == "__main__":
    unittest.main()
