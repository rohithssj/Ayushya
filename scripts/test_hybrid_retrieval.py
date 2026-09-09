import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.application.retrieve_chunks_use_case import RetrieveChunksUseCase
from src.features.rag.application.retrieve_embeddings_use_case import RetrieveEmbeddingsUseCase
from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase

QUESTIONS = [
    ("Patentability of a traditional herbal formulation", "India", "patents"),
    ("What inventions are not patentable under Indian law?", "India", "patents"),
    ("What biodiversity access and benefit-sharing obligations may apply?", "India", "biodiversity"),
    ("What does the TRIPS Agreement say about patents?", "International", "trips"),
    ("What are the requirements for an Ayurveda Aahara product?", "India", "ayurveda-aahar"),
]

def print_results(method_name: str, results: list):
    print(f"\n--- {method_name.upper()} RESULTS ---")
    for rank, result in enumerate(results, start=1):
        page = result.get("page") or f"{result.get('page_start', '?')}-{result.get('page_end', '?')}"
        excerpt = " ".join(result["text"].split())[:500]
        excerpt = excerpt.encode("ascii", "replace").decode("ascii")
        
        score_str = f"score={result.get('relevance_score', '?')}"
        if 'lexical_rank' in result:
            score_str += f" | lex_rank={result.get('lexical_rank')} | sem_rank={result.get('semantic_rank')}"
        elif 'similarity_score' in result:
            score_str += f" | similarity={result.get('similarity_score')}"
            
        print(
            f"   {rank}. {result['title']} | {result['section']} | "
            f"page(s) {page} | {score_str}"
        )
        print(f"      {excerpt}")
    if not results:
        print("   (No results found)")

def main() -> None:
    print("Loading retrievers...")
    lexical_uc = RetrieveChunksUseCase(base_dir)
    embedding_uc = RetrieveEmbeddingsUseCase(base_dir)
    hybrid_uc = HybridRetrievalUseCase(base_dir)
    
    print("Evaluating 5 standard questions...")
    for number, (question, jurisdiction, domain) in enumerate(QUESTIONS, start=1):
        print(f"\n=======================================================")
        print(f"Q{number}: {question}")
        print(f"Filters: jurisdiction={jurisdiction}, domain={domain}")
        print(f"=======================================================")
        
        lex_resp = lexical_uc.execute(query=question, top_k=3, jurisdiction=jurisdiction, domain=domain)
        print_results("Lexical", lex_resp["results"])
        
        emb_resp = embedding_uc.execute(query=question, top_k=3, jurisdiction=jurisdiction, domain=domain)
        print_results("Embedding", emb_resp["results"])
        
        hyb_resp = hybrid_uc.execute(query=question, top_k=3, jurisdiction=jurisdiction, domain=domain)
        print_results("Hybrid", hyb_resp["results"])

if __name__ == "__main__":
    main()
