import sys
import os
import psycopg2
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def run_migrations():
    db_pass = os.getenv("SUPABASE_DB_PASSWORD")
    if not db_pass:
        print("Error: SUPABASE_DB_PASSWORD not found in environment.")
        sys.exit(1)
        
    host = "db.njhxlkevnoizxqiekrrz.supabase.co"
    port = 5432
    user = "postgres"
    dbname = "postgres"
    
    print(f"Connecting to database at {host}:{port} to run memory tables migration...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=db_pass,
            database=dbname,
            sslmode="require"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Creating table planner_feedback if it does not exist...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS planner_feedback (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            recommendation_id VARCHAR(255),
            candidate_id VARCHAR(255) NOT NULL,
            client_id VARCHAR(255) NOT NULL,
            job_id VARCHAR(255) NOT NULL,
            recruiter_decision VARCHAR(50) NOT NULL, -- 'approved', 'rejected', 'modified', 'ignored', 'expired', 'cancelled'
            decision_reason TEXT,
            outcome VARCHAR(50) DEFAULT 'pending', -- 'success', 'failure', 'pending'
            placement_success BOOLEAN DEFAULT FALSE,
            placement_failure BOOLEAN DEFAULT FALSE,
            feedback_notes TEXT,
            historical_confidence FLOAT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        cursor.execute(create_table_sql)
        
        print("Reloading Postgrest schema cache...")
        cursor.execute("NOTIFY pgrst, 'reload schema';")
        
        print("Memory table migration completed successfully!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Memory table migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
