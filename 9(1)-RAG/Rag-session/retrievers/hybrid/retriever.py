"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support with rank_constant=60.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25(특이한 단어 잘 찾아냄) + kNN(paraphrasing으ㄹ 잘 찾아냄).

    Args:
        query: Search query string.
        top_k: Number of results to return.
        candidate_size: Number of kNN candidates before RRF fusion.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Hybrid (RRF)".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Use get_es_client() and es.search() with "retriever" parameter
        - RRF retriever combines "standard" (BM25 match) + "knn" retrievers
        - kNN field: "embedding", rank_constant: 60
        - num_candidates = candidate_size * 2
    """
    query_vector = embed_query(query)
    es_client = get_es_client()

    # 2. RRF 방식 -> retriever 파라미터를 활용해서 combining BM25 + kNN
    response = es_client.search(
        index=INDEX_NAME,
        retriever={
            "rrf": {
                "retrievers": [
                    {
                        "standard": { # (1) BM25 키워드 검색기
                            "query": {
                                "match": {
                                    "text": query
                                }
                            }
                        }
                    },
                    {
                        "knn": { # (2) kNN 벡터 검색기
                            "field": "embedding",
                            "query_vector": query_vector,
                            "k": candidate_size,
                            "num_candidates": candidate_size * 2
                        }
                    }
                ],
                "rank_constant": 60, # RRF 공식에 사용되는 상수
                "rank_window_size": candidate_size
            }
        },
        size=top_k
    )

    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id": hit["_id"],
            "text": hit["_source"]["text"],
            "score": hit["_score"], # RRF 계산 결과 점수
            "method": "Hybrid (RRF)"  
        })

    return results