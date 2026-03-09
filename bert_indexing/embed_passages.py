import json
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

INPUT_PATH = Path("data/processed/passages.jsonl")
EMBEDDINGS_PATH = Path("data/faiss/passage_embeddings.npy")
METADATA_PATH = Path("data/faiss/passage_metadata.jsonl")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32


def main():
    EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    passages = []
    metadata = []

    print(f"Reading passages from {INPUT_PATH}")
    with INPUT_PATH.open("r", encoding="utf-8") as fin:
        for line in fin:
            obj = json.loads(line)
            passages.append(obj["passage_text"])
            metadata.append(obj)

    print(f"Total passages: {len(passages)}")

    start_time = time.time()

    embeddings = model.encode(
        passages,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    end_time = time.time()

    np.save(EMBEDDINGS_PATH, embeddings)

    with METADATA_PATH.open("w", encoding="utf-8") as fout:
        for item in metadata:
            fout.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Saved embeddings to: {EMBEDDINGS_PATH}")
    print(f"Saved metadata to: {METADATA_PATH}")
    print(f"BERT indexing time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
