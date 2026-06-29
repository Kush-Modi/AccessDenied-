# Recruiter scenarios dictionary

SCENARIOS = [
    "Urgent Hiring",
    "Client At Risk",
    "Candidate Ghosting",
    "Counter Offer",
    "Salary Negotiation",
    "Multiple Offers",
    "Interview Delay",
    "Hiring Freeze",
    "Position Closed",
    "Offer Accepted",
    "Offer Declined"
]

def get_scenario_metadata(scenario_name: str):
    """Return scenario properties like default sentiment or description."""
    descriptions = {
        "Urgent Hiring": "High urgency fill request from the client.",
        "Client At Risk": "Client relationship threatened by pipeline delays.",
        "Candidate Ghosting": "Candidate ceased all communication mid-process.",
        "Counter Offer": "Candidate received counter-offer from current company.",
        "Salary Negotiation": "Candidate and client negotiating compensation terms.",
        "Multiple Offers": "Candidate holds active competing offers.",
        "Interview Delay": "Client-side delays in scheduling/feedback.",
        "Hiring Freeze": "Corporate freeze halted active hiring pipeline.",
        "Position Closed": "Requisition filled internally or cancelled by client.",
        "Offer Accepted": "Candidate accepted client's formal offer.",
        "Offer Declined": "Candidate declined client's formal offer."
    }
    return {
        "name": scenario_name,
        "description": descriptions.get(scenario_name, "Standard recruitment scenario."),
        "sentiment": "negative" if scenario_name in ["Client At Risk", "Candidate Ghosting", "Hiring Freeze", "Offer Declined"] else "positive" if scenario_name in ["Offer Accepted"] else "neutral"
    }
