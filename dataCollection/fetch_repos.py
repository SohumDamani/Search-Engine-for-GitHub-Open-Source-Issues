"""
Fetch some repositories for a given GitHub topic and
save them into data/raw/repos_<topic>.jsonl.

Right now we:
- Call the search API once (first page only).
- Save each repo JSON as a separate line.
- Print a short summary to the console.
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from github_client import GitHubClient

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "rawData"

def search_repos_by_topic(topic: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Use GitHub's /search/repositories endpoint to find popular repos for a topic.
    """
    client = GitHubClient()

    params = {
        "q": f"topic:{topic}",
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }

    data = client.get_json("/search/repositories", params=params)
    items = data.get("items", [])
    return items


def save_repos_jsonl(topic: str, repos: List[Dict[str, Any]]) -> Path:
    """
    Save repositories to data/raw/repos_<topic>.jsonl.
    Each line is a JSON object for one repo.
    """
    output_path = RAW_DIR / f"repos_{topic}.jsonl"

    with output_path.open("w", encoding="utf-8") as f:
        for repo in repos:
            f.write(json.dumps(repo, ensure_ascii=False) + "\n")

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch GitHub repositories for a topic and save as JSONL."
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="python",
        help="GitHub topic to search for (default: python)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of repositories to fetch (max 100 per request, default: 20)",
    )
    args = parser.parse_args()

    topic = args.topic
    limit = args.limit

    repos = search_repos_by_topic(topic, limit=limit)
    print(f"Fetched {len(repos)} repos for topic '{topic}'.")

    output_path = save_repos_jsonl(topic, repos)
    print(f"Saved to {output_path}")

    for repo in repos[:5]:
        full_name = repo.get("full_name")
        stars = repo.get("stargazers_count")
        description = (repo.get("description") or "").replace("\n", " ")
        print(f"- {full_name} (★ {stars}) – {description[:80]}")



if __name__ == "__main__":
    main()
