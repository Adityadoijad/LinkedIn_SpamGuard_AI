from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys
import os
import json
import datetime
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.predict import predict_spam
from src.llm_reasoner import get_llm_reasoning

app = FastAPI(title="LinkedIn SpamGuard AI API")

# 2. Secure Backend (API & CORS)
# Tighter CORS restrictions (only allow trusted frontend domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 8. Rate Limiting (Simple in-memory token bucket/dictionary)
RATE_LIMIT_STORE = {}
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECS = 60

def check_rate_limit(ip: str):
    current_time = time.time()
    if ip not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[ip] = []
    
    # Clean up old requests
    RATE_LIMIT_STORE[ip] = [t for t in RATE_LIMIT_STORE[ip] if current_time - t < RATE_LIMIT_WINDOW_SECS]
    
    if len(RATE_LIMIT_STORE[ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    RATE_LIMIT_STORE[ip].append(current_time)

# 6. Input Validation
class JobPostRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=2000, description="The job post text to analyze")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API is running securely"}

@app.post("/analyze")
def analyze_job_post(request: JobPostRequest, req: Request):
    # Apply Rate Limiting
    client_ip = req.client.host if req.client else "127.0.0.1"
    check_rate_limit(client_ip)
    
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty or just whitespace.")
        
    try:
        # 1. Run ML Pipeline (Feature Extraction + XGBoost)
        prediction = predict_spam(text)
        
        # 3. Robust Error Handling & 7. Fallback Logic
        reasoning = None
        try:
            reasoning = get_llm_reasoning(
                text=text,
                features=prediction["features"],
                ml_result=prediction["ml_result"]
            )
        except Exception as llm_err:
            print(f"LLM Error: {llm_err}")
            # Fallback when LLM fails entirely
            reasoning = {
                "explanation": "LLM Service unavailable. Relying on Core ML Prediction.",
                "risk_factors": ["Could not generate dynamic details. Proceed with standard caution."],
                "recommendation": f"Model confidence is {prediction['ml_result']['confidence']}%. Take ML prediction as primary truth."
            }
        
        # 4. Explicit Decision Logic (ML takes absolute precedence)
        # Final Verdict is cleanly defined by the core ML engine, not the LLM.
        if prediction["ml_result"]["confidence"] >= 70:
            final_verdict = prediction["ml_result"]["verdict"]
        else:
            final_verdict = "UNCERTAIN"
        
        # Final output object
        result_payload = {
            "verdict": final_verdict,
            "spam_score": prediction["ml_result"]["confidence"],
            "ml_probabilities": prediction["ml_result"]["probabilities"],
            "features": prediction["features"],
            "analysis": reasoning
        }
        
        # 5. Add Logging System
        os.makedirs("data", exist_ok=True)
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "ip": client_ip,
            "text": text[:500] + ("..." if len(text) > 500 else ""), # Truncate long text in logs
            "features": prediction["features"],
            "prediction": prediction["ml_result"]["verdict"],
            "confidence": prediction["ml_result"]["confidence"]
        }
        with open("data/logs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return result_payload
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Ensure system never crashes hard for the user
        raise HTTPException(status_code=500, detail="Internal ML Pipeline Error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
