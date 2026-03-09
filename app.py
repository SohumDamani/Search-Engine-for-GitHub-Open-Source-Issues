import json
from pathlib import Path

import faiss
from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

app = Flask(__name__)

FAISS_INDEX_PATH = Path("data/faiss/github_issues.faiss")
METADATA_PATH = Path("data/faiss/passage_metadata.jsonl")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
ELASTIC_INDEX_NAME = "github_issues"

print("Loading BERT model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")
faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))

print("Loading passage metadata...")
passage_metadata = []
with METADATA_PATH.open("r", encoding="utf-8") as fin:
    for line in fin:
        passage_metadata.append(json.loads(line))

print("Connecting to Elasticsearch...")
es = Elasticsearch("http://host.docker.internal:9200")


def search_bert(query, top_k):
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = faiss_index.search(query_embedding, top_k)

    results = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        item = passage_metadata[idx]
        results.append({
            "rank": rank,
            "score": round(float(score), 4),
            "repo": item.get("repo", ""),
            "title": item.get("title", ""),
            "url": item.get("issue_url", ""),
            "snippet": item.get("passage_text", "")[:300] + "..."
        })
    return results


def search_elastic(query, top_k):
    body = {
        "size": top_k,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "body"]
            }
        }
    }

    response = es.search(index=ELASTIC_INDEX_NAME, body=body)

    results = []
    for rank, hit in enumerate(response["hits"]["hits"], start=1):
        source = hit["_source"]
        results.append({
            "rank": rank,
            "score": round(float(hit["_score"]), 4),
            "repo": source.get("repo", ""),
            "title": source.get("title", ""),
            "url": source.get("issue_url", ""),
            "snippet": source.get("body", "")[:300] + "..."
        })
    return results


@app.route("/", methods=["GET", "POST"])
def home():
    results = None
    query = ""
    index_choice = "elastic"
    top_k = 5

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        index_choice = request.form.get("index_choice", "elastic")
        top_k = int(request.form.get("top_k", 5))

        if query:
            if index_choice == "bert":
                results = search_bert(query, top_k)
            else:
                results = search_elastic(query, top_k)

    return render_template(
        "index.html",
        results=results,
        query=query,
        index_choice=index_choice,
        top_k=top_k
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
