"""Ingest embeddings into Pinecone vector index.

pinecone -> id / values / metadata 의 양식을 요구
id = 책의 이름(번호)
values = 책의 내용(을 숫자로 바꾼 벡터) = 임베딩 값
metadata = 요약테스트 = 나중에 책을 찾았을 때 바로 읽어볼 수 있게 붙여둔 index

Batch upsert: 100 vectors per call.
Metadata: text truncated to 1000 chars (40KB limit).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm import tqdm

load_dotenv()

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

BATCH_SIZE = 100
TEXT_LIMIT = 1000  # metadata text truncation


def ingest(progress_callback=None):
    """Batch upsert embeddings into Pinecone vector index.

    Args:
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        int: Number of vectors upserted.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Load texts from RAW_DIR / "corpus.jsonl" for metadata
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Upsert format: {"id": ..., "values": [...], "metadata": {"text": ...}}
        - Batch size: BATCH_SIZE (100), truncate text to TEXT_LIMIT (1000) chars
    """
    embeddings_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
    texts_path = RAW_DIR / "corpus.jsonl"

    #임베딩 / id 로딩
    embedding = np.load(embeddings_path)
    with open(ids_path, "r", encoding="utf-8") as f:
        ids = json.load(f)
    

    # text 로딩
    text_dict = {}
    with open(texts_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            text_dict[doc["id"]] = doc["text"][:TEXT_LIMIT]


    # pinecone 연결; Connect: Pinecone(api_key=...) → pc.Index(index_name)
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index_name = "ragsession"
    index = pc.Index(index_name)

    # 100개씩 묶어서 Upsert(= 규칙대로 업로드)
    total = len(ids)
    for i in range(0, total, BATCH_SIZE):
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_vectors = embedding[i : i + BATCH_SIZE]

        vectors_to_upsert = []
        for j, doc_id in enumerate(batch_ids):
            vectors_to_upsert.append({
                "id": doc_id,
                "values": batch_vectors[j].tolist(),
                "metadata": {"text": text_dict[doc_id]} # 검색 시 바로 보여줄 텍스트
            })
        
        index.upsert(vectors=vectors_to_upsert)

        if progress_callback:
            progress_callback(min(i + BATCH_SIZE, total), total)

    return total


if __name__ == "__main__":
    ingest()
