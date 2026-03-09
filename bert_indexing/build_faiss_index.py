import faiss
import numpy as np
from pathlib import Path

EMBEDDINGS_PATH = Path("data/faiss/passage_embeddings.npy")
FAISS_INDEX_PATH = Path("data/faiss/github_issues.faiss")


def main():
    print(f"Loading embeddings from: {EMBEDDINGS_PATH}")
    embeddings = np.load(EMBEDDINGS_PATH).astype("float32")

    print(f"Embeddings shape: {embeddings.shape}")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    faiss.write_index(index, str(FAISS_INDEX_PATH))

    print(f"FAISS index built with {index.ntotal} vectors")
    print(f"Saved index to: {FAISS_INDEX_PATH}")


if __name__ == "__main__":
    main()
