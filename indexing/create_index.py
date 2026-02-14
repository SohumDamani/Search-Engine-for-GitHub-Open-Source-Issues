import os
from elasticsearch import Elasticsearch

INDEX_NAME = "github_issues"
ES_HOST = os.getenv("ES_URL", "http://localhost:9200")

es = Elasticsearch(
    ES_HOST,
    verify_certs=False,
    headers={
        "Accept": "application/vnd.elasticsearch+json; compatible-with=7",
        "Content-Type": "application/vnd.elasticsearch+json; compatible-with=7"
    }
)

mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "custom_english": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "issue_id": {"type": "keyword"},
            "repo": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "custom_english"},
            "body": {"type": "text", "analyzer": "custom_english"},
            "labels": {"type": "keyword"},
            "created_at": {"type": "date"}
        }
    }
}

try:
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)

    es.indices.create(
        index=INDEX_NAME,
        settings=mapping["settings"],
        mappings=mapping["mappings"]
    )
    print(f"Index '{INDEX_NAME}' created successfully at {ES_HOST}.")
except Exception as e:
    print(f"Error: {e}")