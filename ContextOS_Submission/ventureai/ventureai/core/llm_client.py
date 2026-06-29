import os
import asyncio
import sys
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# ─────────────────────────────────────────────
# Structured Output Schema
# ─────────────────────────────────────────────
class MatchRecommendation(BaseModel):
    job_id: str = Field(description="UUID of the best matching job")
    job_title: str = Field(description="Job title")
    client_name: str = Field(description="Client company name")
    client_id: str = Field(description="UUID of the client")
    confidence: float = Field(description="Match confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Detailed evaluation including Strengths, Evidence from placements history, Gaps, and a Pitch Angle")

# ─────────────────────────────────────────────
# Provider 1: Groq — fast ReAct loop reasoning
# llama3-8b-8192 has higher free-tier RPM than llama-3.1-8b-instant
# ─────────────────────────────────────────────
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
    max_retries=0,
)

# ─────────────────────────────────────────────
# Provider 2: Gemini — structured output calls
# Separate quota pool from Groq
# ─────────────────────────────────────────────
GEMINI_AVAILABLE = False
gemini_llm = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    _gemini_key = os.getenv("GEMINI_API_KEY", "")
    if _gemini_key:
        gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=_gemini_key,
            temperature=0.1,
            convert_system_message_to_human=True,
            max_retries=0,
        )
        GEMINI_AVAILABLE = True
except Exception as _e:
    sys.stderr.write(f"[LLM CLIENT] Gemini unavailable: {_e}\n")


# Global registry mapping id(runnable) -> schema to bypass frozen Pydantic object restrictions
_STRUCTURED_SCHEMAS = {}

# ─────────────────────────────────────────────
# get_structured_llm: prefer Gemini, fall back to Groq
# ─────────────────────────────────────────────
def get_structured_llm(schema: type):
    """Returns structured-output LLM. Tries Gemini first (separate quota), falls back to Groq."""
    if GEMINI_AVAILABLE and gemini_llm is not None:
        try:
            structured = gemini_llm.with_structured_output(schema)
            _STRUCTURED_SCHEMAS[id(structured)] = schema
            return structured
        except Exception:
            pass
    structured = llm.with_structured_output(schema)
    _STRUCTURED_SCHEMAS[id(structured)] = schema
    return structured


# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────
def _find_chat_groq(obj):
    from langchain_groq import ChatGroq
    if isinstance(obj, ChatGroq):
        return obj
    if hasattr(obj, "bound"):
        return _find_chat_groq(obj.bound)
    return None

def _is_gemini(obj):
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        if isinstance(obj, ChatGoogleGenerativeAI):
            return True
        if hasattr(obj, "bound") and isinstance(obj.bound, ChatGoogleGenerativeAI):
            return True
    except Exception:
        pass
    return False

def _is_rate_limit(err_msg: str) -> bool:
    return any(k in err_msg.lower() for k in ["429", "rate", "limit", "quota", "tpd", "resource_exhausted", "exhausted"])

def _is_context_error(err_msg: str) -> bool:
    # Only trigger on explicit context length errors, not generic 400s
    keywords = ["context_length", "maximum context", "too long", "string too long", "context window"]
    return any(k in err_msg.lower() for k in keywords)


# ─────────────────────────────────────────────
# safe_ainvoke — dual-provider aware
# ─────────────────────────────────────────────
async def safe_ainvoke(llm_object, messages, session_id=None, log_callback=None):
    """
    Safely invokes an LLM with:
    - Rate limit detection and backoff for both Groq and Gemini
    - Cross-provider fallback: Groq → Gemini, Gemini → Groq
    - Context length error handling (truncates long messages)
    """
    max_attempts = 5
    groq_fallbacks = ["llama-3.3-70b-versatile"]


    def _log(msg):
        if log_callback and session_id:
            log_callback(session_id, msg)
        else:
            sys.stderr.write(msg + "\n")

    for attempt in range(max_attempts):
        try:
            return await llm_object.ainvoke(messages)

        except Exception as e:
            err_msg = str(e)

            if _is_context_error(err_msg):
                _log(f"      [CONTEXT ERROR] Message too long (attempt {attempt+1}). Trimming context...")
                if isinstance(messages, list) and len(messages) > 2:
                    messages = [messages[0], messages[-1]]
                    continue
                raise e

            if not _is_rate_limit(err_msg):
                raise e

            # ── Rate limit handling ──
            is_groq_call = _find_chat_groq(llm_object) is not None
            is_gemini_call = _is_gemini(llm_object)

            if attempt >= 2:
                # Cross-provider fallback
                if is_groq_call and GEMINI_AVAILABLE and gemini_llm:
                    _log(f"      [RATE LIMIT] Groq exhausted. Switching to Gemini for this call...")
                    try:
                        fallback_obj = gemini_llm
                        if id(llm_object) in _STRUCTURED_SCHEMAS:
                            fallback_obj = gemini_llm.with_structured_output(_STRUCTURED_SCHEMAS[id(llm_object)])
                        elif hasattr(llm_object, "kwargs") and "tools" in llm_object.kwargs:
                            fallback_obj = gemini_llm.bind_tools(llm_object.kwargs["tools"])
                        return await fallback_obj.ainvoke(messages)
                    except Exception as ge:
                        if _is_rate_limit(str(ge)):
                            _log(f"      [GEMINI RATE LIMIT] Gemini also rate-limited. Waiting 20s...")
                            await asyncio.sleep(20)
                        else:
                            _log(f"      [GEMINI ERROR] {str(ge)[:100]}")

                elif is_gemini_call and llm:
                    _log(f"      [RATE LIMIT] Gemini exhausted. Falling back to Groq...")
                    try:
                        fallback_obj = llm
                        if id(llm_object) in _STRUCTURED_SCHEMAS:
                            fallback_obj = llm.with_structured_output(_STRUCTURED_SCHEMAS[id(llm_object)])
                        elif hasattr(llm_object, "kwargs") and "tools" in llm_object.kwargs:
                            fallback_obj = llm.bind_tools(llm_object.kwargs["tools"])
                        return await fallback_obj.ainvoke(messages)
                    except Exception as ge:
                        _log(f"      [GROQ FALLBACK ERROR] {str(ge)[:100]}")

            # Try next Groq model
            chat_groq = _find_chat_groq(llm_object)
            if chat_groq and groq_fallbacks and attempt < 2:
                old = chat_groq.model_name
                new = groq_fallbacks.pop(0)
                chat_groq.model_name = new
                _log(f"      [RATE LIMIT] Groq: {old} -> {new}")
                await asyncio.sleep(3)
                continue

            # Standard backoff
            if attempt < max_attempts - 1:
                wait = 10 * (attempt + 1)
                _log(f"      [RATE LIMIT] Waiting {wait}s before retry {attempt+1}/{max_attempts-1}...")
                await asyncio.sleep(wait)
            else:
                raise e
