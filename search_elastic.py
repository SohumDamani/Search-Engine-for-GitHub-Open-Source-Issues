import argparse
from elasticsearch import Elasticsearch

INDEX_NAME = "github_issues"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results")
    args = parser.parse_args()

    es = Elasticsearch("http://host.docker.internal:9200")

    body = {
        "size": args.top_k,
        "query": {
            "multi_match": {
                "query": args.query,
                "fields": ["title^2", "body"]
            }
        }
    }

    response = es.search(index=INDEX_NAME, body=body)

    print(f"\nTop {args.top_k} Elasticsearch results for query: {args.query}\n")

    for rank, hit in enumerate(response["hits"]["hits"], start=1):
        source = hit["_source"]
        snippet = source.get("body", "")[:300].replace("\n", " ")
        print(f"Rank: {rank}")
        print(f"Score: {hit['_score']:.4f}")
        print(f"Repo: {source.get('repo', '')}")
        print(f"Title: {source.get('title', '')}")
        print(f"URL: {source.get('issue_url', '')}")
        print(f"Snippet: {snippet}...")
        print("-" * 80)


if __name__ == "__main__":
    main()
