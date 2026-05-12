"""
STEP 1 — RAG Pipeline (TF-IDF + FAISS)
Loads HR policy documents → chunks → TF-IDF embeddings → FAISS vector DB
"""

import json
import os
import pickle
import numpy as np
import faiss

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

MODEL_DIR = os.path.join(BASE_DIR, "models")

# ---------------------------------------------------------
# LOAD DOCUMENTS
# ---------------------------------------------------------

def load_documents():

    path = os.path.join(DATA_DIR, "hr_policies.json")

    with open(path, encoding="utf-8") as f:
        docs = json.load(f)

    print(f"[+] Loaded {len(docs)} HR policy documents")

    return docs

# ---------------------------------------------------------
# CHUNK DOCUMENTS
# ---------------------------------------------------------

def chunk_documents(docs, chunk_size=60, overlap=10):

    chunks = []

    for doc in docs:

        # CLEAN CONTENT
        content = str(doc.get("content", "")).strip()

        # SKIP EMPTY CONTENT
        if not content:
            continue

        # SOURCE NAME
        source_name = doc.get("title", "Unknown Policy")

        # SPLIT WORDS
        words = content.split()

        start = 0

        chunk_num = 0

        while start < len(words):

            end = min(start + chunk_size, len(words))

            chunk_text = " ".join(words[start:end])

            # STORE SEPARATE CHUNK
            chunks.append({

                "id": f"{doc['id']}_c{chunk_num}",

                "source": source_name,

                "text": chunk_text

            })

            chunk_num += 1

            # STOP IF END REACHED
            if end == len(words):
                break

            # OVERLAP LOGIC
            start += chunk_size - overlap

    print(f"[+] Created {len(chunks)} chunks")

    return chunks

# ---------------------------------------------------------
# EMBEDDINGS
# ---------------------------------------------------------

def embed_chunks(chunks):

    texts = [c["text"] for c in chunks]

    vectorizer = TfidfVectorizer(

        ngram_range=(1, 2),

        min_df=1,

        sublinear_tf=True

    )

    X = vectorizer.fit_transform(texts).toarray().astype(np.float32)

    X = normalize(X)

    print(f"[+] TF-IDF embedding shape: {X.shape}")

    return X, vectorizer

# ---------------------------------------------------------
# BUILD FAISS INDEX
# ---------------------------------------------------------

def build_faiss_index(embeddings):

    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)

    index.add(embeddings)

    print(
        f"[+] FAISS index built: "
        f"{index.ntotal} vectors (dim={dim})"
    )

    return index

# ---------------------------------------------------------
# SAVE ARTIFACTS
# ---------------------------------------------------------

def save_artifacts(index, chunks, vectorizer):

    os.makedirs(MODEL_DIR, exist_ok=True)

    # SAVE INDEX
    faiss.write_index(
        index,
        os.path.join(MODEL_DIR, "hr_faiss.index")
    )

    # SAVE CHUNKS
    with open(
        os.path.join(MODEL_DIR, "chunks.pkl"),
        "wb"
    ) as f:

        pickle.dump(chunks, f)

    # SAVE VECTORIZER
    with open(
        os.path.join(MODEL_DIR, "vectorizer.pkl"),
        "wb"
    ) as f:

        pickle.dump(vectorizer, f)

    print(f"[+] Saved artifacts → {MODEL_DIR}")

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)

    print(" STEP 1 — BUILDING RAG PIPELINE ")

    print("=" * 60 + "\n")

    # LOAD DOCS
    docs = load_documents()

    # CHUNKING
    chunks = chunk_documents(docs)

    # EMBEDDINGS
    embeddings, vec = embed_chunks(chunks)

    # FAISS
    index = build_faiss_index(embeddings)

    # SAVE
    save_artifacts(index, chunks, vec)

    # -----------------------------------------------------
    # SANITY CHECK
    # -----------------------------------------------------

    query = "How many leave days per year?"

    q_vec = normalize(
        vec.transform([query]).toarray().astype(np.float32)
    )

    scores, ids = index.search(q_vec, k=3)

    print("\n[Sanity Check] Top-3 Results:\n")

    for s, i in zip(scores[0], ids[0]):

        print(
            f"Score = {s:.4f}"
        )

        print(
            f"Source = {chunks[i]['source']}"
        )

        print(
            f"Chunk  = {chunks[i]['text'][:150]}..."
        )

        print("-" * 60)

    print("\n✅ STEP 1 COMPLETE — RAG index built successfully!")
