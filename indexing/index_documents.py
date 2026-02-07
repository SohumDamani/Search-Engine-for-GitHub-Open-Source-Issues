import json
import time
from elasticsearch import Elasticsearch, helpers

INDEX_NAME = "github_issues"
DOC_FILE = "data/processed/documents.jsonl"

es = Elasticsearch("http://localhost:9200")

def generate_actions():
    with open(DOC_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": INDEX_NAME,
                "_source": doc
            }

start = time.time()
helpers.bulk(es, generate_actions())
end = time.time()

print(f"✅ Indexed documents in {end - start:.2f} seconds")
