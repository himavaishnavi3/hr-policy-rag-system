"""
STEP 3 — RAG Query Engine
Loads FAISS index + intent classifier → answers HR questions.
"""

import os, pickle, json
import numpy as np
import faiss
from sklearn.preprocessing import normalize

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR  = os.path.join(BASE_DIR, "data")

class HRPolicyRAG:
    def __init__(self):
        print("[RAG] Loading artifacts...")

        # FAISS index
        self.index = faiss.read_index(os.path.join(MODEL_DIR, "hr_faiss.index"))

        # Chunks
        with open(os.path.join(MODEL_DIR, "chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)

        # RAG TF-IDF vectorizer
        with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "rb") as f:
            self.rag_vec = pickle.load(f)

        # Intent classifier
        with open(os.path.join(MODEL_DIR, "intent_classifier.pkl"), "rb") as f:
            saved = pickle.load(f)
        self.clf        = saved["classifier"]
        self.le         = saved["label_encoder"]
        self.intent_vec = saved["vectorizer"]

        # Full policy content
        with open(os.path.join(DATA_DIR, "hr_policies.json")) as f:
            docs = json.load(f)
        self.policy_map = {d["title"]: d["content"] for d in docs}

        print(f"[RAG] Loaded {self.index.ntotal} vectors, "
              f"{len(self.chunks)} chunks, {len(self.policy_map)} policies ✅")

    def retrieve(self, query, top_k=3):
        q_vec = normalize(
            self.rag_vec.transform([query]).toarray().astype(np.float32)
        )
        scores, ids = self.index.search(q_vec, k=top_k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < len(self.chunks):
                results.append({
                    "text":   self.chunks[idx]["text"],
                    "source": self.chunks[idx]["source"],
                    "score":  float(score)
                })
        return results

    def predict_intent(self, query):
        x    = self.intent_vec.transform([query]).toarray()
        pred = self.le.inverse_transform(self.clf.predict(x))[0]
        conf = float(self.clf.predict_proba(x).max())
        return pred, conf

    def generate_answer(self, retrieved):
        if not retrieved:
            return "I could not find relevant information in the HR policy documents."
        top = retrieved[0]
        ans = f"Based on the **{top['source']}**:\n\n{top['text']}"
        extra = list({c["source"] for c in retrieved[1:] if c["source"] != top["source"]})
        if extra:
            ans += f"\n\n*Also see: {', '.join(extra)}*"
        return ans

    def ask(self, query, top_k=3):
        intent, confidence = self.predict_intent(query)
        retrieved          = self.retrieve(query, top_k=top_k)
        answer             = self.generate_answer(retrieved)
        return {
            "query":      query,
            "intent":     intent,
            "confidence": round(confidence, 4),
            "answer":     answer,
            "sources":    list({c["source"] for c in retrieved}),
            "top_chunks": retrieved
        }


if __name__ == "__main__":
    rag = HRPolicyRAG()
    queries = [
        "How many leave days do employees get per year?",
        "Can employees work from home?",
        "What are the working hours?",
        "What benefits do employees receive?",
        "How long can sick leave be taken without a medical certificate?",
        "When should travel reimbursements be submitted?",
    ]
    print("\n" + "=" * 60)
    print("  HR POLICY ASSISTANT — RAG DEMO")
    print("=" * 60)
    for q in queries:
        r = rag.ask(q)
        print(f"\n❓ {r['query']}")
        print(f"🎯 Intent : {r['intent']} ({r['confidence']:.0%})")
        print(f"💬 Answer : {r['answer'][:200]}")
        print(f"📄 Sources: {', '.join(r['sources'])}")
        print("-" * 60)
    print("\n✅ STEP 3 COMPLETE — RAG engine working!")
