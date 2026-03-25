"""
Train Model — LinkedIn SpamGuard AI
Trains an XGBoost classifier on extracted features and saves the model.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
import matplotlib.pyplot as plt

from src.feature_extractor import extract_features, FEATURE_NAMES
from src.dataset_generator import generate_dataset

MODEL_PATH = "models/spam_classifier.pkl"
DATA_PATH  = "data/sample_jobs.csv"


def load_or_generate_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        print("⚠  Dataset not found — generating synthetic data...")
        generate_dataset(n_each=80, output_path=DATA_PATH)
    return pd.read_csv(DATA_PATH)


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    print("🔧 Extracting features from text...")
    feature_rows = df["text"].apply(lambda t: pd.Series(extract_features(t)))
    return feature_rows


def train(save_path: str = MODEL_PATH):
    os.makedirs("models", exist_ok=True)

    df = load_or_generate_data()
    print(f"📊 Loaded {len(df)} samples | Label distribution:\n{df['label_name'].value_counts().to_string()}\n")

    X = build_feature_matrix(df)
    y = df["label"]

    # EXPLANATION: We use an 80/20 train/test split. 
    # 80% is given to the model to learn the feature patterns (spam keywords, text length, etc.)
    # 20% is held back completely blind to evaluate generalization and prevent overfitting.
    # We use 'stratify=y' to ensure the exact same FAKE/LEGIT ratio exists in both sets!
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("🤖 Training XGBoost classifier...")
    
    # Class Imbalance Handling: 
    # Compute balanced weights for each sample so the model doesn't over-bias towards the majority class.
    from sklearn.utils.class_weight import compute_sample_weight
    sample_weights = compute_sample_weight(class_weight='balanced', y=y_train)
    
    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
    )
    
    # Train applying the balancing weights
    model.fit(X_train, y_train, sample_weight=sample_weights)

    y_pred = model.predict(X_test)
    
    # Generate requested explicit metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted')
    rec = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print("\n📈 Model Evaluation Metrics:")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    print("\n🚨 Class Confusion Matrix:")
    print("(Shows True Positives vs False Positives - crucial for spam classification)")
    print(confusion_matrix(y_test, y_pred))
    
    print("\n📊 Detailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["FAKE", "SUSPICIOUS", "LEGIT"]))

    print("🧩 Feature Importances:")
    importances = list(zip(FEATURE_NAMES, model.feature_importances_))
    importances.sort(key=lambda x: x[1], reverse=True)
    for name, score in importances:
        print(f"  - {name:20}: {score:.4f}")
        
    # Generate Feature Importance Bar Chart
    plt.figure(figsize=(10, 6))
    sorted_names = [x[0] for x in importances]
    sorted_scores = [x[1] for x in importances]
    plt.barh(sorted_names[::-1], sorted_scores[::-1], color='indigo')
    plt.xlabel('XGBoost Feature Importance')
    plt.title('LinkedIn Job Spam - Feature Contributions')
    plt.tight_layout()
    plt.savefig("models/feature_importance.png")
    print("📈 Feature importance chart saved to models/feature_importance.png")

    joblib.dump(model, save_path)
    print(f"\n✅ Model saved → {save_path}")
    return model


if __name__ == "__main__":
    train()
