import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase

try:
    c_res = supabase.table("clients").select("*").limit(1).execute()
    if c_res.data:
        print("Clients Table Columns:", list(c_res.data[0].keys()))
        print("Clients Sample:", c_res.data[0])
    
    j_res = supabase.table("job_descriptions").select("*").limit(1).execute()
    if j_res.data:
        print("\nJob Descriptions Table Columns:", list(j_res.data[0].keys()))
        print("Job Descriptions Sample:", j_res.data[0])
except Exception as e:
    import traceback
    traceback.print_exc()
