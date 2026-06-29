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
    
    print(f"Connecting to database at {host}:{port}...")
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
        
        # 1. Enable extension
        print("Enabling pgvector extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # 2. Add columns to knowledge_items
        print("Altering table knowledge_items to add embedding columns...")
        alter_statements = [
            "ALTER TABLE knowledge_items ADD COLUMN IF NOT EXISTS embedding vector(384);",
            "ALTER TABLE knowledge_items ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(255);",
            "ALTER TABLE knowledge_items ADD COLUMN IF NOT EXISTS embedding_version VARCHAR(50);",
            "ALTER TABLE knowledge_items ADD COLUMN IF NOT EXISTS embedded_at TIMESTAMPTZ;",
            "ALTER TABLE knowledge_items ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();"
        ]
        for stmt in alter_statements:
            try:
                cursor.execute(stmt)
            except Exception as col_err:
                print(f"Column warning: {col_err}")
                
        # 3. Create RPC search function
        print("Creating PostgreSQL RPC function match_knowledge_items...")
        rpc_sql = """
        CREATE OR REPLACE FUNCTION match_knowledge_items (
          query_embedding vector(384),
          match_threshold float,
          match_count int,
          filter_entity_type varchar DEFAULT NULL,
          filter_entity_id varchar DEFAULT NULL
        )
        RETURNS TABLE (
          id uuid,
          type varchar,
          source varchar,
          entity_type varchar,
          entity_id varchar,
          title varchar,
          summary text,
          content text,
          metadata jsonb,
          created_at timestamptz,
          updated_at timestamptz,
          embedding_model varchar,
          embedding_version varchar,
          embedded_at timestamptz,
          similarity float
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RETURN QUERY
          SELECT
            ki.id,
            ki.type,
            ki.source,
            ki.entity_type,
            ki.entity_id,
            ki.title,
            ki.summary,
            ki.content,
            ki.metadata,
            ki.created_at,
            ki.updated_at,
            ki.embedding_model,
            ki.embedding_version,
            ki.embedded_at,
            (1 - (ki.embedding <=> query_embedding))::float AS similarity
          FROM knowledge_items ki
          WHERE ki.embedding IS NOT NULL
            AND (1 - (ki.embedding <=> query_embedding)) > match_threshold
            AND (filter_entity_type IS NULL OR ki.entity_type = filter_entity_type)
            AND (filter_entity_id IS NULL OR ki.entity_id = filter_entity_id)
          ORDER BY similarity DESC
          LIMIT match_count;
        END;
        $$;
        """
        cursor.execute(rpc_sql)
        
        # 4. Reload Postgrest schema cache so Supabase API sees the new function and columns
        print("Reloading Postgrest schema cache...")
        cursor.execute("NOTIFY pgrst, 'reload schema';")
        
        print("Migrations successfully completed!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
