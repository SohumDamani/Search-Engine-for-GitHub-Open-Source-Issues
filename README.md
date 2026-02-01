# Search-Engine-for-GitHub-Open-Source-Issues
CS242 project – hybrid search engine (BM25 + BERT) over GitHub repos and issues.

## Status: Data Collection – Phase 1

Current components:

- **Docker dev environment**
- **Data collection module (`dataCollection/`)**
  - `github_client.py`
    - setups the github url and request format.
    - saves the token and ensures to take care of rate limit issue
  - `fetch_repos.py`
    - current;y hardcoded to search only topic = "python" --- update the topic for your usecase
    - Saves results as JSON Lines (`.jsonl`) in `data/rawData/repos_python.jsonl`
    - Prints a short summary of the top repositories

## How to run (current stage)

1. update your token in the .env file
2. Run

- docker compose build
- docker compose up -d
- docker exec -it cs242 bash
- cd /app
- python dataCollection/fetch_repos.py


# to check the raw data output
ls data/rawData
head -2 data/rawData/repos_python.jsonl
