import sys
import os
# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase

def test_supabase_connection():
    print("--- Testing Supabase Connection & Tables ---")
    
    tables = ["candidates", "clients", "job_descriptions", "placements", "recruiter_actions"]
    
    for table in tables:
        try:
            res = supabase.table(table).select("*").limit(1).execute()
            print(f"Table '{table}' query: PASSED (Found {len(res.data)} sample record(s))")
        except Exception as e:
            print(f"Table '{table}' query: FAILED with error: {e}")

if __name__ == "__main__":
    test_supabase_connection()
