# LinkedIn SpamGuard AI — Professional Commit Script

Write-Host "🚀 Starting structured commit sequence for LinkedIn SpamGuard AI..." -ForegroundColor Cyan

# 1. Feature Engineering & ML Pipeline Logic
git add src/feature_extractor.py src/predict.py src/train_model.py app/main.py
git commit -m "feat: implement advanced feature engineering and strict ML decision logic

- Extracted text_length, word_count, digit_count, and question_count signals.
- Set 70% confidence threshold for ML-primary verdicts.
- Integrated sklearn balanced sample weights for class imbalance handling."

# 2. Dataset & Interpretability
git add src/dataset_generator.py models/feature_importance.png
git commit -m "feat: enhance dataset hybridity and model interpretability

- Merged real-world manual samples into synthetic training pipeline.
- Added matplotlib-based feature importance visualization for model auditing."

# 3. Branding & UX Rebranding
git add .
git commit -m "style: global rebrand to LinkedIn SpamGuard AI and UI polish

- Renamed project across all Python headers, FastAPI titles, and Frontend components.
- Integrated premium dark-mode glassmorphism UI with animated indicators.
- Revamped README with professional architecture diagrams and recruiter-targeted highlights."

Write-Host "✅ Project successfully committed with descriptive, industry-standard messages!" -ForegroundColor Green
