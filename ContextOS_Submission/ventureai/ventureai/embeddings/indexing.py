import sys
import os
from datetime import datetime, timezone
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase
from embeddings.embedder import embedder

def build_indexing_text(item: dict) -> str:
    """Build the raw string for vector embedding from a knowledge item."""
    parts = []
    if item.get("type"):
        parts.append(f"Type: {item['type']}")
    if item.get("title"):
        parts.append(f"Title: {item['title']}")
    if item.get("summary"):
        parts.append(f"Summary: {item['summary']}")
    if item.get("content"):
        parts.append(f"Content: {item['content']}")
    return " | ".join(parts)

def run_indexing(batch_size: int = 50) -> int:
    """
    Scans knowledge_items table for stale or unindexed items,
    generates embeddings in batches, and upserts them.
    Returns the count of indexed items.
    """
    print("Checking for unindexed or stale knowledge items in Supabase...")
    
    # 1. Query items where embedded_at is null OR embedded_at < updated_at
    # Since Supabase Postgrest client does not support advanced OR queries with comparisons easily,
    # we can fetch all records (since our seed is small) and filter in Python, OR we can fetch
    # records where embedded_at is null.
    # To be extremely robust, let's fetch all records with id, updated_at, and embedded_at,
    # find which ones need embedding, and then fetch their details to embed them.
    try:
        res = supabase.table("knowledge_items").select("id, updated_at, embedded_at").execute()
        all_items = res.data or []
    except Exception as e:
        print(f"Error fetching knowledge_items metadata: {e}")
        return 0
        
    to_index_ids = []
    for item in all_items:
        embedded_at = item.get("embedded_at")
        updated_at = item.get("updated_at")
        
        # Determine if it needs reindexing
        needs_reindex = False
        if not embedded_at:
            needs_reindex = True
        elif updated_at:
            # Parse ISO timestamps
            try:
                emb_dt = datetime.fromisoformat(embedded_at.replace("Z", "+00:00"))
                upd_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                if emb_dt < upd_dt:
                    needs_reindex = True
            except Exception:
                needs_reindex = True
                
        if needs_reindex:
            to_index_ids.append(item["id"])
            
    if not to_index_ids:
        print("No items need indexing. System is fully up-to-date!")
        return 0
        
    print(f"Found {len(to_index_ids)} items that need indexing. Processing in batches...")
    
    indexed_count = 0
    # Process in batches
    for i in range(0, len(to_index_ids), batch_size):
        batch_ids = to_index_ids[i:i+batch_size]
        try:
            # Fetch full text details of the batch
            batch_res = supabase.table("knowledge_items").select("*").in_("id", batch_ids).execute()
            items = batch_res.data or []
            
            for item in items:
                start_time = time.time()
                text = build_indexing_text(item)
                vector = embedder.get_embedding(text)
                
                # Update item in Supabase
                update_payload = {
                    "embedding": vector,
                    "embedding_model": embedder.MODEL_NAME,
                    "embedding_version": embedder.EMBEDDING_VERSION,
                    "embedded_at": datetime.now(timezone.utc).isoformat()
                }
                
                supabase.table("knowledge_items").update(update_payload).eq("id", item["id"]).execute()
                indexed_count += 1
                
                # Log indexing latency to Redis metrics
                latency = time.time() - start_time
                try:
                    from redis_client import r
                    r.lpush("metrics:embed:latencies", json.dumps(latency))
                    r.ltrim("metrics:embed:latencies", 0, 99) # Keep last 100 values
                except Exception:
                    pass
                    
            print(f"Successfully indexed batch: {len(items)} items.")
        except Exception as batch_err:
            print(f"Error indexing batch starting at index {i}: {batch_err}")
            
    print(f"Indexing completed. Total records processed: {indexed_count}")
    return indexed_count

if __name__ == "__main__":
    run_indexing()
