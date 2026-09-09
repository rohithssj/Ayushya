import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestRetrievalApi(unittest.TestCase):
    """Test suite for Phase 5 Retrieval API validation, bridge, and response shape."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path(__file__).resolve().parents[4]
        venv_python = cls.base_dir / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            cls.python_exe = str(venv_python)
        else:
            cls.python_exe = sys.executable
        cls.script_path = cls.base_dir / "scripts" / "retrieve_hybrid_api.py"

    def run_bridge(self, query: str, jurisdiction: str, domain: str = None, top_k: int = 5):
        cmd = [
            self.python_exe,
            str(self.script_path),
            "--query",
            query,
            "--jurisdiction",
            jurisdiction,
            "--top-k",
            str(top_k),
        ]
        if domain:
            cmd.extend(["--domain", domain])

        import os
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        proc = subprocess.run(
            cmd,
            cwd=str(self.base_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        if proc.returncode != 0:
            print("STDERR:", proc.stderr, file=sys.stderr)
            print("STDOUT:", proc.stdout, file=sys.stderr)
        return proc

    def test_valid_request(self):
        proc = self.run_bridge("patentability of herbal formulation", "India", "patents", top_k=3)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["query"], "patentability of herbal formulation")
        self.assertEqual(data["jurisdiction_filter"], "India")
        self.assertEqual(data["domain_filter"], "patents")
        self.assertEqual(data["retrieval_method"], "hybrid_rrf")
        self.assertEqual(data["top_k"], 3)
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)
        self.assertIn("evidence_strength", data)
        self.assertIn(data["evidence_strength"], ("strong", "moderate", "weak", "insufficient"))
        self.assertIn("abstention_recommended", data)
        self.assertIsInstance(data["abstention_recommended"], bool)
        self.assertIn("requires_human_review", data)
        self.assertIsInstance(data["requires_human_review"], bool)
        self.assertIn("evidence_assessment", data)
        self.assertIn("reasons", data["evidence_assessment"])

    def test_filters(self):
        proc = self.run_bridge("ayurveda aahara labelling requirements", "India", "ayurveda-aahar", top_k=2)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["domain_filter"], "ayurveda-aahar")
        for res in data["results"]:
            self.assertEqual(res["jurisdiction"], "India")
            self.assertEqual(res["domain"], "ayurveda-aahar")

    def test_response_metadata_preservation(self):
        proc = self.run_bridge("biodiversity access benefit sharing", "India", "biodiversity", top_k=2)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        data = json.loads(proc.stdout)
        results = data["results"]
        self.assertGreater(len(results), 0)
        first = results[0]
        self.assertIn("chunk_id", first)
        self.assertIn("document_id", first)
        self.assertIn("title", first)
        self.assertIn("jurisdiction", first)
        self.assertIn("domain", first)
        self.assertIn("text", first)
        self.assertIn("relevance_score", first)
        self.assertIn("lexical_rank", first)
        self.assertIn("semantic_rank", first)
        self.assertIn("matched_terms", first)

        self.assertNotIn("embedding", first)
        self.assertNotIn("vector", first)

    def test_no_results_behavior(self):
        proc = self.run_bridge("xyz123nonexistentterm", "International", "gi", top_k=5)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(len(data["results"]), 0)
        self.assertEqual(data["evidence_strength"], "insufficient")
        self.assertTrue(data["abstention_recommended"])
        self.assertTrue(data["requires_human_review"])


if __name__ == "__main__":
    unittest.main()
