import json
import time
import os
from elasticsearch import Elasticsearch, helpers

INDEX_NAME = "github_issues"
DOC_FILE = "data/processed/documents.jsonl"
ES_HOST = os.getenv("ES_URL", "http://localhost:9200")

es = Elasticsearch(
    ES_HOST,
    verify_certs=False,
    headers={
        "Accept": "application/vnd.elasticsearch+json; compatible-with=7",
        "Content-Type": "application/vnd.elasticsearch+json; compatible-with=7"
    }
)

def generate_actions():
    with open(DOC_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": INDEX_NAME,
                "_id": doc.get("issue_id"),
                "_source": doc
            }

if __name__ == "__main__":
    start = time.time()
    success, _ = helpers.bulk(es, generate_actions())
    end = time.time()
    print(f"Indexed {success} documents in {end - start:.2f} seconds")