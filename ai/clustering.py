"""
Smart Resource Allocation — Geospatial Clustering Engine
Detects hotspots using K-means and density-based clustering.
"""

import math
import random
from collections import defaultdict


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two coordinates."""
    R = 6371
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def kmeans_cluster(points, k=5, max_iterations=100):
    """
    K-means clustering on geographic coordinates.
    
    Args:
        points: list of dicts with 'latitude', 'longitude', and optional metadata
        k: number of clusters
        max_iterations: convergence limit
    
    Returns:
        list of cluster dicts with centroid, members, and stats
    """
    if not points or len(points) < k:
        k = max(len(points), 1)
    
    # Initialize centroids using K-means++ style
    centroids = []
    available = list(range(len(points)))
    
    # First centroid: random
    first = random.choice(available)
    centroids.append((points[first]["latitude"], points[first]["longitude"]))
    available.remove(first)
    
    # Subsequent centroids: farthest point heuristic
    for _ in range(1, k):
        if not available:
            break
        max_dist = -1
        best_idx = available[0]
        for idx in available:
            min_d = min(
                haversine_km(points[idx]["latitude"], points[idx]["longitude"], c[0], c[1])
                for c in centroids
            )
            if min_d > max_dist:
                max_dist = min_d
                best_idx = idx
        centroids.append((points[best_idx]["latitude"], points[best_idx]["longitude"]))
        available.remove(best_idx)
    
    # Iterate
    assignments = [0] * len(points)
    
    for iteration in range(max_iterations):
        changed = False
        
        # Assign each point to nearest centroid
        for i, point in enumerate(points):
            min_dist = float('inf')
            best_c = 0
            for j, (clat, clon) in enumerate(centroids):
                d = haversine_km(point["latitude"], point["longitude"], clat, clon)
                if d < min_dist:
                    min_dist = d
                    best_c = j
            if assignments[i] != best_c:
                assignments[i] = best_c
                changed = True
        
        if not changed:
            break
        
        # Recompute centroids
        for j in range(len(centroids)):
            members = [points[i] for i in range(len(points)) if assignments[i] == j]
            if members:
                avg_lat = sum(m["latitude"] for m in members) / len(members)
                avg_lon = sum(m["longitude"] for m in members) / len(members)
                centroids[j] = (avg_lat, avg_lon)
    
    # Build results
    clusters = []
    for j in range(len(centroids)):
        members = [points[i] for i in range(len(points)) if assignments[i] == j]
        if not members:
            continue
        
        # Calculate cluster stats
        urgency_scores = [m.get("urgency_score", 0) for m in members]
        severity_scores = [m.get("severity", 5) for m in members]
        total_people = sum(m.get("people_affected", 1) for m in members)
        
        # Cluster radius
        max_radius = 0
        for m in members:
            d = haversine_km(m["latitude"], m["longitude"], centroids[j][0], centroids[j][1])
            max_radius = max(max_radius, d)
        
        categories = defaultdict(int)
        for m in members:
            cat = m.get("category", "unknown")
            categories[cat] += 1
        
        cluster = {
            "cluster_id": j,
            "centroid": {
                "latitude": round(centroids[j][0], 6),
                "longitude": round(centroids[j][1], 6),
            },
            "member_count": len(members),
            "total_people_affected": total_people,
            "avg_urgency": round(sum(urgency_scores) / len(urgency_scores), 1) if urgency_scores else 0,
            "max_urgency": max(urgency_scores) if urgency_scores else 0,
            "avg_severity": round(sum(severity_scores) / len(severity_scores), 1),
            "radius_km": round(max_radius, 2),
            "categories": dict(categories),
            "top_category": max(categories, key=categories.get) if categories else "unknown",
            "members": [
                {
                    "id": m.get("id"),
                    "title": m.get("title", ""),
                    "urgency_score": m.get("urgency_score", 0),
                    "latitude": m["latitude"],
                    "longitude": m["longitude"],
                }
                for m in members
            ],
            "hotspot_level": _compute_hotspot_level(len(members), sum(urgency_scores) / max(len(urgency_scores), 1)),
        }
        clusters.append(cluster)
    
    # Sort by hotspot intensity
    clusters.sort(key=lambda c: c["avg_urgency"] * c["member_count"], reverse=True)
    
    return clusters


def dbscan_cluster(points, eps_km=2.0, min_points=2):
    """
    Density-based clustering (DBSCAN) on geographic coordinates.
    Good for finding dense need areas without specifying number of clusters.
    
    Args:
        points: list of dicts with 'latitude', 'longitude'
        eps_km: maximum distance between two points in same cluster (km)
        min_points: minimum points to form a cluster
    
    Returns:
        list of cluster dicts
    """
    n = len(points)
    labels = [-1] * n  # -1 = unvisited
    cluster_id = 0
    
    for i in range(n):
        if labels[i] != -1:
            continue
        
        # Find neighbors
        neighbors = _region_query(points, i, eps_km)
        
        if len(neighbors) < min_points:
            labels[i] = -2  # Noise
            continue
        
        # Expand cluster
        labels[i] = cluster_id
        seed_set = list(neighbors)
        j = 0
        
        while j < len(seed_set):
            q = seed_set[j]
            
            if labels[q] == -2:
                labels[q] = cluster_id
            
            if labels[q] != -1:
                j += 1
                continue
            
            labels[q] = cluster_id
            q_neighbors = _region_query(points, q, eps_km)
            
            if len(q_neighbors) >= min_points:
                for n_idx in q_neighbors:
                    if n_idx not in seed_set:
                        seed_set.append(n_idx)
            
            j += 1
        
        cluster_id += 1
    
    # Build results
    clusters_dict = defaultdict(list)
    noise = []
    
    for i, label in enumerate(labels):
        if label >= 0:
            clusters_dict[label].append(points[i])
        else:
            noise.append(points[i])
    
    clusters = []
    for cid, members in clusters_dict.items():
        avg_lat = sum(m["latitude"] for m in members) / len(members)
        avg_lon = sum(m["longitude"] for m in members) / len(members)
        urgency_scores = [m.get("urgency_score", 0) for m in members]
        
        categories = defaultdict(int)
        for m in members:
            categories[m.get("category", "unknown")] += 1
        
        clusters.append({
            "cluster_id": cid,
            "centroid": {"latitude": round(avg_lat, 6), "longitude": round(avg_lon, 6)},
            "member_count": len(members),
            "total_people_affected": sum(m.get("people_affected", 1) for m in members),
            "avg_urgency": round(sum(urgency_scores) / max(len(urgency_scores), 1), 1),
            "categories": dict(categories),
            "top_category": max(categories, key=categories.get) if categories else "unknown",
            "hotspot_level": _compute_hotspot_level(len(members), sum(urgency_scores) / max(len(urgency_scores), 1)),
        })
    
    clusters.sort(key=lambda c: c["avg_urgency"] * c["member_count"], reverse=True)
    
    return {
        "clusters": clusters,
        "noise_count": len(noise),
        "total_clusters": len(clusters),
    }


def _region_query(points, point_idx, eps_km):
    """Find all points within eps_km of point_idx."""
    neighbors = set()
    p = points[point_idx]
    
    for i, q in enumerate(points):
        if i == point_idx:
            continue
        d = haversine_km(p["latitude"], p["longitude"], q["latitude"], q["longitude"])
        if d <= eps_km:
            neighbors.add(i)
    
    return neighbors


def _compute_hotspot_level(member_count: int, avg_urgency: float) -> str:
    """Categorize hotspot intensity."""
    intensity = member_count * avg_urgency
    
    if intensity >= 300:
        return "severe"
    elif intensity >= 150:
        return "high"
    elif intensity >= 60:
        return "moderate"
    else:
        return "low"


def generate_heatmap_data(points: list[dict]) -> list[dict]:
    """
    Generate heatmap-ready data for frontend visualization.
    
    Returns list of [lat, lon, intensity] for heatmap layers.
    """
    heatmap = []
    
    for point in points:
        lat = point.get("latitude")
        lon = point.get("longitude")
        
        if lat is None or lon is None:
            continue
        
        # Intensity based on urgency and severity
        urgency = point.get("urgency_score", 50)
        severity = point.get("severity", 5) * 10
        people = min(point.get("people_affected", 1) * 5, 100)
        
        intensity = (urgency * 0.5 + severity * 0.3 + people * 0.2) / 100
        intensity = round(min(max(intensity, 0.1), 1.0), 2)
        
        heatmap.append({
            "lat": lat,
            "lng": lon,
            "intensity": intensity,
            "id": point.get("id"),
            "title": point.get("title", ""),
            "category": point.get("category", ""),
            "priority": point.get("priority_level", "medium"),
        })
    
    return heatmap
