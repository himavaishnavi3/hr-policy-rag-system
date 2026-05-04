"""
STEP 1 — RAG Pipeline (TF-IDF + FAISS)
Loads HR policy documents → chunks → TF-IDF embeddings → FAISS vector DB
"""

import json, os, pickle
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# Always resolve paths relative to THIS file's location
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
MODEL_DIR  = os.path.join(BASE_DIR, "models")

def load_documents():
    path = os.path.join(DATA_DIR, "hr_policies.json")
    with open(path) as f:
        docs = json.load(f)
    print(f"[+] Loaded {len(docs)} HR policy documents")
    return docs

def chunk_documents(docs, chunk_size=60, overlap=10):
    chunks = []
    for doc in docs:
        words = doc["content"].split()
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunks.append({
                "id":     f"{doc['id']}_c{len(chunks)}",
                "source": doc["title"],
                "text":   " ".join(words[start:end])
            })
            if end == len(words):
                break
            start += chunk_size - overlap
    print(f"[+] Created {len(chunks)} chunks")
    return chunks

def embed_chunks(chunks):
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    X = vectorizer.fit_transform(texts).toarray().astype(np.float32)
    X = normalize(X)
    print(f"[+] TF-IDF embedding shape: {X.shape}")
    return X, vectorizer

def build_faiss_index(embeddings):
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"[+] FAISS index built: {index.ntotal} vectors (dim={dim})")
    return index

def save_artifacts(index, chunks, vectorizer):
    os.makedirs(MODEL_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(MODEL_DIR, "hr_faiss.index"))
    with open(os.path.join(MODEL_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)
    with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"[+] Saved artifacts → {MODEL_DIR}")

if __name__ == "__main__":
    docs            = load_documents()
    chunks          = chunk_documents(docs)
    embeddings, vec = embed_chunks(chunks)
    index           = build_faiss_index(embeddings)
    save_artifacts(index, chunks, vec)

    # Sanity check
    query = "How many leave days per year?"
    q_vec = normalize(vec.transform([query]).toarray().astype(np.float32))
    scores, ids = index.search(q_vec, k=3)
    print("\n[Sanity Check] Top-3 for:", query)
    for s, i in zip(scores[0], ids[0]):
        print(f"  Score={s:.4f} | {chunks[i]['source']:30s} | {chunks[i]['text'][:80]}...")
    print("\n✅ STEP 1 COMPLETE — RAG index built!")
