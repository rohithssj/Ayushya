import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.application.retrieve_chunks_use_case import RetrieveChunksUseCase
from src.features.rag.application.retrieve_embeddings_use_case import RetrieveEmbeddingsUseCase


QUESTIONS = [
    ("Patentability of a traditional herbal formulation", "India", "patents"),
    ("What inventions are not patentable under Indian law?", "India", "patents"),
    ("What biodiversity access and benefit-sharing obligations may apply?", "India", "biodiversity"),
    ("What does the TRIPS Agreement say about patents?", "International", "trips"),
    ("What are the requirements for an Ayurveda Aahara product?", "India", "ayurveda-aahar"),
]


def summarize(result):
    if not result:
        return "NO RESULT"
    top = result[0]
    page = top.get("page") or f"{top.get('page_start', '?')}-{top.get('page_end', '?')}"
    excerpt = " ".join(top["text"].split())[:180]
    score = top.get("similarity_score", top.get("relevance_score"))
    return f"{top['title']} | {top['section']} | pages {page} | score {score} | {excerpt}"


def main():
    lexical = RetrieveChunksUseCase(base_dir)
    semantic = RetrieveEmbeddingsUseCase(base_dir)
    for number, (question, jurisdiction, domain) in enumerate(QUESTIONS, 1):
        lexical_result = lexical.execute(question, 3, jurisdiction, domain)["results"]
        semantic_result = semantic.execute(question, 3, jurisdiction, domain)["results"]
        print(f"\n{number}. {question}")
        print(f"LEXICAL:  {summarize(lexical_result)}")
        print(f"SEMANTIC: {summarize(semantic_result)}")


if __name__ == "__main__":
    main()