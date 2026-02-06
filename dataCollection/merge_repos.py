import os
from pathlib import Path

RAW_DIR = Path("data") / "rawData"
PROCESSED_DIR = RAW_DIR / "processed"
OUTPUT_PATH = PROCESSED_DIR / "all_repos.jsonl"

def main():

    merge_repos = set()
    total_read = 0

    # Only merge repo files (avoid future issues_*.jsonl)
    for file in os.listdir(RAW_DIR):
        if not file.startswith("repos_") or not file.endswith(".jsonl"):
            continue

        file_path = RAW_DIR / file
        print(f"Reading {file_path}...")

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_read += 1
                merge_repos.add(line)

    print(f"Total lines read: {total_read}")
    print(f"Unique lines (repos) after removing duplicates: {len(merge_repos)}")

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for repo in merge_repos:
            f.write(repo + "\n")

    print(f"Wrote {len(merge_repos)} repos to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
