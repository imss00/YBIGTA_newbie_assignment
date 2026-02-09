"""Ingest corpus into Elasticsearch BM25 index (wiki-bm25).

Index mapping: text field only (no vectors).
Bulk chunk_size=500 (lightweight without vectors).
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

load_dotenv()

INDEX_NAME = "wiki-bm25"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

INDEX_MAPPINGS = {
    "properties": {
        "text": {"type": "text", "analyzer": "standard"},
    }
}


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=60,
    )


def _generate_actions(corpus_path: Path):
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": INDEX_NAME,
                "_id": doc["id"],
                "_source": {
                    "text": doc["text"],
                },
            }


def ingest(progress_callback=None):
    """Create BM25 index and bulk-ingest corpus into Elasticsearch.

    Args:
        progress_callback: Optional callback(count) called after completion.

    Returns:
        int: Number of documents indexed.

    Hints:
        - Use get_es_client() to get ES client
        - Delete existing index if it exists, then create with INDEX_MAPPINGS
        - Corpus is at RAW_DIR / "corpus.jsonl"
        - Use _generate_actions(corpus_path) for bulk data
        - Use elasticsearch.helpers.bulk() with chunk_size=500
        - Call es.indices.refresh() after bulk ingest
    """
    # 1. 클라이언트 연결
    es_client = get_es_client()
    corpus = RAW_DIR /  "corpus.jsonl"

    # 2. 기존 인덱스가 있으면 삭제하고 다시 생성
    # 삭제
    if es_client.indices.exists(index=INDEX_NAME):
        es_client.indices.delete(index=INDEX_NAME)

    # 생성
    es_client.indices.create(index=INDEX_NAME, mappings=INDEX_MAPPINGS)

    
    # 3.Bulk Ingest
    count, _ = bulk(
        es_client,
        _generate_actions(corpus),
        chunk_size=500, # 500개씩 대량 적재 -> 하나씩 저장하면 너무 느려서
        stats_only=True
        )
    
    # 4. 검색이 바로 되도록 새로 고침
    es_client.indices.refresh(index=INDEX_NAME)

    if progress_callback:
        progress_callback(count)

    return count


if __name__ == "__main__":
    ingest()
