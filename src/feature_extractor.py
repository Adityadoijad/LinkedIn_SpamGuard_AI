"""
Feature Extractor — LinkedIn SpamGuard AI
Extracts structured spam signals from raw job post text.
"""

import re
import math
from typing import Dict


# ── Keyword signal lists ──────────────────────────────────────────────────────

URGENCY_PATTERNS = [
    r"\burgent(ly)?\b", r"\bapply\s*(now|fast|today|immediately)\b",
    r"\bhurry\b", r"\blimited\s*(slots?|seats?|openings?)\b",
    r"\bdon'?t\s*miss\b", r"\blast\s*chance\b", r"\bdeadline\s*soon\b",
    r"\bfilling\s*fast\b", r"\bact\s*now\b",
]

VAGUE_COMPANY_PATTERNS = [
    r"\ba\s+(leading|top|reputed|well-known)\s+company\b",
    r"\bclient\s+of\s+ours\b", r"\bconfidential\s+(company|employer|client)\b",
    r"\bour\s+organization\b(?!.*[A-Z][a-z]+\s+(Inc|Corp|Ltd|LLC|Pvt))",
    r"\bundisclosed\s+company\b",
]

EXTERNAL_LINK_PATTERNS = [
    r"bit\.ly", r"tinyurl", r"wa\.me", r"whatsapp",
    r"t\.me", r"telegram", r"\bgmail\.com\b", r"yahoo\.com",
    r"hotmail\.com", r"forms\.gle", r"apply\s*(here|now)?\s*:?\s*https?://(?!linkedin|glassdoor|naukri|indeed)",
]

UNREALISTIC_SALARY_PATTERNS = [
    r"\$\s*[\d,]+\s*(/\s*(week|day|hour))", r"earn\s+\$?\d+[k+]?\s*(per)?\s*(week|day)",
    r"(lakh|lakhs)\s+(per|a)\s+(week|day)", r"unlimited\s+(earning|income)",
    r"earn\s+(upto|up\s+to)?\s*[\d,]+\s*(daily|weekly)",
    r"high\s+(pay|salary|income)\s*(guaranteed)?",
]

TOO_GOOD_PATTERNS = [
    r"\bno\s*(experience|qualification|degree)\s*(needed|required|necessary)\b",
    r"\bwork\s+from\s+home.*earn\b", r"\bpart[\s-]?time.*earn.*full[\s-]?time\b",
    r"\beasy\s+(money|income|job)\b", r"\bguaranteed\s+(income|salary|job)\b",
    r"\bpassive\s+income\b",
]

CONTACT_PATTERNS = [
    r"\+?\d[\d\s\-]{8,}\d",     # phone numbers
    r"\b[a-zA-Z0-9_.+-]+@(gmail|yahoo|hotmail|outlook)\.(com|in)\b",
    r"\bwhatsapp\b.*\d{7,}", r"\bcontact\s+(me|us)\s*(at|on|via)?\s*\+?\d",
]

# Real company signals (if present → lower spam likelihood)
COMPANY_SIGNALS = [
    r"\b(Inc|Corp|Ltd|LLC|Pvt|GmbH|S\.A\.)\b",
    r"\b(Google|Microsoft|Amazon|Apple|Meta|Netflix|IBM|Infosys|TCS|Wipro|Deloitte|Accenture|KPMG)\b",
]


# ── Helper functions ──────────────────────────────────────────────────────────

def _match_any(text: str, patterns: list) -> int:
    """Return 1 if any pattern matches, else 0."""
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return 1
    return 0


def _count_matches(text: str, patterns: list) -> int:
    """Count how many patterns match."""
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))


def _grammar_score(text: str) -> float:
    """
    Heuristic grammar quality score (0.0 = bad, 1.0 = good).
    Checks for ALL CAPS ratio, excessive punctuation, and very short sentences.
    """
    if not text:
        return 1.0
    words = text.split()
    if not words:
        return 1.0

    caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / len(words)
    exclamation_ratio = text.count("!") / max(len(text), 1) * 100
    question_ratio = text.count("?") / max(len(text), 1) * 100

    # Penalise ALL CAPS and excessive punctuation
    score = 1.0 - min(caps_ratio * 2, 0.6) - min(exclamation_ratio * 0.5, 0.2) - min(question_ratio * 0.3, 0.2)
    return round(max(0.0, min(1.0, score)), 3)


# ── Main extractor ────────────────────────────────────────────────────────────

def extract_features(text: str) -> Dict[str, float]:
    """
    Extract spam signal features from a raw job post string.

    Returns
    -------
    dict with keys:
        urgency, vague_company, no_company, unrealistic_salary,
        external_link, grammar_score, contact_info, too_good_to_be_true,
        spam_keyword_count, has_real_company
    """
    text = text.strip()

    urgency           = _match_any(text, URGENCY_PATTERNS)
    vague_company     = _match_any(text, VAGUE_COMPANY_PATTERNS)
    no_company        = int(not bool(re.search(r"[A-Z][a-z]+\s+(Inc|Corp|Ltd|LLC|Pvt|Technologies|Solutions|Services|Group)", text)))
    unrealistic_salary= _match_any(text, UNREALISTIC_SALARY_PATTERNS)
    external_link     = _match_any(text, EXTERNAL_LINK_PATTERNS)
    grammar_score_val = _grammar_score(text)
    contact_info      = _match_any(text, CONTACT_PATTERNS)
    too_good          = _match_any(text, TOO_GOOD_PATTERNS)
    spam_kw_count     = (
        _count_matches(text, URGENCY_PATTERNS) +
        _count_matches(text, UNREALISTIC_SALARY_PATTERNS) +
        _count_matches(text, TOO_GOOD_PATTERNS)
    )
    has_real_company  = _match_any(text, COMPANY_SIGNALS)

    exclamation_count = text.count("!")
    uppercase_ratio   = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    
    # Advanced NLP superficial signals
    text_length       = len(text)
    word_count        = len(text.split())
    question_count    = text.count("?")
    digit_count       = sum(c.isdigit() for c in text)

    return {
        "urgency":              urgency,
        "vague_company":        vague_company,
        "no_company":           no_company,
        "unrealistic_salary":   unrealistic_salary,
        "external_link":        external_link,
        "grammar_score":        grammar_score_val,
        "contact_info":         contact_info,
        "too_good_to_be_true":  too_good,
        "spam_keyword_count":   spam_kw_count,
        "has_real_company":     has_real_company,
        "exclamation_count":    exclamation_count,
        "uppercase_ratio":      uppercase_ratio,
        "text_length":          text_length,
        "word_count":           word_count,
        "question_count":       question_count,
        "digit_count":          digit_count,
    }


def features_to_list(features: Dict) -> list:
    """Convert feature dict to ordered list for model input."""
    keys = [
        "urgency", "vague_company", "no_company", "unrealistic_salary",
        "external_link", "grammar_score", "contact_info", "too_good_to_be_true",
        "spam_keyword_count", "has_real_company", "exclamation_count", "uppercase_ratio",
        "text_length", "word_count", "question_count", "digit_count"
    ]
    return [features[k] for k in keys]


FEATURE_NAMES = [
    "urgency", "vague_company", "no_company", "unrealistic_salary",
    "external_link", "grammar_score", "contact_info", "too_good_to_be_true",
    "spam_keyword_count", "has_real_company", "exclamation_count", "uppercase_ratio",
    "text_length", "word_count", "question_count", "digit_count"
]
