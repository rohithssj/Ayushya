import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.features.rag.application.retrieve_embeddings_use_case import RetrieveEmbeddingsUseCase


QUESTIONS = [
    ("Patentability of a traditional herbal formulation", "India", "patents"),
    ("What inventions are not patentable under Indian law?", "India", "patents"),
    ("What biodiversity access and benefit-sharing obligations may apply?", "India", "biodiversity"),
    ("What does the TRIPS Agreement say about patents?", "International", "trips"),
    ("What are the requirements for an Ayurveda Aahara product?", "India", "ayurveda-aahar"),
]


def main() -> None:
    use_case = RetrieveEmbeddingsUseCase(base_dir)
    print(f"Loaded {len(use_case.retriever.chunks)} embedded chunks")
    for number, (question, jurisdiction, domain) in enumerate(QUESTIONS, start=1):
        response = use_case.execute(
            query=question,
            top_k=3,
            jurisdiction=jurisdiction,
            domain=domain,
        )
        print(f"\n{number}. {question}")
        print(f"   Filters: jurisdiction={jurisdiction}, domain={domain}")
        for rank, result in enumerate(response["results"], start=1):
            page = result.get("page") or f"{result.get('page_start', '?')}-{result.get('page_end', '?')}"
            excerpt = " ".join(result["text"].split())[:500]
            print(
                f"   {rank}. {result['title']} | {result['section']} | "
                f"page(s) {page} | similarity={result['similarity_score']}"
            )
            print(f"      {excerpt}")
        if not response["results"]:
            raise AssertionError(f"No results for question: {question}")


if __name__ == "__main__":
    main()
