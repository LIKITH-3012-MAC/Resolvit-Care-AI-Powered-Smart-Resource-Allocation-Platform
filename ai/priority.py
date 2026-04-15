"""
Smart Resource Allocation — Priority Scoring Engine
Computes urgency/priority scores using weighted multi-factor formula.
"""

import math
from datetime import datetime, timezone


# Weight configuration (sums to ~1.0 for normalization)
WEIGHTS = {
    "severity": 0.25,
    "people_affected": 0.20,
    "vulnerability": 0.15,
    "time_criticality": 0.15,
    "resource_gap": 0.10,
    "repeat_frequency": 0.08,
    "verification_confidence": 0.04,
    "fairness_boost": 0.03,
}

# Vulnerability multipliers
VULNERABILITY_SCORES = {
    "elderly": 0.85,
    "children": 0.90,
    "bedridden": 0.95,
    "disabled": 0.90,
    "pregnant": 0.88,
    "women": 0.75,
    "families": 0.70,
    "infants": 0.95,
}

# Priority level thresholds
PRIORITY_LEVELS = {
    "critical": (76, 100),
    "high": (56, 75),
    "medium": (31, 55),
    "low": (0, 30),
}


def compute_severity_score(severity: int) -> float:
    """Normalize severity (1-10) to 0-100 scale."""
    return min(max(severity, 1), 10) * 10


def compute_people_score(people_affected: int) -> float:
    """Log-scaled score for number of people affected."""
    if people_affected <= 0:
        return 10
    # Log scaling: 1 person = ~10, 10 = ~50, 100 = ~80, 1000 = ~100
    return min(10 + 30 * math.log10(max(people_affected, 1)), 100)


def compute_vulnerability_score(vulnerable_groups: str) -> float:
    """Score based on presence of vulnerable populations."""
    if not vulnerable_groups:
        return 20
    
    groups = [g.strip().lower() for g in vulnerable_groups.split(",")]
    scores = []
    
    for group in groups:
        for key, value in VULNERABILITY_SCORES.items():
            if key in group:
                scores.append(value)
                break
    
    if not scores:
        return 30
    
    # Combine: max vulnerability + bonus for multiple groups
    max_v = max(scores)
    multi_bonus = min(len(scores) - 1, 3) * 0.03
    return min((max_v + multi_bonus) * 100, 100)


def compute_time_criticality(created_at: str, category: str = "") -> float:
    """Score based on how time-sensitive the need is."""
    # Category-based base urgency
    urgent_categories = {
        "disaster_relief": 90,
        "medical_emergency": 85,
        "women_safety": 75,
        "food_support": 65,
        "child_welfare": 70,
        "medical_support": 60,
    }
    
    base = urgent_categories.get(category, 40)
    
    # Age factor: older reports get higher urgency
    if created_at:
        try:
            if isinstance(created_at, str):
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created = created_at
            
            now = datetime.now(timezone.utc)
            hours_old = (now - created).total_seconds() / 3600
            
            age_bonus = min(hours_old * 0.5, 20)  # Max 20 point bonus for old reports
            return min(base + age_bonus, 100)
        except (ValueError, TypeError):
            pass
    
    return base


def compute_resource_gap(available_resources: int = -1, needed_resources: int = 1) -> float:
    """Score based on resource scarcity."""
    if available_resources < 0:
        return 50  # Unknown
    if available_resources == 0:
        return 100
    ratio = needed_resources / max(available_resources, 1)
    return min(ratio * 60, 100)


def compute_repeat_frequency(repeat_count: int = 0) -> float:
    """Score for repeat occurrences of same issue."""
    if repeat_count <= 0:
        return 10
    return min(10 + repeat_count * 15, 100)


def compute_verification_confidence(status: str) -> float:
    """Score based on verification status."""
    scores = {
        "verified": 90,
        "needs_review": 60,
        "pending": 40,
        "rejected": 10,
    }
    return scores.get(status, 40)


def compute_fairness_boost(location_risk_index: float = 0, recent_support_count: int = 0) -> float:
    """Fairness scoring to prevent neglect of underserved areas."""
    # High risk index + low recent support = high fairness boost
    risk_factor = min(location_risk_index * 100, 100)
    neglect_factor = max(80 - recent_support_count * 10, 0)
    return (risk_factor * 0.6 + neglect_factor * 0.4)


def calculate_priority(report: dict) -> dict:
    """
    Calculate comprehensive priority score for a community report.
    
    Args:
        report: dict with keys:
            - severity (int 1-10)
            - people_affected (int)
            - vulnerable_group (str, comma-separated)
            - created_at (str, ISO format)
            - category (str)
            - verification_status (str)
            - repeat_count (int, optional)
            - available_resources (int, optional)
            - location_risk_index (float 0-1, optional)
            - recent_support_count (int, optional)
    
    Returns:
        dict with score, level, breakdown, and explanation
    """
    
    # Compute individual factor scores
    severity_s = compute_severity_score(report.get("severity", 5))
    people_s = compute_people_score(report.get("people_affected", 1))
    vuln_s = compute_vulnerability_score(report.get("vulnerable_group", ""))
    time_s = compute_time_criticality(report.get("created_at", ""), report.get("category", ""))
    resource_s = compute_resource_gap(report.get("available_resources", -1))
    repeat_s = compute_repeat_frequency(report.get("repeat_count", 0))
    verify_s = compute_verification_confidence(report.get("verification_status", "pending"))
    fairness_s = compute_fairness_boost(
        report.get("location_risk_index", 0.5),
        report.get("recent_support_count", 0)
    )
    
    # Weighted sum
    total = (
        WEIGHTS["severity"] * severity_s +
        WEIGHTS["people_affected"] * people_s +
        WEIGHTS["vulnerability"] * vuln_s +
        WEIGHTS["time_criticality"] * time_s +
        WEIGHTS["resource_gap"] * resource_s +
        WEIGHTS["repeat_frequency"] * repeat_s +
        WEIGHTS["verification_confidence"] * verify_s +
        WEIGHTS["fairness_boost"] * fairness_s
    )
    
    total = round(min(max(total, 0), 100), 1)
    
    # Determine level
    level = "low"
    for lev, (lo, hi) in PRIORITY_LEVELS.items():
        if lo <= total <= hi:
            level = lev
            break
    
    # Build explanation
    breakdown = {
        "severity": round(severity_s, 1),
        "people_affected": round(people_s, 1),
        "vulnerability": round(vuln_s, 1),
        "time_criticality": round(time_s, 1),
        "resource_gap": round(resource_s, 1),
        "repeat_frequency": round(repeat_s, 1),
        "verification_confidence": round(verify_s, 1),
        "fairness_boost": round(fairness_s, 1),
    }
    
    explanation = _generate_explanation(report, total, level, breakdown)
    
    return {
        "score": total,
        "level": level,
        "breakdown": breakdown,
        "explanation": explanation
    }


def _generate_explanation(report: dict, score: float, level: str, breakdown: dict) -> str:
    """Generate human-readable explanation for priority decision."""
    parts = []
    
    parts.append(f"Priority Score: {score}/100 ({level.upper()})")
    
    # Top contributing factors
    sorted_factors = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    top_factors = sorted_factors[:3]
    
    factor_names = {
        "severity": "severity rating",
        "people_affected": "number of people affected",
        "vulnerability": "vulnerable populations",
        "time_criticality": "time sensitivity",
        "resource_gap": "resource scarcity",
        "repeat_frequency": "repeated occurrence",
        "verification_confidence": "verification status",
        "fairness_boost": "underserved area priority",
    }
    
    top_strs = [f"{factor_names.get(f, f)} ({v}/100)" for f, v in top_factors]
    parts.append(f"Top factors: {', '.join(top_strs)}.")
    
    people = report.get("people_affected", 0)
    if people > 0:
        parts.append(f"{people} people affected.")
    
    vuln = report.get("vulnerable_group", "")
    if vuln:
        parts.append(f"Vulnerable groups: {vuln}.")
    
    cat = report.get("category", "")
    if cat:
        parts.append(f"Category: {cat.replace('_', ' ')}.")
    
    return " ".join(parts)


def prioritize_batch(reports: list[dict]) -> list[dict]:
    """Calculate priorities for multiple reports and sort by score."""
    results = []
    for report in reports:
        priority = calculate_priority(report)
        results.append({
            "report_id": report.get("id"),
            **priority
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)
