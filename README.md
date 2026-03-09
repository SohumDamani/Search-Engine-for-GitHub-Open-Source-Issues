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

- Person Sohum – Issues
  - Scripts: `fetch_issues.py`, `merge_issues.py` 
  - The code has been tested sucessfully and the data is about 440Mb.
  - Look into the data and if required more add new topics
  - For Now I have taken 1246 repos and 50 recent issues from it. We can increase the issues size also so look into it.
  - Outputs:
    - Raw: `data/rawData/issues_*.jsonl`
    - Processed: `data/processed/all_issues.jsonl` (planned)

- Person Thrisha/Yashaswini – Preprocessing for IR
  - Scripts: `preprocess.py` (planned)
  - Outputs:
    - `data/processed/documents.jsonl` for BM25/BERT indexing

---

## Indexing (Part A2 – Information Retrieval)

After data collection, GitHub issues are indexed using Elasticsearch (Lucene-based) to enable fast, relevance-ranked full-text search using the BM25 ranking function.

Each GitHub issue is treated as a document and indexed with structured fields such as title, body text, repository name, labels, state, and timestamps.

---

### Indexing Pipeline Overview

Raw GitHub Issues (data/rawData/issues.jsonl)  
→ Preprocessing (document creation)  
→ Elasticsearch index creation  
→ Bulk indexing  
→ Searchable IR index

---
### How to Run Indexing (Docker)
1. Run the Docker Container
  docker run -it --name cs242-crawler   bash
 
2. Verify Elasticsearch is Running
  curl http://elasticsearch:9200
3. Run the Indexing Pipeline
  python indexing/preprocess.py
  python indexing/create_index.py
  python indexing/index_documents.py
4. Verify Indexing Output (Document Count)
  curl -s http://es-node:9200/github_issues/_count


### How to Run Indexing (Locally)


### Prerequisites

- Python 3.9+
- Elasticsearch 8.x or 9.x
- Elasticsearch running locally on http://localhost:9200

---

#### Step 1: Create and activate Python virtual environment

From the project root directory:

python -m venv .venv  
.venv\Scripts\Activate  
python -m pip install --upgrade pip  
pip install -r indexing/requirements.txt  

---

#### Step 2: Start Elasticsearch

Download and extract Elasticsearch (8.x or 9.x).

From the Elasticsearch directory (not the project directory), run:

.\bin\elasticsearch.bat -E xpack.security.enabled=false -E discovery.type=single-node  

Verify Elasticsearch is running:

curl http://localhost:9200  

---

#### Step 3: Preprocess GitHub issues

Convert raw GitHub issues into structured, IR-ready documents.

From the project root:

python indexing/preprocess.py  

Output generated:

data/processed/documents.jsonl  

Each line represents one GitHub issue with fields:
issue_id, repo, title, body, labels, state, created_at

---

#### Step 4: Create Elasticsearch index

Create the Elasticsearch index with appropriate mappings and analyzers:

python indexing/create_index.py  

This creates an index named:

github_issues  

---

#### Step 5: Bulk index documents

Index all preprocessed documents into Elasticsearch:

python indexing/index_documents.py  

Indexing completes in approximately 16 seconds on a local machine.

---

### Verifying Indexing Output

Check the number of indexed documents:

Invoke-RestMethod http://localhost:9200/github_issues/_count  

Result:

count: 45906  

---

Run a sample search query:

(Invoke-RestMethod "http://localhost:9200/github_issues/_search?q=bug&size=3").hits.hits._source |
Select-Object repo,title,issue_id  

Example output:

repo    title                                   issue_id  
        [Bug] name your bug                     924  
        [Bug] the title of bug report            60  
        [Bug]: New-WinUserLanguageList bug      1640  

---

### Indexing Output Summary

- Processed documents: data/processed/documents.jsonl  
- Elasticsearch index: github_issues  
- Total indexed documents: 45,906 GitHub issues  
- Search type: Full-text keyword search using BM25 ranking

---

# Part B – Dense Retrieval using BERT and Query Interface

In addition to the sparse BM25 index created using Elasticsearch in Part A, we implemented a dense retrieval pipeline using BERT embeddings and FAISS vector search. This allows semantic search where queries can retrieve relevant issues even if the exact keywords do not appear in the document.

Each GitHub issue document is converted into a passage and encoded into a dense vector embedding using a pretrained BERT model.

---

## Dense Indexing Pipeline Overview

Processed Documents (data/processed/documents.jsonl)  
→ Passage Generation  
→ BERT Embedding Creation  
→ FAISS Vector Index  
→ Semantic Search Retrieval

---

## Step 1: Generate Passages

GitHub issues are converted into passages suitable for BERT input.

Each passage is created by combining the issue title and issue body in the following format:

title [SEP] body

Run the script:

python bert_indexing/build_passages.py

Output generated:

data/processed/passages.jsonl

Each line in the file represents one passage extracted from a GitHub issue.

---

## Step 2: Generate BERT Embeddings

Each passage is converted into a dense embedding using the pretrained model:

sentence-transformers/all-MiniLM-L6-v2

Run:

python bert_indexing/embed_passages.py

Outputs generated:

data/faiss/passage_embeddings.npy  
data/faiss/passage_metadata.jsonl

Each passage is represented as a 384-dimensional embedding vector.

---

## Step 3: Build FAISS Vector Index

The embeddings are stored in a FAISS index for efficient nearest-neighbor similarity search.

Run:

python bert_indexing/build_faiss_index.py

Output generated:

data/faiss/github_issues.faiss

The FAISS index stores embeddings for all passages.

---

## Step 4: Run Dense Retrieval Search

Queries can now be searched using BERT embeddings and FAISS similarity search.

Run:

python bert_indexing/search_bert.py --query "login bug" --top_k 5

Process:

1. The query is converted into a BERT embedding  
2. FAISS finds the nearest passage embeddings  
3. The top-k results are returned

---

## Indexing Time Comparison

Two indexing methods were implemented in this project.

| Method | Representation | Indexing Time |
|------|------|------|
| Elasticsearch | Sparse BM25 index | ~23.28 seconds |
| BERT + FAISS | Dense vector index | ~1760.47 seconds |

Elasticsearch indexing is faster because it builds an inverted index, while BERT indexing requires generating embeddings using a neural model for every passage.

---

# Query Interface (B2)

A web interface was implemented using Flask to allow users to search using either Elasticsearch (BM25) or BERT (dense retrieval).

The interface allows the user to:

- Enter a search query
- Select the retrieval method
- Specify the number of results (Top-K)

---

## Running the Web Application

Start the search interface:

python app.py

Open a browser and go to:

http://localhost:5000

---

## Web Interface Features

The interface includes:

- Textbox for entering a search query
- Radio button to select the index:
  - Elasticsearch (BM25)
  - BERT (semantic search)
- Input field to select the number of results
- Ranked results displaying:
  - repository name
  - issue title
  - GitHub issue URL
  - snippet of issue text

---

## Example Query

Example query used during testing:

login bug

The system can return results using either:

- Elasticsearch keyword search (BM25 ranking)
- BERT semantic similarity search using FAISS

---

## Output Summary

- Dense embeddings generated for approximately **45,906 passages**
- FAISS vector index created
- Semantic search retrieval implemented
- Web interface supports both BM25 and BERT search
