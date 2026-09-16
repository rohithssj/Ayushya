"""
Metadata & Extracted Text Integrity Validation Test.

Ensures that every chunk in the processed corpus matches its document metadata
and that no document's extracted text contradicts its metadata (e.g. CBD containing Indian law).
"""

import json
import os
import unittest
from pathlib import Path


class TestMetadataValidation(unittest.TestCase):

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parents[4]
        self.processed_dir = self.base_dir / "data" / "processed"
        self.manifest_path = self.base_dir / "data" / "metadata" / "resource_manifest.json"

    def test_resource_manifest_exists(self):
        self.assertTrue(self.manifest_path.exists(), f"Resource manifest not found: {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertIsInstance(manifest, list)
        self.assertGreater(len(manifest), 0)

    def test_cbd_metadata_and_text_integrity(self):
        """CBD 1992 document MUST be International jurisdiction and contain CBD text, NOT Indian Biological Diversity Act."""
        cbd_chunk_file = self.processed_dir / "international_cbd_convention_1992_chunks.json"
        self.assertTrue(cbd_chunk_file.exists(), "CBD chunks file missing!")

        with open(cbd_chunk_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        self.assertGreater(len(chunks), 0, "CBD chunks are empty")
        for chunk in chunks:
            self.assertEqual(chunk.get("jurisdiction", "").lower(), "international", f"CBD chunk {chunk['chunk_id']} has non-international jurisdiction!")
            self.assertEqual(chunk.get("document_id"), "international_cbd_convention_1992")
            text = chunk.get("text", "").lower()
            # Must not contain Indian statutory short title header
            self.assertNotIn("biological diversity act, 2002", text, f"CBD chunk {chunk['chunk_id']} contains Indian Biological Diversity Act text!")
            self.assertNotIn("national biodiversity authority", text, f"CBD chunk {chunk['chunk_id']} contains Indian National Biodiversity Authority text!")

    def test_all_processed_chunks_match_jurisdiction_and_domain(self):
        """All chunks across processed JSON files must have valid jurisdiction and non-empty metadata."""
        chunk_files = list(self.processed_dir.glob("*_chunks.json"))
        self.assertGreater(len(chunk_files), 0, "No processed chunk files found!")

        for chunk_file in chunk_files:
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            if not chunks:
                continue
            for chunk in chunks:
                jur = chunk.get("jurisdiction", "").lower()
                self.assertIn(jur, ["india", "international"], f"Invalid jurisdiction '{jur}' in chunk {chunk.get('chunk_id')}")
                self.assertTrue(chunk.get("document_id"), f"Missing document_id in {chunk.get('chunk_id')}")
                self.assertTrue(chunk.get("title"), f"Missing title in {chunk.get('chunk_id')}")


if __name__ == "__main__":
    unittest.main()
