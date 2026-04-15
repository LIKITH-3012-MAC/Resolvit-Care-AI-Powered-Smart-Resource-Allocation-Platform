"""
Smart Resource Allocation — AI Classification Engine
Categorizes community need reports into predefined categories.
"""

import re
import math
from collections import Counter


# Category definitions with keyword patterns
CATEGORIES = {
    "food_support": {
        "keywords": ["food", "hunger", "meal", "nutrition", "starving", "malnourish", "ration", "grocery", "feed", "diet", "food kit", "food shortage", "cooking"],
        "weight": 1.0
    },
    "medical_emergency": {
        "keywords": ["medical", "health", "hospital", "doctor", "medicine", "fever", "disease", "illness", "injury", "sick", "patient", "clinic", "ambulance", "emergency", "infection", "epidemic", "vaccination", "covid"],
        "weight": 1.2
    },
    "medical_support": {
        "keywords": ["medicine delivery", "pharmacy", "prescription", "bedridden", "chronic", "diabetes", "blood pressure", "health camp", "checkup", "diagnosis"],
        "weight": 1.0
    },
    "education_support": {
        "keywords": ["school", "education", "student", "teacher", "book", "uniform", "tuition", "learning", "literacy", "classroom", "dropout", "scholarship"],
        "weight": 0.9
    },
    "shelter_need": {
        "keywords": ["shelter", "housing", "homeless", "displaced", "tent", "roof", "accommodation", "eviction", "house damage", "construction"],
        "weight": 1.1
    },
    "disaster_relief": {
        "keywords": ["flood", "earthquake", "cyclone", "storm", "disaster", "emergency", "rescue", "evacuation", "debris", "landslide", "fire", "collapse", "relief", "displaced"],
        "weight": 1.3
    },
    "women_safety": {
        "keywords": ["women", "safety", "harassment", "abuse", "domestic violence", "assault", "stalking", "threat", "protection", "streetlight", "unsafe"],
        "weight": 1.2
    },
    "child_welfare": {
        "keywords": ["child", "orphan", "minor", "abuse", "neglect", "adoption", "juvenile", "protection", "child labor", "trafficking"],
        "weight": 1.2
    },
    "sanitation": {
        "keywords": ["sanitation", "toilet", "sewage", "drainage", "garbage", "waste", "cleaning", "hygiene", "water supply", "contaminated", "pollution"],
        "weight": 0.9
    },
    "elderly_support": {
        "keywords": ["elderly", "senior", "old age", "bedridden", "pension", "geriatric", "wheelchair", "mobility", "caretaker"],
        "weight": 1.0
    }
}


def preprocess_text(text: str) -> str:
    """Normalize and clean input text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def compute_tf(text: str) -> dict:
    """Compute term frequency for text."""
    words = text.split()
    total = len(words) if words else 1
    freq = Counter(words)
    return {word: count / total for word, count in freq.items()}


def classify_report(text: str, title: str = "") -> dict:
    """
    Classify a community report into categories.
    
    Returns:
        dict with:
        - primary: top category
        - confidence: score 0-1
        - secondary: second best category (if close)
        - all_scores: dict of all category scores
        - keywords_matched: list of matched keywords
    """
    combined = preprocess_text(f"{title} {text}")
    tf = compute_tf(combined)
    
    scores = {}
    matched_keywords = {}
    
    for category, config in CATEGORIES.items():
        score = 0
        matches = []
        
        for keyword in config["keywords"]:
            kw_lower = keyword.lower()
            # Check for multi-word keywords
            if ' ' in kw_lower:
                if kw_lower in combined:
                    score += 2.0 * config["weight"]
                    matches.append(keyword)
            else:
                if kw_lower in tf:
                    score += tf[kw_lower] * 10 * config["weight"]
                    matches.append(keyword)
                elif kw_lower in combined:
                    score += 1.0 * config["weight"]
                    matches.append(keyword)
        
        scores[category] = round(score, 4)
        matched_keywords[category] = matches
    
    if not any(scores.values()):
        return {
            "primary": "uncategorized",
            "confidence": 0.0,
            "secondary": None,
            "all_scores": scores,
            "keywords_matched": []
        }
    
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top = sorted_cats[0]
    second = sorted_cats[1] if len(sorted_cats) > 1 else (None, 0)
    
    max_score = top[1]
    total_score = sum(scores.values()) or 1
    confidence = min(max_score / (total_score * 0.5), 1.0)
    
    result = {
        "primary": top[0],
        "confidence": round(confidence, 2),
        "secondary": second[0] if second[1] > max_score * 0.4 else None,
        "all_scores": scores,
        "keywords_matched": matched_keywords.get(top[0], [])
    }
    
    return result


def classify_batch(reports: list[dict]) -> list[dict]:
    """Classify multiple reports at once."""
    results = []
    for report in reports:
        text = report.get("description", "")
        title = report.get("title", "")
        classification = classify_report(text, title)
        results.append({
            "report_id": report.get("id"),
            **classification
        })
    return results
