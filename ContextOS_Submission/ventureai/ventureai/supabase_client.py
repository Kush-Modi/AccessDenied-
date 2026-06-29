import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

class MockTableBuilder:
    def __init__(self, table_name):
        self.name = table_name
    def select(self, *args, **kwargs): return self
    def insert(self, *args, **kwargs): return self
    def update(self, *args, **kwargs): return self
    def delete(self, *args, **kwargs): return self
    def eq(self, *args, **kwargs): return self
    def limit(self, *args, **kwargs): return self
    def execute(self, *args, **kwargs):
        class MockResult:
            data = []
        return MockResult()

class ResilientSupabaseProxy:
    def __init__(self, client):
        self._client = client
        
    def table(self, name):
        if not self._client:
            return MockTableBuilder(name)
        try:
            return self._client.table(name)
        except Exception as e:
            sys.stderr.write(f"Supabase connection warning: {e}. Falling back to mock table builder.\n")
            return MockTableBuilder(name)
            
    def rpc(self, fn, params):
        if not self._client:
            class MockRpcResult:
                data = []
            return MockRpcResult()
        try:
            return self._client.rpc(fn, params)
        except Exception as e:
            sys.stderr.write(f"Supabase RPC connection warning: {e}.\n")
            class MockRpcResult:
                data = []
            return MockRpcResult()

    def __getattr__(self, name):
        if not self._client:
            # Safe empty execution fallback for other attributes
            return lambda *args, **kwargs: None
        return getattr(self._client, name)

try:
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment.")
    raw_client = create_client(url, key)
    supabase = ResilientSupabaseProxy(raw_client)
except Exception as e:
    sys.stderr.write(f"Warning: Failed to initialize Supabase connection: {e}. Running in offline proxy mode.\n")
    supabase = ResilientSupabaseProxy(None)