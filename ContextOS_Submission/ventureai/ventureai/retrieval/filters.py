import os
import sys
import yaml
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_ranking_config() -> Dict[str, Any]:
    """Helper to load config from ranking_config.yaml."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "ranking_config.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to load config/ranking_config.yaml: {e}\n")
            sys.stderr.flush()

    return {}

def filter_by_metadata(items: List[Dict[str, Any]], candidate_id: str = None, client_id: str = None) -> List[Dict[str, Any]]:
    """
    Filter items by candidate_id and client_id if specified.
    """
    filtered = []
    for item in items:
        # Check candidate_id match
        if candidate_id:
            # We can check item["entity_id"] if entity_type is candidate
            # Or we can check in item["metadata"]
            entity_type = item.get("entity_type")
            entity_id = item.get("entity_id")
            meta = item.get("metadata") or {}
            meta_cand = meta.get("candidate_id") or meta.get("candidate")
            
            cand_match = (entity_type == "candidate" and entity_id == candidate_id) or (str(meta_cand) == str(candidate_id))
            if not cand_match:
                continue
                
        # Check client_id match
        if client_id:
            entity_type = item.get("entity_type")
            entity_id = item.get("entity_id")
            meta = item.get("metadata") or {}
            meta_client = meta.get("client_id") or meta.get("client")
            
            client_match = (entity_type == "client" and entity_id == client_id) or (str(meta_client) == str(client_id))
            if not client_match:
                continue
                
        filtered.append(item)
    return filtered

def filter_by_similarity(items: List[Dict[str, Any]], custom_threshold: float = None) -> List[Dict[str, Any]]:
    """
    Filter items based on similarity threshold defined in config/ranking_config.yaml or passed custom_threshold.
    """
    config = load_ranking_config()
    threshold = custom_threshold
    if threshold is None:
        threshold = config.get("retrieval", {}).get("similarity_threshold", 0.75)
        
    filtered = []
    for item in items:
        sim = item.get("similarity", 0.0)
        if sim >= threshold:
            filtered.append(item)
    return filtered
