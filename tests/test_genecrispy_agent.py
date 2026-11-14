import unittest

from patientworld.genecrispy_agent import GeneCrispyAgent


class GeneCrispyAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = GeneCrispyAgent()

    def test_analyzes_fasta_sequence_descriptively(self):
        result = self.agent.analyze(">sample gene\nACGTGC\n")
        record = result["records"][0]
        self.assertEqual(result["analysis_type"], "sequence_descriptive")
        self.assertEqual(record["molecule_type"], "DNA")
        self.assertEqual(record["length"], 6)
        self.assertEqual(record["gc_percent_of_canonical_bases"], 66.67)
        self.assertIn("not a diagnosis", result["safety_notice"])

    def test_analyzes_protein_fasta(self):
        result = self.agent.analyze(">protein\nMKWV\n", input_format="fasta")
        self.assertEqual(result["records"][0]["molecule_type"], "protein")
        self.assertEqual(result["records"][0]["length"], 4)

    def test_rejects_invalid_sequence_symbols(self):
        with self.assertRaisesRegex(ValueError, "unsupported symbols"):
            self.agent.analyze(">bad\nACGT?\n", input_format="fasta")

    def test_analyzes_pdb_atom_and_structure_summary(self):
        line = "ATOM      1  N   GLY A   1      11.104  13.207   9.223  1.00 20.00           N"
        result = self.agent.analyze(line + "\n")
        self.assertEqual(result["atom_count"], 1)
        self.assertEqual(result["residue_count"], 1)
        self.assertEqual(result["chain_ids"], ["A"])
        self.assertEqual(result["coordinate_bounds_angstrom"]["x"]["min"], 11.104)

    def test_rejects_unknown_format(self):
        with self.assertRaisesRegex(ValueError, "Could not detect format"):
            self.agent.analyze("some arbitrary text")


if __name__ == "__main__":
    unittest.main()
