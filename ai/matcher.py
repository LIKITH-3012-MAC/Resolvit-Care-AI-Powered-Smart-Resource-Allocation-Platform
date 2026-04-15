"""
Smart Resource Allocation — Volunteer-Task Matching Engine
Intelligently matches volunteers to tasks using weighted scoring.
"""

import math


# Matching weight configuration
MATCH_WEIGHTS = {
    "skill_fit": 0.30,
    "distance": 0.25,
    "availability": 0.15,
    "reliability": 0.12,
    "workload": 0.08,
    "language": 0.05,
    "safety_suitability": 0.05,
}

# Skill-to-task mapping
TASK_SKILL_MAP = {
    "food_distribution": ["food_distribution", "logistics", "cooking", "community_outreach"],
    "health_camp": ["medical", "first_aid", "health_camp", "vaccination"],
    "medicine_delivery": ["medical", "logistics", "transport"],
    "education_support": ["teaching", "education", "child_welfare", "counseling"],
    "disaster_response": ["emergency_response", "logistics", "transport", "first_aid"],
    "women_support": ["women_support", "counseling", "emergency_response"],
    "child_welfare": ["child_welfare", "counseling", "teaching"],
    "shelter_setup": ["logistics", "transport", "warehouse"],
    "sanitation": ["logistics", "community_outreach"],
    "elderly_care": ["medical", "community_outreach", "logistics"],
    "field_survey": ["field_survey", "community_outreach"],
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers."""
    R = 6371  # Earth radius in km
    
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def compute_skill_score(volunteer_skills: list, task_type: str) -> float:
    """Score based on skill-task fit (0-100)."""
    required_skills = TASK_SKILL_MAP.get(task_type, [])
    
    if not required_skills:
        return 50  # Neutral for unknown task types
    
    if not volunteer_skills:
        return 10
    
    v_skills = set(s.lower() for s in volunteer_skills)
    r_skills = set(s.lower() for s in required_skills)
    
    matched = v_skills.intersection(r_skills)
    
    if not matched:
        return 15
    
    # Primary skill match gets more weight
    primary_match = required_skills[0].lower() in v_skills
    score = (len(matched) / len(r_skills)) * 80
    
    if primary_match:
        score += 20
    
    return min(score, 100)


def compute_distance_score(vol_lat: float, vol_lon: float,
                           task_lat: float, task_lon: float,
                           travel_radius: float) -> float:
    """Score based on geographic proximity (0-100)."""
    if not all([vol_lat, vol_lon, task_lat, task_lon]):
        return 50
    
    distance = haversine_km(vol_lat, vol_lon, task_lat, task_lon)
    
    if distance <= 1:
        return 100
    elif distance <= 5:
        return 90
    elif distance <= travel_radius * 0.5:
        return 75
    elif distance <= travel_radius:
        return 55
    elif distance <= travel_radius * 1.5:
        return 30
    else:
        return max(10, 100 - distance * 3)


def compute_availability_score(availability: str) -> float:
    """Score based on volunteer availability status."""
    scores = {
        "available": 100,
        "busy": 20,
        "on_leave": 5,
        "offline": 0,
    }
    return scores.get(availability, 0)


def compute_reliability_score(reliability: float) -> float:
    """Direct score from reliability rating (0-100)."""
    return min(max(reliability, 0), 100)


def compute_workload_score(current_tasks: int) -> float:
    """Inverse score — lower workload = higher score."""
    if current_tasks <= 0:
        return 100
    elif current_tasks == 1:
        return 80
    elif current_tasks == 2:
        return 60
    elif current_tasks <= 4:
        return 35
    else:
        return max(5, 100 - current_tasks * 15)


def compute_language_score(vol_languages: list, required_language: str = "") -> float:
    """Score based on language compatibility."""
    if not required_language:
        return 70  # Neutral
    
    vol_langs = [l.lower() for l in vol_languages]
    
    if required_language.lower() in vol_langs:
        return 100
    
    # English as fallback
    if "english" in vol_langs:
        return 50
    
    return 20


def compute_safety_score(task_type: str, volunteer_gender: str = "",
                         time_of_day: str = "day") -> float:
    """Score for safety suitability based on task context."""
    sensitive_tasks = ["women_support", "child_welfare"]
    
    if task_type not in sensitive_tasks:
        return 80  # Neutral for non-sensitive tasks
    
    score = 50
    
    if task_type == "women_support" and volunteer_gender == "female":
        score = 95
    elif task_type == "child_welfare":
        score = 75
    
    if time_of_day == "night":
        score = max(score - 20, 10)
    
    return score


def match_volunteer_to_task(volunteer: dict, task: dict) -> dict:
    """
    Compute match score between a volunteer and a task.
    
    Args:
        volunteer: dict with keys: skill_tags, latitude, longitude,
                   availability, reliability_score, current_workload,
                   languages, gender, travel_radius_km, user_id, name
        task: dict with keys: task_type, latitude, longitude,
              required_language, time_context
    
    Returns:
        dict with: score, breakdown, explanation
    """
    skill_s = compute_skill_score(
        volunteer.get("skill_tags", []),
        task.get("task_type", "")
    )
    
    distance_s = compute_distance_score(
        volunteer.get("latitude", 0), volunteer.get("longitude", 0),
        task.get("latitude", 0), task.get("longitude", 0),
        volunteer.get("travel_radius_km", 10)
    )
    
    avail_s = compute_availability_score(volunteer.get("availability", "offline"))
    reliability_s = compute_reliability_score(volunteer.get("reliability_score", 50))
    workload_s = compute_workload_score(volunteer.get("current_workload", 0))
    
    language_s = compute_language_score(
        volunteer.get("languages", []),
        task.get("required_language", "")
    )
    
    safety_s = compute_safety_score(
        task.get("task_type", ""),
        volunteer.get("gender", ""),
        task.get("time_context", "day")
    )
    
    # Weighted total
    total = (
        MATCH_WEIGHTS["skill_fit"] * skill_s +
        MATCH_WEIGHTS["distance"] * distance_s +
        MATCH_WEIGHTS["availability"] * avail_s +
        MATCH_WEIGHTS["reliability"] * reliability_s +
        MATCH_WEIGHTS["workload"] * workload_s +
        MATCH_WEIGHTS["language"] * language_s +
        MATCH_WEIGHTS["safety_suitability"] * safety_s
    )
    
    total = round(min(max(total, 0), 100), 2)
    
    breakdown = {
        "skill_fit": round(skill_s, 1),
        "distance": round(distance_s, 1),
        "availability": round(avail_s, 1),
        "reliability": round(reliability_s, 1),
        "workload": round(workload_s, 1),
        "language": round(language_s, 1),
        "safety_suitability": round(safety_s, 1),
    }
    
    # Generate explanation
    dist = 0
    if all([volunteer.get("latitude"), volunteer.get("longitude"),
            task.get("latitude"), task.get("longitude")]):
        dist = round(haversine_km(
            volunteer["latitude"], volunteer["longitude"],
            task["latitude"], task["longitude"]
        ), 1)
    
    explanation = _generate_match_explanation(volunteer, task, total, breakdown, dist)
    
    return {
        "volunteer_id": volunteer.get("user_id"),
        "volunteer_name": volunteer.get("name", "Unknown"),
        "score": total,
        "distance_km": dist,
        "breakdown": breakdown,
        "explanation": explanation,
    }


def _generate_match_explanation(vol: dict, task: dict, score: float,
                                 breakdown: dict, distance: float) -> str:
    """Generate human-readable match explanation."""
    name = vol.get("name", "Volunteer")
    parts = [f"Assigned to {name} (match score: {score}/100):"]
    
    # Skill match
    matched_skills = set(s.lower() for s in vol.get("skill_tags", []))
    task_skills = set(s.lower() for s in TASK_SKILL_MAP.get(task.get("task_type", ""), []))
    overlap = matched_skills.intersection(task_skills)
    if overlap:
        parts.append(f"skill match ({', '.join(overlap)})")
    
    # Distance
    if distance > 0:
        parts.append(f"{distance}km proximity")
    
    # Reliability
    rel = vol.get("reliability_score", 0)
    if rel >= 80:
        parts.append(f"high reliability ({rel}%)")
    
    # Languages
    langs = vol.get("languages", [])
    if langs:
        parts.append(f"speaks {', '.join(langs[:2])}")
    
    # Availability
    if vol.get("availability") == "available":
        parts.append("currently available")
    
    return ", ".join(parts) + "."


def find_best_matches(volunteers: list[dict], task: dict,
                      top_n: int = 5, min_score: float = 30) -> list[dict]:
    """
    Find the best volunteer matches for a given task.
    
    Returns top N matches sorted by score, filtered by minimum threshold.
    """
    matches = []
    
    for volunteer in volunteers:
        # Skip unavailable volunteers
        if volunteer.get("availability") in ("offline", "on_leave"):
            continue
        
        result = match_volunteer_to_task(volunteer, task)
        
        if result["score"] >= min_score:
            matches.append(result)
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:top_n]
