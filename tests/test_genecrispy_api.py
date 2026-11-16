import unittest

from fastapi.testclient import TestClient

from backend import app


class GeneCrispyEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_analyzes_fasta(self):
        response = self.client.post(
            "/genecrispy/analyze",
            json={"content": ">sample\nACGTGC\n"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["analysis_type"], "sequence_descriptive")
        self.assertEqual(body["records"][0]["length"], 6)
        self.assertIn("not a diagnosis", body["safety_notice"])

    def test_invalid_sequence_returns_422(self):
        response = self.client.post(
            "/genecrispy/analyze",
            json={"content": ">invalid\nACGT?\n", "input_format": "fasta"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("unsupported symbols", response.json()["detail"])

    def test_rejects_unsupported_input_format(self):
        response = self.client.post(
            "/genecrispy/analyze",
            json={"content": "sequence", "input_format": "xml"},
        )
        self.assertEqual(response.status_code, 422)

    def test_gets_pathway_summary_in_genecrispy_namespace(self):
        response = self.client.get("/genecrispy/pathways/hsa04930")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["title"], "Type II diabetes mellitus")
        self.assertGreater(body["gene_count"], 0)
        self.assertGreater(body["relation_count"], 0)
        self.assertEqual(body["relations"][0]["entry1"], "17")
        self.assertIn("not patient-specific", body["safety_notice"])

    def test_gets_pathway_response_schema(self):
        response = self.client.get("/genecrispy/pathways/schema")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("relation", schema["$defs"])
        relation = schema["$defs"]["relation"]
        self.assertEqual(relation["properties"]["entry1"]["type"], "string")
        self.assertIn("subtypes", relation["required"])

    def test_renders_pathway_as_colab_ready_html(self):
        response = self.client.get("/genecrispy/pathways/hsa04930/render")
        self.assertEqual(response.status_code, 200)
        self.assertIn("image/svg+xml", response.text)
        self.assertIn("Type II diabetes mellitus", response.text)

    def test_unknown_pathway_returns_404(self):
        response = self.client.get("/genecrispy/pathways/hsa00000")
        self.assertEqual(response.status_code, 404)

    def test_pathway_id_is_validated(self):
        response = self.client.get("/genecrispy/pathways/../../README")
        self.assertIn(response.status_code, (404, 422))


if __name__ == "__main__":
    unittest.main()
