import json
import os

INPUT = "data/rawData/issues.jsonl"
OUTPUT = "data/processed/documents.jsonl"

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

def repo_from_url(url: str) -> str:
    parts = url.rstrip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return ""

count = 0
skipped_prs = 0

with open(INPUT, "r", encoding="utf-8") as fin, open(OUTPUT, "w", encoding="utf-8") as fout:
    for line in fin:
        issue = json.loads(line)

        if "pull_request" in issue:
            skipped_prs += 1
            continue

        doc = {
            "issue_id": issue.get("issue_number"),
            "title": issue.get("title") or "",
            "body": issue.get("body") or "",
            "labels": [l.get("name") for l in issue.get("labels", []) if isinstance(l, dict) and "name" in l],
            "state": issue.get("state") or "",
            "repo": repo_from_url(issue.get("repository_url", "")) if issue.get("repository_url") else "",
            "created_at": issue.get("created_at") or ""
        }

        fout.write(json.dumps(doc) + "\n")
        count += 1

print(f"Wrote {count} issue-documents to {OUTPUT}")
print(f"Skipped {skipped_prs} pull-request items")
