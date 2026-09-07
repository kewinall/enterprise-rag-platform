from dataclasses import asdict
from functools import lru_cache

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.ingestion.chunking import Chunk


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection
        self.encoder = SentenceTransformer(settings.embedding_model)

    def ensure_collection(self) -> None:
        dimension = self.encoder.get_sentence_embedding_dimension()
        collections = {c.name for c in self.client.get_collections().collections}
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=dimension,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        self.ensure_collection()
        vectors = self.encoder.encode([c.text for c in chunks], normalize_embeddings=True)
        points = [
            models.PointStruct(
                id=chunk.chunk_id,
                vector=vector.tolist(),
                payload=asdict(chunk),
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query: str, limit: int) -> list[dict]:
        self.ensure_collection()
        vector = self.encoder.encode(query, normalize_embeddings=True).tolist()
        results = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            limit=limit,
        ).points
        return [
            {
                "chunk_id": str(item.id),
                "source": item.payload.get("source", "unknown"),
                "text": item.payload.get("text", ""),
                "score": float(item.score),
            }
            for item in results
        ]

    def list_documents(self, limit: int = 1000) -> list[dict]:
        self.ensure_collection()
        points, _ = self.client.scroll(
            collection_name=self.collection,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [
            {
                "chunk_id": str(item.id),
                "source": item.payload.get("source", "unknown"),
                "text": item.payload.get("text", ""),
                "score": 0.0,
            }
            for item in points
        ]


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()
