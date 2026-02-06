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
    - Saves results as JSON Lines (`.jsonl`) in `data/rawData/repos_<topic>.jsonl`
    - Prints a short summary of the top repositories
  - `fetch_batch.py`
    - Has a list of topics to search for on github 
    - Has a limit of 100 repos for each topic.


## How to run (current stage)

1. update your token in the .env file
2. Update the topics to your choice different from the ones written and comment out the earlier ones
3. Collect atleast for 20 topics.

docker compose build
docker compose up -d
docker exec -it cs242 bash
cd /app
python dataCollection/fetch_batch.py


# to check the raw data output
ls data/rawData
head -2 data/rawData/repos_python.jsonl

## Data pipeline ownership (3-person team)

- Person Sohum – Repositories
  - Scripts: `fetch_repos.py`, `fetch_repos_batch.py`, `merge_repos.py`
  - Outputs:
    - Raw: `data/rawData/repos_*.jsonl`
    - Processed: `data/processed/all_repos.jsonl`

- Person Trisha/Yashaswani – Issues
  - Scripts: `fetch_issues.py`, `merge_issues.py` 
  - The code has been tested sucessfully and the data is about 440Mb.
  - Look into the data and if required more add new topics
  - For Now I have taken 1246 repos and 50 recent issues from it. We can increase the issues size also so look into it.
  - Outputs:
    - Raw: `data/rawData/issues_*.jsonl`
    - Processed: `data/processed/all_issues.jsonl` (planned)

- Person Trisha/Yashaswani – Preprocessing for IR
  - Scripts: `preprocess.py` (planned)
  - Outputs:
    - `data/processed/documents.jsonl` for BM25/BERT indexing