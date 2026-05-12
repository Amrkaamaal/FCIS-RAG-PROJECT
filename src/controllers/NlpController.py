"""
samaXjana
NLP Controller
 → Embed the search query
 → Find top-K similar chunks
 →  Build the prompt from retrieved chunks
 → Call LLM API → Get answer
"""

import os
from controllers.indexer import run_pipeline
from stores.llm.LLMFactory import LLMFactory
from stores.llm.tempelate.template_parser import TemplateParser
from stores.vectordb.provider.qdrant_provider import QdrantProvider


class NlpController:

    def __init__(self):
        self.llm = LLMFactory.create()
        self.template_parser = TemplateParser(language="en")
        self.db = QdrantProvider(
            db_path=os.getenv("VECTOR_DB_PATH", "assets/db/qdrant_data"),
            collection_name=os.getenv("COLLECTION_NAME", "job_documents"),
            vector_size=int(os.getenv("EMBEDDING_DIMENSION", "768")),
        )

    def info(self) -> dict:
        return {
            "collection_name": os.getenv("COLLECTION_NAME", "job_documents"),
            "vector_size": int(os.getenv("EMBEDDING_DIMENSION", "768")),
            "points": self.db.count(),
            "llm_provider": os.getenv("LLM_PROVIDER", "openai"),
            "embedding_model": os.getenv("EMBEDDINGS_MODEL", "nomic-embed-text"),
            "generation_model": os.getenv("GENERATE_RESPONSE_MODEL", "qwen2.5:3b"),
        }

    def index_push(self, do_reset: bool = False) -> dict:
        run_pipeline(
            documents_dir=os.getenv("DOCUMENTS_DIR", "assets/documents/job_pdfs"),
            db_path=os.getenv("VECTOR_DB_PATH", "assets/db/qdrant_data"),
            collection_name=os.getenv("COLLECTION_NAME", "job_documents"),
            reset=do_reset,
        )

        return {
            "status": "ok",
            "reset": do_reset,
        }

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_vector = self.llm.embed_text(query)
        return self.db.search(query_vector=query_vector, top_k=top_k)

    def answer(self, query: str, top_k: int = 5, locale: str = "en") -> dict:
        query_vector = self.llm.embed_text(query)
        results = self.db.search(query_vector=query_vector, top_k=top_k, language_filter=locale)
        results = self._dedupe_results(results)

        if not results:
            return {
                "query": query,
                "answer": "No relevant documents found in the database.",
                "retrieved_chunks": [],
            }

        template_parser = TemplateParser(language=locale or "en")
        chunks_text = [r["text"] for r in results]
        prompt = template_parser.build_prompt(
            context_chunks=chunks_text,
            query=query,
        )

        answer = self.llm.generate_response(prompt)
        return {
            "query": query,
            "answer": answer,
            "retrieved_chunks": results,
        }

    def answer_query(self, query: str, top_k: int = 5) -> dict:
        return self.answer(query, top_k, "en")

    def _dedupe_results(self, results: list[dict]) -> list[dict]:
        # Remove duplicate chunks (same text from same file)
        seen = set()
        unique_results = []
        for result in results:
            text = result.get("text", "")
            if text in seen:
                continue
            seen.add(text)
            unique_results.append(result)
        return unique_results


if __name__ == "__main__":
    controller = NlpController()

    query = "What are the responsibilities of a sales manager?"
    print(f"Query: {query}\n")

    result = controller.answer_query(query, top_k=5)

    print(f"Answer:\n{result['answer']}\n")
    print(f"Retrieved {len(result['retrieved_chunks'])} chunks:")
    for i, chunk in enumerate(result['retrieved_chunks']):
        print(f"\n  Chunk {i+1} (score: {chunk['score']:.3f}) from {chunk['source_file']}")
        print(f"  {chunk['text'][:150]}...")