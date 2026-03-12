import glob
import hashlib
import os
import uuid

import yaml
from chatwilly_knowledge.core.model import embeddings_model
from chatwilly_knowledge.settings import knowledge_settings
from qdrant_client import QdrantClient
from qdrant_client.http import models

qdrant = QdrantClient(
    url=knowledge_settings.qdrant.url, api_key=knowledge_settings.qdrant.api_key
)


def init_collection():
    if not qdrant.collection_exists(knowledge_settings.qdrant.collection_name):
        qdrant.create_collection(
            collection_name=knowledge_settings.qdrant.collection_name,
            vectors_config=models.VectorParams(
                size=knowledge_settings.qdrant.vector_size,
                distance=models.Distance.COSINE,
            ),
        )
        print(
            f"📦 Collezione '{knowledge_settings.qdrant.collection_name}' creata (Dim: {knowledge_settings.qdrant.vector_size})."
        )

        qdrant.create_payload_index(
            collection_name=knowledge_settings.qdrant.collection_name,
            field_name="category",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        qdrant.create_payload_index(
            collection_name=knowledge_settings.qdrant.collection_name,
            field_name="source_filename",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        qdrant.create_payload_index(
            collection_name=knowledge_settings.qdrant.collection_name,
            field_name="keywords",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        print("⚡ Indici creati con successo.")


def get_all_stored_filenames():
    filenames = set()
    next_offset = None
    while True:
        records, next_offset = qdrant.scroll(
            collection_name=knowledge_settings.qdrant.collection_name,
            limit=100,
            offset=next_offset,
            with_payload=["source_filename"],
            with_vectors=False,
        )
        for record in records:
            if "source_filename" in record.payload:
                filenames.add(record.payload["source_filename"])
        if next_offset is None:
            break
    return filenames


def run_loader():
    init_collection()

    staging_files = glob.glob(os.path.join(knowledge_settings.staging_folder, "*.yaml"))
    staging_data = {}

    if not staging_files:
        print(f"❌ Nessun file trovato in {knowledge_settings.staging_folder}")
        return

    for filepath in staging_files:
        if "processing_errors" in filepath:
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and "source_filename" in data:
                staging_data[data["source_filename"]] = data

    # 2. DELETE ORPHANS
    stored_files = get_all_stored_filenames()
    staging_filenames = set(staging_data.keys())
    files_to_delete = stored_files - staging_filenames

    if files_to_delete:
        print(f"🧹 Rimuovo {len(files_to_delete)} file obsoleti dal DB...")
        for fname in files_to_delete:
            qdrant.delete(
                collection_name=knowledge_settings.qdrant.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="source_filename",
                                match=models.MatchValue(value=fname),
                            )
                        ]
                    )
                ),
            )

    # 3. UPSERT
    for source_filename, data in staging_data.items():
        file_hash = data.get("file_hash")
        summary = data.get("document_summary", "")
        chunks = data.get("content", [])

        if not chunks:
            continue

        qdrant.delete(
            collection_name=knowledge_settings.qdrant.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source_filename",
                            match=models.MatchValue(value=source_filename),
                        )
                    ]
                )
            ),
        )

        print(f"🚀 Embedding & Uploading {source_filename} ({len(chunks)} chunks)...")

        texts_to_embed = []
        payloads = []
        point_ids = []

        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get("text", "")
            embed_text = f"Document Context: {summary}\n\nChunk: {chunk_text}"

            texts_to_embed.append(embed_text)

            raw_hash = hashlib.md5(
                f"{source_filename}_{i}_{chunk_text}".encode()
            ).hexdigest()
            point_ids.append(str(uuid.UUID(raw_hash)))

            payloads.append(
                {
                    "text": chunk_text,
                    "document_summary": summary,
                    "category": chunk.get("category", "unknown"),
                    "keywords": chunk.get("keywords", []),
                    "source_filename": source_filename,
                    "file_hash": file_hash,
                }
            )

        try:
            embeddings_list = embeddings_model.embed_documents(texts_to_embed)

            points = []
            for j, vector in enumerate(embeddings_list):
                points.append(
                    models.PointStruct(
                        id=point_ids[j], vector=vector, payload=payloads[j]
                    )
                )

            if points:
                qdrant.upsert(
                    collection_name=knowledge_settings.qdrant.collection_name,
                    points=points,
                )
                print(f"   ✅ Caricati {len(points)} vettori.")

        except Exception as e:
            print(f"   ❌ Errore embedding per {source_filename}: {e}")

    print("\n🎉 DB Sincronizzato con successo.")


if __name__ == "__main__":
    run_loader()
