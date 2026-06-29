import os
import sys
import json
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_client import r

class RetrievalMetrics:
    @staticmethod
    def record_latencies(embed_sec: float, retrieve_sec: float, rerank_sec: float):
        try:
            r.hset("metrics:retrieval", "last_embedding_latency", embed_sec)
            r.hset("metrics:retrieval", "last_retrieval_latency", retrieve_sec)
            r.hset("metrics:retrieval", "last_rerank_latency", rerank_sec)
        except Exception:
            pass

    @staticmethod
    def record_averages(similarity: float, confidence: float):
        try:
            r.hset("metrics:retrieval", "last_average_similarity", similarity)
            r.hset("metrics:retrieval", "last_average_confidence", confidence)
        except Exception:
            pass

    @staticmethod
    def record_counts(retrieved: int, filtered: int, reranked: int):
        try:
            r.hset("metrics:retrieval", "last_retrieved_count", retrieved)
            r.hset("metrics:retrieval", "last_filtered_count", filtered)
            r.hset("metrics:retrieval", "last_reranked_count", reranked)
            
            # Increment running totals
            r.hincrby("metrics:retrieval", "total_retrieved", retrieved)
            r.hincrby("metrics:retrieval", "total_filtered", filtered)
            r.hincrby("metrics:retrieval", "total_reranked", reranked)
            r.hincrby("metrics:retrieval", "total_queries", 1)
        except Exception:
            pass

    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        try:
            raw = r.hgetall("metrics:retrieval")
            # Decode bytes keys and values
            metrics = {}
            for k, v in raw.items():
                key_str = k.decode("utf-8") if isinstance(k, bytes) else str(k)
                val_str = v.decode("utf-8") if isinstance(v, bytes) else str(v)
                try:
                    if "." in val_str:
                        metrics[key_str] = float(val_str)
                    else:
                        metrics[key_str] = int(val_str)
                except ValueError:
                    metrics[key_str] = val_str
                    
            # Check cache hits/misses
            cache_hits = r.get("metrics:embed:cache_hits")
            cache_misses = r.get("metrics:embed:cache_misses")
            
            hits = int(cache_hits) if cache_hits else 0
            misses = int(cache_misses) if cache_misses else 0
            total = hits + misses
            metrics["cache_hit_rate"] = (hits / total) if total > 0 else 0.0
            metrics["cache_hits"] = hits
            metrics["cache_misses"] = misses
            
            # Default values if keys don't exist
            defaults = {
                "last_embedding_latency": 0.0,
                "last_retrieval_latency": 0.0,
                "last_rerank_latency": 0.0,
                "last_average_similarity": 0.0,
                "last_average_confidence": 0.0,
                "last_retrieved_count": 0,
                "last_filtered_count": 0,
                "last_reranked_count": 0,
                "total_queries": 0
            }
            for k, val in defaults.items():
                if k not in metrics:
                    metrics[k] = val
            return metrics
        except Exception as e:
            return {"error": f"Failed to retrieve metrics: {e}"}

    @staticmethod
    def reset_metrics():
        try:
            r.delete("metrics:retrieval")
            r.delete("metrics:embed:cache_hits")
            r.delete("metrics:embed:cache_misses")
        except Exception:
            pass
