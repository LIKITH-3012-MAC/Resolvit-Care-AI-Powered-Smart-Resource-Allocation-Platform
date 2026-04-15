"""
Smart Resource Allocation — Explainable AI Module
Generates human-readable explanations for all AI decisions.
"""


def explain_classification(classification: dict, report_text: str = "") -> str:
    """Generate explanation for why a report was classified a certain way."""
    primary = classification.get("primary", "unknown")
    confidence = classification.get("confidence", 0)
    secondary = classification.get("secondary")
    keywords = classification.get("keywords_matched", [])
    
    parts = []
    
    # Primary classification
    readable = primary.replace("_", " ").title()
    parts.append(f"Classified as \"{readable}\" with {confidence:.0%} confidence.")
    
    # Keywords evidence
    if keywords:
        kw_str = ", ".join(f"'{k}'" for k in keywords[:5])
        parts.append(f"Based on detected keywords: {kw_str}.")
    
    # Secondary classification
    if secondary:
        sec_readable = secondary.replace("_", " ").title()
        parts.append(f"Secondary concern detected: {sec_readable}.")
    
    # Low confidence warning
    if confidence < 0.5:
        parts.append("⚠ Low confidence — manual review recommended.")
    
    return " ".join(parts)


def explain_priority(priority_result: dict, report: dict = None) -> str:
    """Generate detailed explanation for priority scoring."""
    score = priority_result.get("score", 0)
    level = priority_result.get("level", "medium")
    breakdown = priority_result.get("breakdown", {})
    
    parts = []
    parts.append(f"🔴 Priority: {level.upper()} ({score}/100)")
    
    # Top factors
    sorted_factors = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    
    factor_explanations = {
        "severity": "severity of the reported issue",
        "people_affected": "number of people impacted",
        "vulnerability": "presence of vulnerable populations (elderly, children, etc.)",
        "time_criticality": "urgency and time-sensitivity of the need",
        "resource_gap": "scarcity of available resources",
        "repeat_frequency": "repeated occurrence of similar issues",
        "verification_confidence": "confidence in report verification",
        "fairness_boost": "priority boost for historically underserved areas",
    }
    
    parts.append("\nKey factors (highest to lowest impact):")
    for factor, score_val in sorted_factors[:4]:
        desc = factor_explanations.get(factor, factor)
        bar = "█" * int(score_val / 10) + "░" * (10 - int(score_val / 10))
        parts.append(f"  • {desc}: {bar} {score_val}/100")
    
    # Context from report
    if report:
        people = report.get("people_affected", 0)
        vuln = report.get("vulnerable_group", "")
        cat = report.get("category", "")
        
        if people > 0:
            parts.append(f"\n{people} people are directly affected.")
        if vuln:
            parts.append(f"Vulnerable groups involved: {vuln}.")
        if cat:
            parts.append(f"Issue type: {cat.replace('_', ' ')}.")
    
    return "\n".join(parts)


def explain_match(match_result: dict, volunteer: dict = None, task: dict = None) -> str:
    """Generate explanation for why a volunteer was matched to a task."""
    name = match_result.get("volunteer_name", "Volunteer")
    score = match_result.get("score", 0)
    distance = match_result.get("distance_km", 0)
    breakdown = match_result.get("breakdown", {})
    
    parts = []
    parts.append(f"✅ Recommended: {name} (match score: {score}/100)")
    
    reasons = []
    
    # Skill
    if breakdown.get("skill_fit", 0) >= 70:
        if volunteer:
            skills = volunteer.get("skill_tags", [])
            reasons.append(f"strong skill match ({', '.join(skills[:3])})")
        else:
            reasons.append("strong skill match")
    
    # Distance
    if distance > 0:
        if distance <= 2:
            reasons.append(f"very close proximity ({distance}km)")
        elif distance <= 10:
            reasons.append(f"nearby ({distance}km away)")
        else:
            reasons.append(f"within travel range ({distance}km)")
    
    # Reliability
    if breakdown.get("reliability", 0) >= 80:
        rel = volunteer.get("reliability_score", 0) if volunteer else breakdown["reliability"]
        reasons.append(f"high reliability ({rel}%)")
    
    # Language
    if breakdown.get("language", 0) >= 80 and volunteer:
        langs = volunteer.get("languages", [])
        reasons.append(f"speaks {', '.join(langs[:2])}")
    
    # Availability
    if breakdown.get("availability", 0) >= 80:
        reasons.append("currently available")
    
    # Workload
    if breakdown.get("workload", 0) >= 80:
        reasons.append("low current workload")
    
    # Safety
    if breakdown.get("safety_suitability", 0) >= 90:
        reasons.append("safety-appropriate for this task")
    
    if reasons:
        parts.append("Reasons: " + ", ".join(reasons) + ".")
    
    # Completed tasks history
    if volunteer:
        completed = volunteer.get("total_tasks_completed", 0)
        if completed > 0:
            parts.append(f"Track record: {completed} tasks completed successfully.")
    
    return "\n".join(parts)


def explain_hotspot(cluster: dict) -> str:
    """Generate explanation for hotspot detection."""
    level = cluster.get("hotspot_level", "low")
    count = cluster.get("member_count", 0)
    people = cluster.get("total_people_affected", 0)
    avg_urgency = cluster.get("avg_urgency", 0)
    top_cat = cluster.get("top_category", "unknown").replace("_", " ").title()
    
    level_emoji = {"severe": "🔴", "high": "🟠", "moderate": "🟡", "low": "🟢"}
    emoji = level_emoji.get(level, "⚪")
    
    parts = [
        f"{emoji} Hotspot Level: {level.upper()}",
        f"  • {count} reported needs in this area",
        f"  • {people} total people affected",
        f"  • Average urgency: {avg_urgency}/100",
        f"  • Primary concern: {top_cat}",
    ]
    
    if level in ("severe", "high"):
        parts.append("  ⚠ Immediate attention recommended for this zone.")
    
    return "\n".join(parts)
