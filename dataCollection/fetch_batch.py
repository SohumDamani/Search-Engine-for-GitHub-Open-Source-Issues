from fetch_repos import search_repos_by_topic, save_repos_jsonl

TOPICS = [
    "python",  "rust","javascript","react","Azure","machine-learning", "data-science", "deep-learning", "nlp",
    "devops", "docker", "kubernetes","vector-database","local-llm","ai-agent", "real-time-speach-to-text"
]

def main():
    limit = 100  # per topic, first page only for now
    for topic in TOPICS:
        repos = search_repos_by_topic(topic, limit=limit)
        print(f"[{topic}] fetched {len(repos)} repos")
        save_repos_jsonl(topic, repos)

if __name__ == "__main__":
    main()
