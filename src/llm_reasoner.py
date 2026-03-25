"""
LLM Reasoner — LinkedIn SpamGuard AI
Interprets the ML features and output, returning a human-readable explanation using Google Gemini.
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any

def get_llm_reasoning(text: str, features: Dict[str, float], ml_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call Gemini LLM to provide human-readable explanation of the spam analysis.
    Gracefully falls back to a deterministic response if no API key is available.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        # Fallback if no API key is provided
        return _fallback_reasoning(features, ml_result)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        
        prompt = f"""
        You are an expert cybersecurity and recruitment fraud analyst.
        Analyze this LinkedIn job post and explain why the ML model classified it as {ml_result['verdict']}.
        
        Job Post Text:
        "{text}"
        
        Extracted Signals (1 means present, 0 means absent):
        {json.dumps(features, indent=2)}
        
        ML Model Verdict: {ml_result['verdict']} (Confidence: {ml_result['confidence']}%)
        
        Provide a JSON response with the following structure exactly:
        {{
            "explanation": "A concise 2-3 sentence explanation of the verdict.",
            "risk_factors": ["A specific risk factor identified", "Another risk factor"],
            "recommendation": "A 1-sentence recommendation for the user (e.g. 'Do not click the link' or 'Safe to apply')."
        }}
        
        Only return the JSON object, nothing else. Make the tone professional and helpful.
        If the verdict is LEGIT, the risk_factors array should be empty or mention why it's safe.
        """
        
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        # Ensure the expected keys exist
        if "explanation" not in result:
            result["explanation"] = "API response format error."
        if "risk_factors" not in result:
            result["risk_factors"] = []
        if "recommendation" not in result:
            result["recommendation"] = ""
            
        return result
        
    except Exception as e:
        print(f"LLM API Error: {e}")
        return _fallback_reasoning(features, ml_result)

def _fallback_reasoning(features: Dict[str, float], ml_result: Dict[str, Any]) -> Dict[str, Any]:
    """Rule-based fallback explanation when LLM API isn't available."""
    
    verdict = ml_result["verdict"]
    factors = []
    
    if features.get("urgency"): factors.append("Uses high-pressure urgency keywords")
    if features.get("vague_company"): factors.append("Company identity is vague or hidden")
    if features.get("no_company"): factors.append("No clear company name mentioned")
    if features.get("unrealistic_salary"): factors.append("Promises unrealistically high compensation")
    if features.get("external_link"): factors.append("Contains suspicious tracking or chat links")
    if features.get("contact_info"): factors.append("Asks to contact via personal email or WhatsApp")
    if features.get("too_good_to_be_true"): factors.append("Job requirements are suspiciously low for the pay")
    if features.get("grammar_score", 1.0) < 0.7: factors.append("Poor grammar, excessive capitals or punctuation")
    
    if verdict == "FAKE":
        exp = "This job post exhibits multiple strong indicators of being a scam."
        rec = "DO NOT apply, share personal information, or pay any fees."
    elif verdict == "SUSPICIOUS":
        exp = "This post has some unusual patterns common in low-quality or potentially fraudulent listings."
        rec = "Proceed with caution. Verify the company independently before applying."
    else:
        exp = "This post appears to follow standard professional recruiting patterns without obvious red flags."
        factors = ["Mentions specific role, requirements, and realistic expectations"]
        if features.get("has_real_company"):
            factors.append("References a known corporate entity or standard business structure")
        rec = "Looks safe to apply through standard official channels."
        
    return {
        "explanation": f"[Auto-generated] {exp}",
        "risk_factors": factors,
        "recommendation": rec
    }
