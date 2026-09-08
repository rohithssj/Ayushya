import os
import sys
import argparse
import json

# Ensure project root is in sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.application.ingest_document_use_case import IngestDocumentUseCase

def main():
    parser = argparse.ArgumentParser(description="AYUSHYA RAG Ingestion Pipeline — Phase 1")
    parser.add_argument(
        "--doc-id", 
        type=str, 
        default="india_patents_act_1970",
        help="Document ID from resource_manifest.json to process (default: india_patents_act_1970)"
    )
    parser.add_argument("--start-page", type=int, default=None, help="Optional page override; otherwise detect the statutory body")
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Process all documents listed in resource_manifest.json"
    )

    args = parser.parse_args()

    use_case = IngestDocumentUseCase(base_dir=base_dir)

    if args.all:
        manifest_path = os.path.join(base_dir, "data", "metadata", "resource_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        print(f"Starting batch ingestion for all {len(manifest)} documents...")
        results = []
        for doc in manifest:
            doc_id = doc["document_id"]
            try:
                res = use_case.execute(document_id=doc_id, start_page=args.start_page)
                results.append(res)
                print(f"[OK] Processed {doc_id} -> {res['chunks_created']} chunks created.")
            except Exception as e:
                print(f"[FAIL] Failed to process {doc_id}: {e}")
        print(f"Batch ingestion complete. Processed {len(results)}/{len(manifest)} documents.")
    else:
        print(f"Processing single document: {args.doc_id} (Start page: {args.start_page or 'auto-detect'})...")
        res = use_case.execute(document_id=args.doc_id, start_page=args.start_page)
        
        print("\n==========================================")
        print("AYUSHYA RAG INGESTION PHASE 1 REPORT")
        print("==========================================")
        print(f"Document ID:        {res['document_id']}")
        print(f"Title:              {res['title']}")
        print(f"PDF Path:           {res['pdf_path']}")
        print(f"Total Pages:        {res['total_pages']}")
        print(f"Pages Processed:    {res['pages_processed']}")
        print(f"Chunks Created:     {res['chunks_created']}")
        print(f"Output Saved To:    {res['output_file']}")
        print("==========================================\n")

        print("--- EXAMPLE CHUNK 1 ---")
        print(json.dumps(res["example_chunks"][0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
