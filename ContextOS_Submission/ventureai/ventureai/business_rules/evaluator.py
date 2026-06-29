from typing import Dict, Any, List

class RuleEvaluator:
    @staticmethod
    def evaluate(condition: str, context: Dict[str, Any]) -> bool:
        """
        Safely evaluates a declarative rule condition against the context dictionary.
        Bypasses unsafe eval() to prevent security issues.
        """
        condition = condition.strip()
        
        # 1. Direct key lookups in context
        if condition in context:
            return bool(context[condition])
            
        # 2. Support client_health < 40 comparison
        if condition.startswith("client_health"):
            health = context.get("client_health", 100)
            # Parse threshold, e.g. "client_health < 40"
            parts = condition.split()
            if len(parts) == 3 and parts[1] == "<":
                try:
                    threshold = float(parts[2])
                    return health < threshold
                except ValueError:
                    pass
            elif len(parts) == 3 and parts[1] == ">":
                try:
                    threshold = float(parts[2])
                    return health > threshold
                except ValueError:
                    pass
                    
        return False
        
    @staticmethod
    def build_context(
        candidate: Dict[str, Any],
        client: Dict[str, Any],
        job: Dict[str, Any],
        extra: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Helper to assemble candidate, client, and job details into a flat context map."""
        extra = extra or {}
        
        # Calculate skills overlap
        cand_skills = set([s.lower() for s in candidate.get("skills", [])])
        req_skills = set([s.lower() for s in job.get("required_skills", [])])
        missing_skills = list(req_skills - cand_skills)
        
        # Calculate Notice period
        notice_days = candidate.get("notice_days", 0)
        if not notice_days and "notice" in str(candidate.get("resume_text", "")).lower():
            # If notice period is mentioned in resume text but not explicit, try to infer or fallback
            notice_days = 0
            
        # Check Salary mismatch
        salary_mismatch = False
        cand_sal = candidate.get("expected_salary")
        job_sal_range = job.get("salary_range", "")
        # Parse job max salary (e.g. "25-35 LPA")
        job_max_salary = None
        if job_sal_range and "-" in job_sal_range:
            try:
                # Extract max number, e.g. 35
                max_str = job_sal_range.split("-")[1].split()[0]
                # Clean non-digits
                max_str = "".join([c for c in max_str if c.isdigit()])
                if max_str:
                    job_max_salary = float(max_str) * 100000  # Convert LPA to absolute number
            except:
                pass
        
        if cand_sal and job_max_salary and cand_sal > job_max_salary:
            salary_mismatch = True
            
        # Check Location mismatch
        location_mismatch = False
        cand_loc = candidate.get("location", "").lower().strip()
        job_loc = job.get("location", "").lower().strip()
        if cand_loc and job_loc and cand_loc != job_loc and "remote" not in job_loc:
            location_mismatch = True
            
        # Client priority & freeze
        hiring_freeze = client.get("hiring_freeze", False)
        if not hiring_freeze:
            # Check description or updates
            hiring_freeze = "freeze" in str(job.get("description_text", "")).lower()
            
        high_priority = False
        client_health = client.get("account_health", 100)
        if client_health > 80:
            high_priority = True
            
        context = {
            "client_health": client_health,
            "candidate_rejected_recently": extra.get("candidate_rejected_recently", False),
            "candidate_already_submitted": extra.get("candidate_already_submitted", False),
            "hiring_freeze": hiring_freeze,
            "high_priority_client": high_priority,
            "candidate_notice_period_long": notice_days > 60 or extra.get("notice_days", 0) > 60,
            "candidate_unavailable": candidate.get("status") == "placed" or extra.get("unavailable", False),
            "urgent_hiring": "critical" in str(job.get("description_text", "")).lower() or "urgent" in str(job.get("description_text", "")).lower(),
            "duplicate_recommendation": extra.get("duplicate_recommendation", False),
            "salary_mismatch": salary_mismatch,
            "location_mismatch": location_mismatch,
            "missing_mandatory_skills": len(missing_skills) > 0,
            "missing_skills_list": missing_skills,
        }
        
        # Merge direct key-values from extra
        for k, v in extra.items():
            if k not in context:
                context[k] = v
                
        return context
