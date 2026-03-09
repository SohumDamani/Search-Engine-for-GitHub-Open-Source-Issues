import json
from pathlib import Path

INPUT_PATH = Path("data/processed/documents.jsonl")
OUTPUT_PATH = Path("data/processed/passages.jsonl")

def clean_text(text):
    if text is None:
        return ""
    return " ".join(str(text).split())

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with INPUT_PATH.open("r", encoding="utf-8") as fin, OUTPUT_PATH.open("w", encoding="utf-8") as fout:
        for line in fin:
            doc = json.loads(line)

            title = clean_text(doc.get("title", ""))
            body = clean_text(doc.get("body", ""))

            combined_text = f"{title} [SEP] {body}".strip()

            passage = {
                "passage_id": f"{doc['issue_id']}_0",
                "issue_id": doc["issue_id"],
                "repo": doc.get("repo", ""),
                "title": title,
                "passage_text": combined_text,
                "labels": doc.get("labels", []),
                "state": doc.get("state", ""),
                "issue_url": doc.get("issue_url", ""),
                "chunk_index": 0
            }

            fout.write(json.dumps(passage, ensure_ascii=False) + "\n")
            count += 1

    print(f"Created {count} passages")
    print(f"Saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
