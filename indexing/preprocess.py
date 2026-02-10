import json
import os

INPUT = "data/rawData/issues.jsonl"
OUTPUT = "data/processed/documents.jsonl"

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

count = 0
skipped_prs = 0

with open(INPUT, "r", encoding="utf-8") as fin, open(OUTPUT, "w", encoding="utf-8") as fout:
    for line in fin:
        issue = json.loads(line)

        raw_obj = issue.get("raw", {})
        if isinstance(raw_obj, dict) and "pull_request" in raw_obj:
            skipped_prs += 1
            continue

        doc = {
    "issue_id": issue.get("issue_number"),
    "repo": issue.get("repo_full_name") or "",
    "title": issue.get("title") or "",
    "body": issue.get("body") or "",
    "state": issue.get("state") or "",
    "labels": issue.get("labels") or [],
    "created_at": issue.get("created_at") or "",
    "updated_at": issue.get("updated_at") or "",
    "issue_url": (raw_obj.get("html_url") if isinstance(raw_obj, dict) else "") or ""
}


        fout.write(json.dumps(doc, ensure_ascii=False) + "\n")
        count += 1

print(f"Wrote {count} issue-documents to {OUTPUT}")
print(f"Skipped {skipped_prs} pull-request items")
