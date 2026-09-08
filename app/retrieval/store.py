from dataclasses import asdict
from functools import lru_cache

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.ingestion.chunking import Chunk

PayloadFilter = dict[str, str | int]


def build_qdrant_filter(filters: PayloadFilter | None) -> models.Filter | None:
    if not filters:
        return None
    conditions = [
        models.FieldCondition(key=key, match=models.MatchValue(value=value))
        for key, value in filters.items()
    ]
    return models.Filter(must=conditions)


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

    @staticmethod
    def _payload_to_dict(payload: dict, chunk_id: str, score: float) -> dict:
        return {
            "chunk_id": chunk_id,
            "document_id": payload.get("document_id", "unknown"),
            "source": payload.get("source", "unknown"),
            "text": payload.get("text", ""),
            "ordinal": payload.get("ordinal"),
            "page": payload.get("page"),
            "section": payload.get("section"),
            "content_type": payload.get("content_type", "text/plain"),
            "score": score,
        }

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
        self.client.upsert(collection_name=self.collection, points=points, wait=True)

    def search(
        self,
        query: str,
        limit: int,
        filters: PayloadFilter | None = None,
    ) -> list[dict]:
        self.ensure_collection()
        vector = self.encoder.encode(query, normalize_embeddings=True).tolist()
        results = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            query_filter=build_qdrant_filter(filters),
            with_payload=True,
            limit=limit,
        ).points
        return [
            self._payload_to_dict(item.payload or {}, str(item.id), float(item.score))
            for item in results
        ]

    def list_chunks(
        self,
        limit: int = 10_000,
        filters: PayloadFilter | None = None,
    ) -> list[dict]:
        self.ensure_collection()
        result: list[dict] = []
        offset = None

        while len(result) < limit:
            batch_limit = min(256, limit - len(result))
            points, offset = self.client.scroll(
                collection_name=self.collection,
                scroll_filter=build_qdrant_filter(filters),
                limit=batch_limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            result.extend(
                self._payload_to_dict(item.payload or {}, str(item.id), 0.0)
                for item in points
            )
            if offset is None or not points:
                break

        return result

    def count_document(self, document_id: str) -> int:
        self.ensure_collection()
        query_filter = build_qdrant_filter({"document_id": document_id})
        result = self.client.count(
            collection_name=self.collection,
            count_filter=query_filter,
            exact=True,
        )
        return int(result.count)

    def delete_document(self, document_id: str) -> int:
        count = self.count_document(document_id)
        if count == 0:
            return 0
        query_filter = build_qdrant_filter({"document_id": document_id})
        if query_filter is None:
            return 0
        self.client.delete(
            collection_name=self.collection,
            points_selector=models.FilterSelector(filter=query_filter),
            wait=True,
        )
        return count

    def list_document_summaries(self) -> list[dict]:
        summaries: dict[str, dict] = {}
        for item in self.list_chunks():
            document_id = item["document_id"]
            summary = summaries.setdefault(
                document_id,
                {
                    "document_id": document_id,
                    "source": item["source"],
                    "content_type": item["content_type"],
                    "chunks": 0,
                    "pages": set(),
                    "sections": set(),
                },
            )
            summary["chunks"] += 1
            if item["page"] is not None:
                summary["pages"].add(item["page"])
            if item["section"]:
                summary["sections"].add(item["section"])

        return [
            {
                **summary,
                "pages": sorted(summary["pages"]),
                "sections": sorted(summary["sections"]),
            }
            for summary in sorted(summaries.values(), key=lambda value: value["source"])
        ]


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()
