import os
import json
import redis
import sys
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis_available = None  # None: not yet checked, True: running, False: failed/local fallback
_local_cache = {}
_local_logs = {}
r = None

def get_redis_client():
    global _redis_available, r
    if _redis_available is None:
        try:
            r = redis.from_url(REDIS_URL, decode_responses=True, protocol=2, socket_timeout=1.0)
            r.ping()
            try:
                r.config_set("stop-writes-on-bgsave-error", "no")
            except Exception:
                pass
            _redis_available = True
        except Exception as err:
            _redis_available = False
            sys.stderr.write(f"Warning: Redis is unavailable at {REDIS_URL}: {err}. Falling back to local in-memory store.\n")
            r = None
    return r if _redis_available else None

def cache_get(key: str):
    client = get_redis_client()
    if client:
        try:
            val = client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            sys.stderr.write(f"Redis get error: {e}\n")
    return _local_cache.get(key)

def cache_set(key: str, value, ttl: int = 300):
    client = get_redis_client()
    if client:
        try:
            client.setex(key, ttl, json.dumps(value))
            return
        except Exception as e:
            sys.stderr.write(f"Redis set error: {e}\n")
    _local_cache[key] = value

def cache_delete(key: str):
    client = get_redis_client()
    if client:
        try:
            client.delete(key)
            return
        except Exception as e:
            sys.stderr.write(f"Redis delete error: {e}\n")
    if key in _local_cache:
        del _local_cache[key]

# HITL session bridge
def set_hitl_pending(session_id: str, payload: dict, ttl: int = 600):
    cache_set(f"hitl:{session_id}", payload, ttl)

def get_hitl_pending(session_id: str):
    return cache_get(f"hitl:{session_id}")

def resolve_hitl(session_id: str, decision: str):
    cache_set(f"hitl:{session_id}:decision", decision, 300)

def get_hitl_decision(session_id: str):
    val = cache_get(f"hitl:{session_id}:decision")
    # If returned from local cache directly (not json serialized), it might be raw string
    return val

def log_session(session_id: str, message: str):
    """Log a message for a specific session to Redis or local memory."""
    client = get_redis_client()
    if client:
        try:
            client.rpush(f"logs:{session_id}", message)
            client.expire(f"logs:{session_id}", 600)
            return
        except Exception as e:
            sys.stderr.write(f"Redis log error: {e}\n")
            
    if session_id not in _local_logs:
        _local_logs[session_id] = []
    _local_logs[session_id].append(message)

def get_session_logs(session_id: str):
    """Retrieve all logged messages for a session."""
    client = get_redis_client()
    if client:
        try:
            return client.lrange(f"logs:{session_id}", 0, -1)
        except Exception as e:
            sys.stderr.write(f"Redis get logs error: {e}\n")
    return _local_logs.get(session_id, [])