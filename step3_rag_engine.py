"""
STEP 3 — RAG Query Engine
Loads FAISS index + intent classifier → answers HR questions.
"""

import os
import pickle
import json
import numpy as np
import faiss
from sklearn.preprocessing import normalize
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")


class HRPolicyRAG:

    def __init__(self):

        print("[RAG] Loading artifacts...")

        # FAISS index
        self.index = faiss.read_index(
            os.path.join(MODEL_DIR, "hr_faiss.index")
        )

        # Chunks
        with open(os.path.join(MODEL_DIR, "chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)

        # TF-IDF Vectorizer
        with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "rb") as f:
            self.rag_vec = pickle.load(f)

        # Intent classifier
        with open(os.path.join(MODEL_DIR, "intent_classifier.pkl"), "rb") as f:
            saved = pickle.load(f)

        self.clf = saved["classifier"]
        self.le = saved["label_encoder"]
        self.intent_vec = saved["vectorizer"]

        # Full JSON policies
        with open(os.path.join(DATA_DIR, "hr_policies.json"), encoding="utf-8") as f:
            docs = json.load(f)

        self.policy_map = {}
        self.holidays = []

        for d in docs:

            self.policy_map[d["title"]] = d.get("content", "")

            # Store holiday list separately
            if d.get("type") == "holiday_data":
                self.holidays = d.get("holidays", [])

        print(
            f"[RAG] Loaded {self.index.ntotal} vectors, "
            f"{len(self.chunks)} chunks, "
            f"{len(self.policy_map)} policies ✅"
        )

    # ---------------------------------------------------------
    # RETRIEVAL
    # ---------------------------------------------------------
    def retrieve(self, query, top_k=3):

        q_vec = normalize(
            self.rag_vec.transform([query]).toarray().astype(np.float32)
        )

        scores, ids = self.index.search(q_vec, k=len(self.chunks))

        query_lower = query.lower()

        boosted_results = []

        for score, idx in zip(scores[0], ids[0]):

            if idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]

            text = chunk["text"].lower()
            source = chunk["source"].lower()

            boost = 0

            # EXIT POLICY
            if "exit" in query_lower and "exit" in source:
                boost += 100

            # ASSET POLICY
            if "asset" in query_lower and "asset" in source:
                boost += 100

            # HOLIDAY POLICY
            if "holiday" in query_lower and "holiday" in source:
                boost += 120

            # LEAVE POLICY
            if "leave" in query_lower and "leave" in source:
                boost += 50

            # WORK FROM HOME
            if (
                "work from home" in query_lower
                or "wfh" in query_lower
            ) and "work from home" in source:
                boost += 100

            final_score = float(score) + boost

            boosted_results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "score": final_score
            })

        boosted_results = sorted(
            boosted_results,
            key=lambda x: x["score"],
            reverse=True
        )

        return boosted_results[:top_k]

    # ---------------------------------------------------------
    # INTENT
    # ---------------------------------------------------------
    def predict_intent(self, query):

        x = self.intent_vec.transform([query]).toarray()

        pred = self.le.inverse_transform(
            self.clf.predict(x)
        )[0]

        conf = float(self.clf.predict_proba(x).max())

        return pred, conf

    # ---------------------------------------------------------
    # HOLIDAY HELPERS
    # ---------------------------------------------------------
    def get_next_holiday(self):

        today = datetime.today().date()

        future_holidays = []

        for h in self.holidays:

            try:
                holiday_date = datetime.strptime(
                    h["date"],
                    "%Y-%m-%d"
                ).date()

                if holiday_date >= today:
                    future_holidays.append((holiday_date, h))

            except:
                continue

        if not future_holidays:
            return "No upcoming holidays found."

        future_holidays.sort(key=lambda x: x[0])

        next_holiday = future_holidays[0][1]

        return (
            f"Your next holiday is "
            f"{next_holiday['name']} on "
            f"{next_holiday['date']} "
            f"({next_holiday['day']})."
        )

    def get_month_holidays(self):

        today = datetime.today()

        month = today.month
        year = today.year

        result = []

        for h in self.holidays:

            try:
                holiday_date = datetime.strptime(
                    h["date"],
                    "%Y-%m-%d"
                )

                if (
                    holiday_date.month == month
                    and holiday_date.year == year
                ):
                    result.append(
                        f"{h['name']} - {h['date']}"
                    )

            except:
                continue

        if not result:
            return "No holidays this month."

        return "Holidays this month:\n\n" + "\n".join(result)

    def get_all_holidays(self):

        result = []

        for h in self.holidays:

            result.append(
                f"{h['name']} - {h['date']} ({h['day']})"
            )

        return "Holiday List:\n\n" + "\n".join(result)

    # ---------------------------------------------------------
    # ANSWER GENERATION
    # ---------------------------------------------------------
    def generate_answer(self, query, retrieved):

        query_lower = query.lower()

        # NEXT HOLIDAY
        if "next holiday" in query_lower:
            return self.get_next_holiday()

        # HOLIDAYS THIS MONTH
        if "holidays this month" in query_lower:
            return self.get_month_holidays()

        # HOLIDAY LIST
        if (
            "holiday list" in query_lower
            or "all holidays" in query_lower
        ):
            return self.get_all_holidays()

        # NORMAL RAG ANSWER
        if not retrieved:
            return (
                "I could not find relevant information "
                "in the HR policy documents."
            )

        top = retrieved[0]

        answer = (
            f"Based on the "
            f"**{top['source']}**:\n\n"
            f"{top['text']}"
        )

        extra = list({
            c["source"]
            for c in retrieved[1:]
            if c["source"] != top["source"]
        })

        if extra:
            answer += (
                f"\n\nAlso see: "
                f"{', '.join(extra)}"
            )

        return answer

    # ---------------------------------------------------------
    # MAIN ASK FUNCTION
    # ---------------------------------------------------------
    def ask(self, query, top_k=3):

        intent, confidence = self.predict_intent(query)

        retrieved = self.retrieve(query, top_k=top_k)

        answer = self.generate_answer(query, retrieved)

        return {
            "query": query,
            "intent": intent,
            "confidence": round(confidence, 4),
            "answer": answer,
            "sources": list({
                c["source"]
                for c in retrieved
            }),
            "top_chunks": retrieved
        }


# ---------------------------------------------------------
# TESTING
# ---------------------------------------------------------
if __name__ == "__main__":

    rag = HRPolicyRAG()

    queries = [
        "Exit policy",
        "Asset policy",
        "Holiday list",
        "When is my next holiday?",
        "How many leave days per year?",
        "Can employees work from home?"
    ]

    print("\n" + "=" * 60)
    print("HR POLICY ASSISTANT — RAG DEMO")
    print("=" * 60)

    for q in queries:

        r = rag.ask(q)

        print(f"\nQUESTION : {r['query']}")
        print(f"INTENT  : {r['intent']}")
        print(f"ANSWER  : {r['answer']}")
        print(f"SOURCES : {', '.join(r['sources'])}")

        print("-" * 60)

    print("\nSTEP 3 COMPLETE — RAG engine working!")
