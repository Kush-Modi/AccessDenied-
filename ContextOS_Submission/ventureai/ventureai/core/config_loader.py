import os
import yaml
import sys
from typing import Dict, Any

class ConfigLoader:
    _config = None
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        if cls._config is not None:
            return cls._config
            
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "ranking_config.yaml"
        )
        
        default_config = {
            "cache": {"ttl_seconds": 300, "hitl_ttl_seconds": 600},
            "retrieval": {"top_k": 5, "similarity_threshold": 0.75},
            "weights": {
                "semantic_similarity": 0.40,
                "business_signals": 0.20,
                "client_health": 0.15,
                "placement_history": 0.10,
                "recency": 0.10,
                "importance": 0.05
            },
            "decision_weights": {
                "candidate_fit": 0.35,
                "knowledge_rag": 0.25,
                "planner_memory": 0.20,
                "client_health": 0.10,
                "priority_urgency": 0.10
            }
        }
        
        if not os.path.exists(file_path):
            cls._config = default_config
            return cls._config
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
            if loaded:
                for k, v in loaded.items():
                    if k in default_config and isinstance(v, dict):
                        default_config[k].update(v)
                    else:
                        default_config[k] = v
            cls._config = default_config
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to load config file: {e}. Using defaults.\n")
            cls._config = default_config
            
        return cls._config
