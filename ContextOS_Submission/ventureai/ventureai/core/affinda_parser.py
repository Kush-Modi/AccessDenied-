import os
from affinda import AffindaAPI, TokenCredential

def get_affinda_client():
    api_key = os.getenv("AFFINDA_API_KEY")
    if not api_key:
        return None
    credential = TokenCredential(token=api_key)
    return AffindaAPI(credential=credential)

def parse_resume_file(file_content: bytes, filename: str) -> dict:
    client = get_affinda_client()
    if not client:
        raise ValueError("AFFINDA_API_KEY is not configured in .env file.")
        
    workspace_id = os.getenv("AFFINDA_WORKSPACE_ID")
    if not workspace_id:
        raise ValueError("AFFINDA_WORKSPACE_ID is not configured in .env file.")
        
    # Upload document (passing bytes directly)
    # Affinda API create_document accepts file-like object or bytes
    # To pass as file object, we wrap in BytesIO
    import io
    file_obj = io.BytesIO(file_content)
    file_obj.name = filename
    
    # Run creation
    doc = client.create_document(
        file=file_obj,
        workspace=workspace_id
    )
    
    return extract_resume_data(doc)

def _safe_str(val) -> str:
    if not val:
        return ""
    if isinstance(val, dict):
        inner_val = val.get("value") or val.get("raw") or val.get("raw_text") or val.get("rawText") or val.get("formatted") or ""
        return _safe_str(inner_val)
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        if val:
            return _safe_str(val[0])
        return ""
    # If it's an SDK object, try attributes
    for attr in ["value", "raw", "raw_text", "rawText", "formatted"]:
        if hasattr(val, attr):
            attr_val = getattr(val, attr)
            if attr_val:
                return _safe_str(attr_val)
    return str(val)

def _safe_float(val) -> float:
    if not val:
        return 0.0
    if isinstance(val, dict):
        inner_val = val.get("value") or val.get("parsed") or val.get("raw") or val.get("raw_text") or val.get("rawText")
        return _safe_float(inner_val)
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val)
        except Exception:
            import re
            m = re.search(r"[-+]?\d*\.\d+|\d+", val)
            if m:
                return float(m.group(0))
    # If it is an SDK object, try attributes
    for attr in ["value", "parsed", "raw", "raw_text", "rawText"]:
        if hasattr(val, attr):
            attr_val = getattr(val, attr)
            if attr_val is not None:
                return _safe_float(attr_val)
    return 0.0

def _extract_rects(val) -> list:
    rects = []
    if not val:
        return rects
    # If it is a dictionary
    if isinstance(val, dict):
        if "rectangle" in val and val["rectangle"]:
            rects.append(val["rectangle"])
        elif "rectangles" in val and val["rectangles"]:
            rects.extend(val["rectangles"])
        for k, v in val.items():
            if k not in ["rectangle", "rectangles"]:
                rects.extend(_extract_rects(v))
    # If it is a list
    elif isinstance(val, list):
        for item in val:
            rects.extend(_extract_rects(item))
    # If it is an SDK object, try attributes
    else:
        for attr in ["rectangle", "rectangles"]:
            if hasattr(val, attr):
                r = getattr(val, attr)
                if r:
                    if isinstance(r, list):
                        rects.extend(r)
                    else:
                        rects.append(r)
        try:
            d = val.__dict__
            for k, v in d.items():
                if k not in ["rectangle", "rectangles"]:
                    rects.extend(_extract_rects(v))
        except Exception:
            pass
    return rects

def _norm_rect(rect) -> dict:
    if not rect:
        return None
    if isinstance(rect, dict):
        return {
            "x0": rect.get("x0") or rect.get("xMin") or rect.get("left") or 0.0,
            "y0": rect.get("y0") or rect.get("yMin") or rect.get("top") or 0.0,
            "x1": rect.get("x1") or rect.get("xMax") or rect.get("right") or 0.0,
            "y1": rect.get("y1") or rect.get("yMax") or rect.get("bottom") or 0.0,
            "pageIndex": rect.get("page_index") or rect.get("pageIndex") or 0
        }
    res = {}
    for attr, keys in [("x0", ["x0", "xMin", "left"]), ("y0", ["y0", "yMin", "top"]), 
                       ("x1", ["x1", "xMax", "right"]), ("y1", ["y1", "yMax", "bottom"]), 
                       ("pageIndex", ["page_index", "pageIndex"])]:
        val = 0.0
        for k in keys:
            if hasattr(rect, k):
                val = getattr(rect, k)
                break
        res[attr] = val
    return res

def extract_resume_data(doc) -> dict:
    data = {}
    if hasattr(doc, "data"):
        data_obj = doc.data
        if hasattr(data_obj, "as_dict"):
            data = data_obj.as_dict()
        elif isinstance(data_obj, dict):
            data = data_obj
        else:
            try:
                data = doc.data.__dict__
            except Exception:
                data = {}
    elif hasattr(doc, "as_dict"):
        data = doc.as_dict()
    elif isinstance(doc, dict):
        data = doc

    # Safe extraction helpers
    name_obj = data.get("candidate_name") or data.get("candidateName") or {}
    first_name = _safe_str(name_obj.get("first_name") or name_obj.get("firstName") or "")
    last_name = _safe_str(name_obj.get("family_name") or name_obj.get("familyName") or name_obj.get("lastName") or "")
    name = _safe_str(name_obj.get("formatted")) or f"{first_name} {last_name}".strip()
    if not name:
        name = "Unknown Candidate"

    emails = data.get("emails") or data.get("email") or []
    email = _safe_str(emails)

    phones = data.get("phone_numbers") or data.get("phoneNumber") or data.get("phone") or []
    phone = _safe_str(phones)

    loc_obj = data.get("location") or {}
    location = _safe_str(loc_obj)
    if not location:
        location = "Remote"

    summary = _safe_str(data.get("summary") or "")
    exp_years = data.get("total_years_experience") or data.get("totalYearsExperience") or 0

    # Skills parsing
    skills_raw = data.get("skills") or data.get("skill") or []
    skills = []
    if isinstance(skills_raw, list):
        for s in skills_raw:
            s_name = ""
            if isinstance(s, dict):
                s_name = s.get("name") or s.get("value") or ""
            elif isinstance(s, str):
                s_name = s
            elif hasattr(s, "name"):
                s_name = s.name
            s_name = _safe_str(s_name)
            if s_name:
                skills.append(s_name)
    skills = [s for s in skills if s]

    # Education parsing
    edu_raw = data.get("education") or []
    education = []
    if isinstance(edu_raw, list):
        for e in edu_raw:
            if isinstance(e, dict):
                org = _safe_str(e.get("organization") or e.get("education_organization") or e.get("educationOrganization") or "")
                deg = _safe_str(e.get("degree") or e.get("education_degree") or e.get("educationDegree") or "")
                lvl = _safe_str(e.get("level") or e.get("education_level") or e.get("educationLevel") or "")
                maj = _safe_str(e.get("major") or e.get("education_major") or e.get("educationMajor") or "")
                
                # Check for grade
                gpa_obj = e.get("grade") or e.get("education_grade") or e.get("educationGrade") or {}
                gpa = _safe_str(gpa_obj)
                    
                dates_obj = e.get("dates") or {}
                start = _safe_str(dates_obj.get("start") if isinstance(dates_obj, dict) else "")
                end = _safe_str(dates_obj.get("end") if isinstance(dates_obj, dict) else "")
                dates = f"{start} - {end}" if start or end else ""
                education.append({
                    "organization": org,
                    "degree": deg,
                    "level": lvl,
                    "major": maj,
                    "gpa": gpa,
                    "dates": dates
                })

    # Work experience parsing
    work_raw = data.get("work_experience") or data.get("workExperience") or []
    work_experience = []
    if isinstance(work_raw, list):
        for w in work_raw:
            if isinstance(w, dict):
                org = _safe_str(w.get("organization") or w.get("work_experience_organization") or w.get("workExperienceOrganization") or "")
                title = _safe_str(w.get("job_title") or w.get("jobTitle") or w.get("work_experience_job_title") or w.get("workExperienceJobTitle") or "")
                dates_obj = w.get("dates") or {}
                start = _safe_str(dates_obj.get("start") if isinstance(dates_obj, dict) else "")
                end = _safe_str(dates_obj.get("end") if isinstance(dates_obj, dict) else "")
                dates = f"{start} - {end}" if start or end else ""
                desc = _safe_str(w.get("job_description") or w.get("jobDescription") or w.get("work_experience_job_description") or w.get("workExperienceJobDescription") or "")
                work_experience.append({
                    "organization": org,
                    "job_title": title,
                    "dates": dates,
                    "description": desc
                })

    # Projects parsing
    proj_raw = data.get("projects") or data.get("project") or []
    projects = []
    if isinstance(proj_raw, list):
        for p in proj_raw:
            if isinstance(p, dict):
                projects.append({
                    "title": _safe_str(p.get("title") or p.get("project_title") or p.get("projectTitle") or ""),
                    "description": _safe_str(p.get("description") or p.get("project_description") or p.get("projectDescription") or "")
                })

    # Achievements parsing
    ach_raw = data.get("achievements") or data.get("achievement") or []
    achievements = []
    if isinstance(ach_raw, list):
        for a in ach_raw:
            ach = _safe_str(a)
            if ach:
                achievements.append(ach)

    current_position = ""
    if work_experience:
        current_position = work_experience[0].get("job_title") or ""
    if not current_position:
        current_position = "Software Engineer"

    # Extract all coordinates
    coordinates = {
        "name": [_norm_rect(r) for r in _extract_rects(data.get("candidate_name") or data.get("candidateName")) if r][:1],
        "email": [_norm_rect(r) for r in _extract_rects(data.get("emails") or data.get("email")) if r][:1],
        "phone": [_norm_rect(r) for r in _extract_rects(data.get("phone_numbers") or data.get("phoneNumber") or data.get("phone")) if r][:1],
        "location": [_norm_rect(r) for r in _extract_rects(data.get("location")) if r][:1],
        "experience": [_norm_rect(r) for r in _extract_rects(data.get("total_years_experience") or data.get("totalYearsExperience")) if r][:1],
        "skills": [_norm_rect(r) for r in _extract_rects(data.get("skills") or data.get("skill")) if r][:4],
        "education": [_norm_rect(r) for r in _extract_rects(data.get("education")) if r][:2],
        "work_experience": [_norm_rect(r) for r in _extract_rects(data.get("work_experience") or data.get("workExperience")) if r][:3]
    }

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "skills": skills,
        "experience_years": int(_safe_float(exp_years)),
        "current_position": current_position,
        "summary": summary,
        "education": education,
        "work_experience": work_experience,
        "projects": projects,
        "achievements": achievements,
        "coordinates": coordinates
    }
