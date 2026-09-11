import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.infrastructure.lexical_retriever import LexicalRetriever
from src.features.rag.infrastructure.embedding_retriever import EmbeddingRetriever

query = "Can I register a trademark for the brand name of my Ayurvedic medicine?"

print("=== 1. LEXICAL RETRIEVAL TOP 10 ===")
lex = LexicalRetriever(os.path.join(base_dir, "data", "processed"))
lex_res = lex.search(query=query, top_k=10, jurisdiction="India")
for i, r in enumerate(lex_res, 1):
    c = r.chunk
    print(f"  {i}. [{c.get('chunk_id')}] doc={c.get('document_id')} sec={c.get('section')} score={r.score:.4f}")
    print(f"     Title: {c.get('title')}")

print("\n=== 2. EMBEDDING RETRIEVAL TOP 10 ===")
emb = EmbeddingRetriever(os.path.join(base_dir, "data", "embeddings", "legal_chunks"))
emb_res = emb.search(query=query, top_k=10, jurisdiction="India")
for i, r in enumerate(emb_res, 1):
    c = r.chunk
    print(f"  {i}. [{c.get('chunk_id')}] doc={c.get('document_id')} sec={c.get('section')} sim={r.similarity_score:.4f}")
    print(f"     Title: {c.get('title')}")
