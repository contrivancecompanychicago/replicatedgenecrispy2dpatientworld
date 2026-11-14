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


if __name__ == "__main__":
    unittest.main()
