# Client Health Score Calculator

def calculate_client_health(
    last_contact_days: int,
    open_positions_count: int,
    placement_success_rate: float,
    recruiter_activity_count: int,
    recent_meetings_count: int
) -> int:
    """
    Calculate a client's health score between 0 and 100.
    
    Factors:
    - Last Contact Days (Max 20 pts)
    - Open Positions Count (Max 20 pts)
    - Placement Success Rate (Max 30 pts)
    - Recruiter Activity Count (Max 10 pts)
    - Recent Meetings Count (Max 20 pts)
    """
    score = 0
    
    # 1. Last Contact Days
    if last_contact_days <= 7:
        score += 20
    elif last_contact_days <= 14:
        score += 15
    elif last_contact_days <= 30:
        score += 10
    elif last_contact_days <= 60:
        score += 5
        
    # 2. Open Positions Count
    if open_positions_count > 5:
        score += 20
    elif open_positions_count >= 3:
        score += 15
    elif open_positions_count >= 1:
        score += 10
    else:
        score += 5
        
    # 3. Placement Success Rate (0.0 to 1.0)
    score += int(placement_success_rate * 30)
    
    # 4. Recruiter Activity Count
    if recruiter_activity_count >= 10:
        score += 10
    elif recruiter_activity_count >= 5:
        score += 7
    elif recruiter_activity_count >= 2:
        score += 4
        
    # 5. Recent Meetings Count
    if recent_meetings_count >= 3:
        score += 20
    elif recent_meetings_count >= 1:
        score += 15
        
    # Clamp between 0 and 100
    return max(0, min(100, score))
