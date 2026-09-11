import json
import glob
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processed_dir = os.path.join(base_dir, "data", "processed")

json_files = glob.glob(os.path.join(processed_dir, "**", "*.json"), recursive=True)

print("=== TRIPS SPECIFIC SEARCH ===")
trips_matches = []
for file_path in json_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data if isinstance(data, list) else data.get("chunks", [])
            for chunk in chunks:
                text = str(chunk.get("text", "")).lower()
                doc_id = str(chunk.get("document_id", "")).lower()
                title = str(chunk.get("title", "")).lower()
                if "trips" in text or "trips" in doc_id or "trips" in title:
                    trips_matches.append(chunk)
    except Exception:
        pass

print(f"Total TRIPS chunks found: {len(trips_matches)}")
for c in trips_matches[:5]:
    print(f"Chunk ID: {c.get('chunk_id')} | Doc: {c.get('document_id')} | Domain: {c.get('domain')} | Jur: {c.get('jurisdiction')}")
    print(f"  Title: {c.get('title')}")
    print(f"  Section: {c.get('section')}")
    print(f"  Snippet: {c.get('text')[:200].replace('\n', ' ')}...")

print("\n=== TRADEMARK REGISTRATION SPECIFIC SEARCH ===")
tm_matches = []
for file_path in json_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data if isinstance(data, list) else data.get("chunks", [])
            for chunk in chunks:
                text = str(chunk.get("text", "")).lower()
                doc_id = str(chunk.get("document_id", "")).lower()
                if "trademark" in doc_id or "trade_marks" in doc_id:
                    if any(w in text for w in ["registration", "register", "eligibility", "distinctive", "prohibited", "application"]):
                        tm_matches.append(chunk)
    except Exception:
        pass

print(f"Total Trademark Registration chunks found: {len(tm_matches)}")
for c in tm_matches[:5]:
    print(f"Chunk ID: {c.get('chunk_id')} | Doc: {c.get('document_id')} | Sec: {c.get('section')}")
    print(f"  Title: {c.get('title')}")
    print(f"  Snippet: {c.get('text')[:200].replace('\n', ' ')}...")
