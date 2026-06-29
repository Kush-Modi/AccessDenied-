import os
import sys
import hashlib
import json
from typing import List

# Import SentenceTransformer locally
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_client import r

class LocalEmbedder:
    MODEL_NAME = "all-MiniLM-L6-v2"
    EMBEDDING_VERSION = "1"
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LocalEmbedder, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
        # Download and cache the model locally. Will run on CPU.
        sys.stderr.write(f"Loading local embedding model '{self.MODEL_NAME}'...\n")
        sys.stderr.flush()
        self.model = SentenceTransformer(self.MODEL_NAME)
        self._initialized = True
        sys.stderr.write("Embedding model loaded successfully.\n")
        sys.stderr.flush()


    def get_embedding(self, text: str) -> List[float]:
        """
        Get the 384-dimensional vector embedding for the given text.
        Checks Redis cache first.
        """
        if not text:
            return [0.0] * 384
            
        # 1. Compute hash of the input text
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cache_key = f"embed_cache:{self.MODEL_NAME}:{self.EMBEDDING_VERSION}:{text_hash}"
        
        # 2. Check Redis cache
        try:
            cached = r.get(cache_key)
            if cached:
                # Cache hit!
                # We can record the hit by incrementing a metrics key later in the metrics class
                r.incr("metrics:embed:cache_hits")
                return json.loads(cached)
        except Exception as cache_err:
            # If Redis connection fails, bypass cache and log warning
            pass
            
        # 3. Generate embedding using model
        # Record miss
        try:
            r.incr("metrics:embed:cache_misses")
        except Exception:
            pass
            
        vector = self.model.encode(text).tolist()
        
        # 4. Cache vector in Redis
        try:
            r.setex(cache_key, 86400 * 7, json.dumps(vector)) # Cache for 7 days
        except Exception:
            pass
            
        return vector

embedder = LocalEmbedder()
