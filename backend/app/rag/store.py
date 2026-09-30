"""Almacén vectorial Chroma (T3.4).

- Colección `cvweb_public` con métrica coseno y persistencia en `CHROMA_PATH`.
- Guarda `embed_model` y `schema_version` en los metadatos de la colección y
  **rechaza** usarla con otra configuración (evita resultados basura).
- La API en producción lo abre en solo lectura; las escrituras las hace la
  ingesta offline (T3.5).
"""

from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.errors import NotFoundError

from app.rag.chunking import Chunk, embedding_text

COLLECTION_NAME = "cvweb_public"
SCHEMA_VERSION = "1"


class StoreConfigMismatch(RuntimeError):
    """El índice fue creado con otro modelo de embeddings o esquema."""


@dataclass(frozen=True)
class QueryHit:
    id: str
    text: str
    metadata: dict[str, Any]
    score: float


class ChromaStore:
    def __init__(
        self,
        path: Path | str,
        *,
        embed_model: str,
        read_only: bool = False,
        allow_mismatch: bool = False,
        collection_name: str = COLLECTION_NAME,
        schema_version: str = SCHEMA_VERSION,
    ) -> None:
        self._read_only = read_only
        self._allow_mismatch = allow_mismatch
        self._embed_model = embed_model
        self._schema_version = schema_version
        self._collection_name = collection_name
        self._path = Path(path)
        self._client = chromadb.PersistentClient(
            path=str(path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._open_or_create_collection()

    @property
    def read_only(self) -> bool:
        return self._read_only

    def _open_or_create_collection(self) -> Any:
        try:
            collection = self._client.get_collection(self._collection_name)
        except NotFoundError:
            return self._client.create_collection(
                name=self._collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "embed_model": self._embed_model,
                    "schema_version": self._schema_version,
                },
            )

        metadata = collection.metadata or {}
        stored_model = metadata.get("embed_model")
        stored_schema = metadata.get("schema_version")
        if self._allow_mismatch:
            return collection
        if stored_model != self._embed_model or stored_schema != self._schema_version:
            raise StoreConfigMismatch(
                "El índice se creó con "
                f"embed_model={stored_model!r} schema={stored_schema!r} y la configuración "
                f"actual es embed_model={self._embed_model!r} schema={self._schema_version!r}. "
                "Reindexa el vault (ver T3.5)."
            )
        return collection

    def count(self) -> int:
        return int(self._collection.count())

    def upsert(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        *,
        corpus_prefix: str = "",
    ) -> None:
        self._ensure_writable()
        if len(chunks) != len(embeddings):
            raise ValueError("chunks y embeddings deben tener la misma longitud")
        if not chunks:
            return
        self._collection.upsert(
            ids=[chunk.id for chunk in chunks],
            embeddings=embeddings,
            documents=[
                embedding_text(chunk, corpus_prefix=corpus_prefix) for chunk in chunks
            ],
            metadatas=[self._metadata(chunk) for chunk in chunks],
        )

    def delete_source(self, source_id: str) -> None:
        self._ensure_writable()
        self._collection.delete(where={"source_id": source_id})

    def reset(self) -> None:
        self._ensure_writable()
        self._client.delete_collection(self._collection_name)
        self._collection = self._open_or_create_collection()

    def start_replacement(self) -> "ChromaStore":
        """Crea una colección temporal para reconstruir el índice sin tocar la activa."""
        self._ensure_writable()
        name = f"{self._collection_name}__new"
        with suppress(NotFoundError):
            self._client.delete_collection(name)
        return ChromaStore(
            self._path,
            embed_model=self._embed_model,
            collection_name=name,
            schema_version=self._schema_version,
        )

    def commit_replacement(self, replacement: "ChromaStore") -> None:
        """Swap atómico: renombra la activa y promociona la temporal."""
        self._ensure_writable()
        backup = f"{self._collection_name}__old"
        with suppress(NotFoundError):
            self._client.delete_collection(backup)
        self._collection.modify(name=backup)
        replacement._collection.modify(name=self._collection_name)
        self._collection = replacement._collection
        with suppress(NotFoundError):
            self._client.delete_collection(backup)

    def query(self, embedding: list[float], *, top_k: int = 5) -> list[QueryHit]:
        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=max(1, top_k),
            include=["documents", "metadatas", "distances"],
        )
        ids = result["ids"][0]
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]
        hits: list[QueryHit] = []
        for index, chunk_id in enumerate(ids):
            hits.append(
                QueryHit(
                    id=str(chunk_id),
                    text=str(documents[index]),
                    metadata=dict(metadatas[index]),
                    score=1.0 - float(distances[index]),
                )
            )
        return hits

    def _metadata(self, chunk: Chunk) -> dict[str, Any]:
        return {
            "source_id": chunk.source_id,
            "title": chunk.title,
            "section": chunk.section,
            "tags": ",".join(chunk.tags),
            "lang": chunk.lang,
            "updated": chunk.updated or "",
            "context": chunk.context,
        }

    def _ensure_writable(self) -> None:
        if self._read_only:
            raise PermissionError("El almacén está abierto en solo lectura")
