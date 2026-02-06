"""
Fetch issues for all repositories in data/processed/all_repos.jsonl
and save them into data/rawData/issues.jsonl (one issue per line).

Notes:
- Uses GitHub's /repos/{owner}/{repo}/issues endpoint.
- Fetches both open and closed issues (state=all).
- Paginates with per_page=100 until no more issues.
"""

import json
import requests
import argparse
from itertools import islice
from pathlib import Path
from typing import Dict, Any, List
from github_client import GitHubClient

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "rawData"
PROCESSED_DIR = RAW_DIR / "processed"

REPOS_PATH = PROCESSED_DIR / "all_repos.jsonl"
ISSUES_OUTPUT_PATH = RAW_DIR / "issues.jsonl"


def load_repos(path: Path) -> List[Dict[str, Any]]:
    repos: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            repos.append(json.loads(line))
    return repos


def fetch_issues_for_repo(client: GitHubClient, owner: str, repo: str, max_issues: int = 50) -> List[Dict[str, Any]]:
    all_issues: List[Dict[str, Any]] = []
    page = 1
    per_page = 50  # you can keep 50/page and just take the first page

    while True:
        params = {
            "state": "all",
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }
        endpoint = f"/repos/{owner}/{repo}/issues"
        try:
            items = client.get_json(endpoint, params=params)
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status == 422:
                print(f"Got 422 for {owner}/{repo} on page={page}, stopping pagination for this repo.")
                break
            raise

        if not items:
            break

        all_issues.extend(items)

        # Stop as soon as we have at least max_issues
        if len(all_issues) >= max_issues:
            break

        if len(items) < per_page:
            break

        page += 1

    return all_issues[:max_issues]



def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(
        description="Fetch GitHub issues for all repos in all_repos.jsonl."
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="0-based index of repo to start from (default: 0)",
    )
    args = parser.parse_args()
    start_index = args.start_index
    client = GitHubClient()

    repos = load_repos(REPOS_PATH)
    print(f"Loaded {len(repos)} repos from {REPOS_PATH}")

    written = 0
    mode = "a" if ISSUES_OUTPUT_PATH.exists() else "w"
    with ISSUES_OUTPUT_PATH.open(mode, encoding="utf-8") as out_f:
        for idx, repo in enumerate(repos):
            if idx < start_index:
                continue

            full_name = repo.get("full_name", "")
            if "/" not in full_name:
                continue
            owner, name = full_name.split("/", 1)
            print(f"[{idx}/{len(repos)}] Fetching issues for {full_name}...")

            issues = fetch_issues_for_repo(client, owner, name)

            for issue in issues:
                # Add a few explicit fields for convenience
                issue_record = {
                    "repo_full_name": full_name,
                    "issue_number": issue.get("number"),
                    "title": issue.get("title"),
                    "body": issue.get("body"),
                    "state": issue.get("state"),
                    "created_at": issue.get("created_at"),
                    "updated_at": issue.get("updated_at"),
                    "closed_at": issue.get("closed_at"),
                    "comments": issue.get("comments"),
                    "labels": [lbl.get("name") for lbl in issue.get("labels", [])],
                    # Keep the full raw issue as well if you want:
                    "raw": issue,
                }

                out_f.write(json.dumps(issue_record, ensure_ascii=False) + "\n")
                written += 1

    print(f"Wrote {written} issues to {ISSUES_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
