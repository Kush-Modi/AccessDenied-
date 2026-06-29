import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from embeddings.indexing import run_indexing

def trigger_reindex(batch_size: int = 50) -> int:
    """
    Trigger incremental re-indexing of knowledge items.
    Can be called inside ingestion/migration workflows.
    """
    try:
        return run_indexing(batch_size=batch_size)
    except Exception as e:
        print(f"Failed to trigger re-index: {e}")
        return 0

if __name__ == "__main__":
    trigger_reindex()
