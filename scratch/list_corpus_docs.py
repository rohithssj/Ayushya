import json
import glob
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processed_dir = os.path.join(base_dir, "data", "processed")

json_files = glob.glob(os.path.join(processed_dir, "**", "*.json"), recursive=True)

docs = set()
for file_path in json_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data if isinstance(data, list) else data.get("chunks", [])
            for c in chunks:
                doc_id = c.get("document_id")
                jur = c.get("jurisdiction")
                domain = c.get("domain")
                if doc_id:
                    docs.add((doc_id, domain, jur))
    except Exception:
        pass

print(f"=== ALL {len(docs)} DOCUMENTS IN CORPUS ===")
for doc_id, domain, jur in sorted(docs):
    print(f"  - Document: {doc_id} | Domain: {domain} | Jurisdiction: {jur}")
