// ============================================================
// ContextOS — Typed API Layer
// All calls go to FastAPI backend at http://127.0.0.1:8000
// Backend files are NEVER modified — this is a pure consumer
// ============================================================

import type {
  HealthStatus,
  Candidate,
  Client,
  Job,
  AnalysisResult,
  HITLPending,
  HITLResult,
  NBAQueue,
  SessionLogs,
  OutcomeRequest,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

// Health
export const api = {
  health: (): Promise<HealthStatus> => apiFetch("/health"),

  // Candidates
  getCandidates: (): Promise<Candidate[]> => apiFetch("/candidates"),
  createCandidate: (candidate: Partial<Candidate> & { name: string; current_position: string; experience_years: number; location: string }): Promise<any> =>
    apiFetch("/candidates", {
      method: "POST",
      body: JSON.stringify(candidate),
    }),

  parseResume: (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    return fetch(`${BASE_URL}/candidates/parse`, {
      method: "POST",
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `Upload error ${res.status}`);
      }
      return res.json();
    });
  },

  // Clients
  getClients: (): Promise<Client[]> => apiFetch("/clients"),
  createClient: (client: { name: string; industry?: string; account_health?: number }): Promise<any> =>
    apiFetch("/clients", {
      method: "POST",
      body: JSON.stringify(client),
    }),

  // Jobs
  getJobs: (): Promise<Job[]> => apiFetch("/jobs"),
  createJob: (job: { client_id: string; title: string; required_skills: string[]; location: string; salary_range?: string; description_text?: string }): Promise<any> =>
    apiFetch("/jobs", {
      method: "POST",
      body: JSON.stringify(job),
    }),

  // Analyze a candidate — triggers LangGraph ReAct agent
  analyze: (candidate_id: string, session_id?: string): Promise<AnalysisResult> =>
    apiFetch("/analyze", {
      method: "POST",
      body: JSON.stringify({ candidate_id, session_id }),
    }),

  // HITL
  getHITLPending: (session_id: string): Promise<HITLPending> =>
    apiFetch(`/hitl/pending/${session_id}`),

  respondHITL: (
    session_id: string,
    decision: "approved" | "rejected"
  ): Promise<HITLResult> =>
    apiFetch("/hitl/respond", {
      method: "POST",
      body: JSON.stringify({ session_id, decision }),
    }),

  // NBA Queue
  getNBAQueue: (): Promise<NBAQueue> => apiFetch("/nba/queue"),

  // Session logs
  getSessionLogs: (session_id: string): Promise<SessionLogs> =>
    apiFetch(`/logs/${session_id}`),

  // Outcome logging
  logOutcome: (req: OutcomeRequest): Promise<unknown> =>
    apiFetch("/analyze/outcome", {
      method: "POST",
      body: JSON.stringify(req),
    }),
};

export default api;
