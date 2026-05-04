"""
STEP 2 — Train Intent Classifier (TF-IDF + Logistic Regression)
Expanded dataset for better accuracy across 7 HR policy categories.
"""

import os, pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

TRAINING_DATA = [
    # Leave Policy
    ("How many leave days do I get per year?",                    "Leave Policy"),
    ("What is the annual leave entitlement?",                     "Leave Policy"),
    ("Can I carry forward unused leave?",                         "Leave Policy"),
    ("How do I apply for leave?",                                 "Leave Policy"),
    ("How many days advance notice for leave?",                   "Leave Policy"),
    ("What is the maximum carry-forward leave days?",             "Leave Policy"),
    ("How many annual paid leave days are allowed?",              "Leave Policy"),
    ("What is the leave policy for employees?",                   "Leave Policy"),
    ("Can unused annual leave be rolled over?",                   "Leave Policy"),
    ("How to request annual leave?",                              "Leave Policy"),
    ("How far in advance must I apply for time off?",             "Leave Policy"),
    ("What happens to unused leave at year end?",                 "Leave Policy"),
    ("Can I take more than 18 days leave?",                       "Leave Policy"),

    # Sick Leave Policy
    ("How many sick days am I entitled to?",                      "Sick Leave Policy"),
    ("Do I need a doctor certificate for sick leave?",            "Sick Leave Policy"),
    ("Can I carry forward sick leave?",                           "Sick Leave Policy"),
    ("What happens if sick leave exceeds 3 days?",                "Sick Leave Policy"),
    ("How many sick leave days per year?",                        "Sick Leave Policy"),
    ("Is medical certificate required for sick leave?",           "Sick Leave Policy"),
    ("How many consecutive sick days before needing a certificate?","Sick Leave Policy"),
    ("What is the sick leave policy?",                            "Sick Leave Policy"),
    ("Can I accumulate sick leave?",                              "Sick Leave Policy"),
    ("Does sick leave rollover to next year?",                    "Sick Leave Policy"),
    ("How many days sick leave without proof?",                   "Sick Leave Policy"),
    ("What documents are needed for extended sick leave?",        "Sick Leave Policy"),

    # Work From Home Policy
    ("Can I work from home?",                                     "Work From Home Policy"),
    ("How many WFH days are allowed per week?",                   "Work From Home Policy"),
    ("What are the core hours for WFH?",                          "Work From Home Policy"),
    ("Do I need manager approval to work from home?",             "Work From Home Policy"),
    ("How to request work from home?",                            "Work From Home Policy"),
    ("Is remote work allowed?",                                   "Work From Home Policy"),
    ("What is the WFH policy?",                                   "Work From Home Policy"),
    ("How many days can I work remotely?",                        "Work From Home Policy"),
    ("Can I work from home every day?",                           "Work From Home Policy"),
    ("What are core working hours when working remotely?",        "Work From Home Policy"),
    ("Do I need approval for remote work?",                       "Work From Home Policy"),
    ("How do I apply for work from home?",                        "Work From Home Policy"),

    # Travel Reimbursement Policy
    ("How do I claim travel reimbursement?",                      "Travel Reimbursement Policy"),
    ("What expenses are covered for business travel?",            "Travel Reimbursement Policy"),
    ("When should I submit travel claims?",                       "Travel Reimbursement Policy"),
    ("Are hotel costs reimbursed?",                               "Travel Reimbursement Policy"),
    ("What is the deadline for submitting travel claims?",        "Travel Reimbursement Policy"),
    ("Is airfare covered for business trips?",                    "Travel Reimbursement Policy"),
    ("What is the reimbursement policy for travel?",              "Travel Reimbursement Policy"),
    ("Can I claim meals during business travel?",                 "Travel Reimbursement Policy"),
    ("How many days to submit travel expense claims?",            "Travel Reimbursement Policy"),
    ("Are local transport costs covered during travel?",          "Travel Reimbursement Policy"),
    ("What receipts do I need for travel reimbursement?",         "Travel Reimbursement Policy"),
    ("Can I book business class for travel?",                     "Travel Reimbursement Policy"),

    # Employee Benefits
    ("What benefits do employees get?",                           "Employee Benefits"),
    ("Is health insurance provided?",                             "Employee Benefits"),
    ("What is the probation period for benefits?",                "Employee Benefits"),
    ("Is there a performance bonus?",                             "Employee Benefits"),
    ("Do employees get parental leave?",                          "Employee Benefits"),
    ("What is provident fund contribution?",                      "Employee Benefits"),
    ("What benefits are available after probation?",              "Employee Benefits"),
    ("Does the company offer health coverage?",                   "Employee Benefits"),
    ("When am I eligible for employee benefits?",                 "Employee Benefits"),
    ("Is there an annual bonus for employees?",                   "Employee Benefits"),
    ("What is the maternity leave policy?",                       "Employee Benefits"),
    ("Are there any retirement benefits?",                        "Employee Benefits"),

    # Working Hours Policy
    ("What are the office working hours?",                        "Working Hours Policy"),
    ("What time does work start and end?",                        "Working Hours Policy"),
    ("How many hours per week should I work?",                    "Working Hours Policy"),
    ("What happens if I am late frequently?",                     "Working Hours Policy"),
    ("What are the standard office timings?",                     "Working Hours Policy"),
    ("What are the official working hours?",                      "Working Hours Policy"),
    ("How many hours a week do I need to work?",                  "Working Hours Policy"),
    ("What time do I need to be at office?",                      "Working Hours Policy"),
    ("Are there penalties for coming late?",                      "Working Hours Policy"),
    ("What is the weekly work hour requirement?",                 "Working Hours Policy"),
    ("Does the company work on weekends?",                        "Working Hours Policy"),
    ("What is the shift timing?",                                 "Working Hours Policy"),

    # Code of Conduct
    ("What is the code of conduct?",                              "Code of Conduct"),
    ("What happens if someone harasses me?",                      "Code of Conduct"),
    ("What are the disciplinary rules?",                          "Code of Conduct"),
    ("Is there a confidentiality policy?",                        "Code of Conduct"),
    ("What behavior is not allowed at work?",                     "Code of Conduct"),
    ("What is the policy on workplace harassment?",               "Code of Conduct"),
    ("What are the consequences of misconduct?",                  "Code of Conduct"),
    ("Can I share company data externally?",                      "Code of Conduct"),
    ("What is considered unethical behavior at work?",            "Code of Conduct"),
    ("What action is taken against discrimination?",              "Code of Conduct"),
    ("What are employee obligations regarding confidentiality?",  "Code of Conduct"),
    ("What is the professional behavior policy?",                 "Code of Conduct"),
]

def build_dataset():
    questions = [q for q, _ in TRAINING_DATA]
    labels    = [l for _, l in TRAINING_DATA]
    print(f"[+] Dataset: {len(questions)} samples across {len(set(labels))} categories")
    for cat in sorted(set(labels)):
        print(f"    {cat:35s}: {labels.count(cat)} samples")
    return questions, labels

def train(questions, labels):
    le  = LabelEncoder()
    y   = le.fit_transform(labels)
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    X   = vec.fit_transform(questions).toarray()

    cv_scores = cross_val_score(
        LogisticRegression(max_iter=1000, C=5.0, random_state=42),
        X, y, cv=5, scoring="accuracy"
    )
    print(f"\n[+] 5-Fold CV Accuracy: {cv_scores.mean()*100:.1f}% ± {cv_scores.std()*100:.1f}%")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    clf = LogisticRegression(max_iter=1000, C=5.0, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)

    print(f"\n{'='*55}")
    print(f"  TRAINING COMPLETE  |  Hold-out Accuracy: {acc*100:.1f}%")
    print(f"{'='*55}")
    print(classification_report(y_test, y_pred,
                                 target_names=le.classes_, zero_division=0))

    # Final model on ALL data
    clf.fit(X, y)
    return clf, le, vec

def save_model(clf, le, vec):
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(os.path.join(MODEL_DIR, "intent_classifier.pkl"), "wb") as f:
        pickle.dump({"classifier": clf, "label_encoder": le, "vectorizer": vec}, f)
    print(f"[+] Saved intent classifier → {MODEL_DIR}")

if __name__ == "__main__":
    questions, labels = build_dataset()
    clf, le, vec      = train(questions, labels)
    save_model(clf, le, vec)

    test_cases = [
        "What benefits are available after probation?",
        "Can I work from home 3 days a week?",
        "How do I submit a travel expense?",
        "What are the office hours?",
        "How many sick days without a certificate?",
    ]
    print("\n[Inference Tests]")
    print("-" * 55)
    for q in test_cases:
        x    = vec.transform([q]).toarray()
        pred = le.inverse_transform(clf.predict(x))[0]
        conf = clf.predict_proba(x).max()
        print(f"  Q: {q[:45]:<45s}")
        print(f"     → {pred}  ({conf:.0%})")
    print("\n✅ STEP 2 COMPLETE — Model training done!")
