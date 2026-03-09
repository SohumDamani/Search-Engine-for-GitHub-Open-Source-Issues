import argparse
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

FAISS_INDEX_PATH = Path("data/faiss/github_issues.faiss")
METADATA_PATH = Path("data/faiss/passage_metadata.jsonl")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_metadata():
    metadata = []
    with METADATA_PATH.open("r", encoding="utf-8") as fin:
        for line in fin:
            metadata.append(json.loads(line))
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results")
    args = parser.parse_args()

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Loading FAISS index from: {FAISS_INDEX_PATH}")
    index = faiss.read_index(str(FAISS_INDEX_PATH))

    print(f"Loading metadata from: {METADATA_PATH}")
    metadata = load_metadata()

    query_embedding = model.encode(
        [args.query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_embedding, args.top_k)

    print(f"\nTop {args.top_k} BERT results for query: {args.query}\n")

    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        item = metadata[idx]
        snippet = item["passage_text"][:300].replace("\n", " ")
        print(f"Rank: {rank}")
        print(f"Score: {score:.4f}")
        print(f"Repo: {item.get('repo', '')}")
        print(f"Title: {item.get('title', '')}")
        print(f"URL: {item.get('issue_url', '')}")
        print(f"Snippet: {snippet}...")
        print("-" * 80)


if __name__ == "__main__":
    main()
