from elasticsearch import Elasticsearch

INDEX_NAME = "github_issues"

es = Elasticsearch("http://localhost:9200")

if es.indices.exists(index=INDEX_NAME):
    print(f"Index '{INDEX_NAME}' already exists. Deleting...")
    es.indices.delete(index=INDEX_NAME)

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
            "title": {
                "type": "text",
                "analyzer": "custom_english"
            },
            "body": {
                "type": "text",
                "analyzer": "custom_english"
            },
            "labels": {"type": "keyword"},
            "created_at": {"type": "date"}
        }
    }
}

es.indices.create(index=INDEX_NAME, body=mapping)
print(f"Index '{INDEX_NAME}' created successfully.")
