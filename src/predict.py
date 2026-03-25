"""
predict.py — LinkedIn SpamGuard AI
Runs the end-to-end ML prediction pipeline (Feature Extraction + ML Model).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import joblib
import pandas as pd
from typing import Dict, Any

from src.feature_extractor import extract_features, FEATURE_NAMES

MODEL_PATH = "models/spam_classifier.pkl"
LABELS = {0: "FAKE", 1: "SUSPICIOUS", 2: "LEGIT"}

# Global cache for the loaded model
_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_spam(text: str) -> Dict[str, Any]:
    """
    Run the ML prediction pipeline on raw text.
    Returns features, prediction class, and confidence scores.
    """
    model = load_model()
    
    # 1. Feature Extraction
    features = extract_features(text)
    
    # 2. Prepare for model
    # Convert dict to DataFrame using the expected feature order
    feature_df = pd.DataFrame([features], columns=FEATURE_NAMES)
    
    # 3. Model Inference
    # predict_proba returns array of probabilities for [0(FAKE), 1(SUS), 2(LEGIT)]
    probs = model.predict_proba(feature_df)[0]
    pred_idx = model.predict(feature_df)[0]
    
    verdict = LABELS[pred_idx]
    confidence = float(probs[pred_idx]) * 100
    
    return {
        "text": text,
        "features": features,
        "ml_result": {
            "verdict": verdict,
            "confidence": round(confidence, 1),
            "probabilities": {
                "FAKE": round(probs[0] * 100, 1),
                "SUSPICIOUS": round(probs[1] * 100, 1),
                "LEGIT": round(probs[2] * 100, 1)
            }
        }
    }

if __name__ == "__main__":
    # Test cases
    test_texts = [
        "URGENT HIRING!! Earn $5000/week working from home. No experience needed. Apply NOW on WhatsApp: +919876543210. Limited slots!",
        "Google is hiring a Senior Software Engineer in Bangalore. 5+ years experience required with strong Python and ML skills. Apply at google.com/careers.",
        "We are hiring Data Analysts urgently. Our client is a leading firm. Salary up to $50k. Mail: hr123@gmail.com"
    ]
    
    for t in test_texts:
        print("\n" + "-"*50)
        print(f"TEXT: {t[:60]}...")
        res = predict_spam(t)
        print(f"VERDICT: {res['ml_result']['verdict']} ({res['ml_result']['confidence']}%)")
        print(f"PROBS: {res['ml_result']['probabilities']}")
