# Job Priority Classifier

def calculate_job_priority(
    client_health: int,
    urgency_level: str, # high, medium, low
    job_age_days: int,
    recruiter_activity_count: int
) -> str:
    """
    Calculate and return a priority label: Critical, High, Medium, Low.
    """
    score = 0
    
    # 1. Urgency Level
    if urgency_level.lower() == "high":
        score += 35
    elif urgency_level.lower() == "medium":
        score += 20
    else:
        score += 5
        
    # 2. Job Age (Freshness needs momentum, old roles might be stalled)
    if job_age_days <= 14:
        score += 25
    elif job_age_days <= 45:
        score += 15
    else:
        score += 5
        
    # 3. Client Health (Low health = risk = action needed; High health = key account = keep happy)
    if client_health < 40:
        score += 20  # Risk retention priority
    elif client_health >= 80:
        score += 15  # High-value VIP priority
    else:
        score += 5
        
    # 4. Recruiter Activity (Low activity means it needs a kickstart)
    if recruiter_activity_count <= 2:
        score += 20
    elif recruiter_activity_count <= 5:
        score += 10
    else:
        score += 5
        
    # Assign label based on score
    if score >= 75:
        return "Critical"
    elif score >= 55:
        return "High"
    elif score >= 30:
        return "Medium"
    else:
        return "Low"
