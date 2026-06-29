// ============================================================
// ContextOS — TypeScript Interfaces
// ============================================================

export interface HealthStatus {
  status: string;
  mcp: string;
  agent: string;
}

export interface Candidate {
  id: string;
  name: string;
  email?: string;
  current_position: string;
  experience_years: number;
  location: string;
  skills: string[];
  resume_text: string;
  available?: boolean;
  notice_period_days?: number;
  salary_expectation?: number;
  created_at?: string;
}

export interface Client {
  id: string;
  name: string;
  industry?: string;
  location?: string;
  account_health: number;
  high_priority?: boolean;
  hiring_freeze?: boolean;
  created_at?: string;
}

export interface Job {
  id: string;
  title: string;
  client_id: string;
  description_text?: string;
  required_skills?: string[];
  experience_required?: number;
  location?: string;
  salary_max?: number;
  status?: string;
  clients?: { name: string };
  created_at?: string;
}

// Analysis / HITL types
export interface AnalyzeRequest {
  candidate_id: string;
}

export interface AnalysisResult {
  status: "awaiting_approval" | "no_match_found" | "already_evaluated";
  session_id: string;
  candidate: Candidate | null;
  recommendation: Recommendation | null;
  reasoning: string;
  confidence: number;
  nba_status?: string;
  knowledge_trace?: string[];
  retrieval_trace?: string[];
  planner_trace?: string[];
  decision_trace?: string[];
  business_rule_trace?: string[];
  memory_trace?: string[];
  evidence_tree?: EvidenceNode;
  confidence_breakdown?: ConfidenceBreakdown;
}

export interface Recommendation {
  job_id: string;
  job_title: string;
  client_name: string;
  client_id: string;
  confidence: number;
  reasoning: string;
  decision_confidence?: number;
  knowledge_trace?: string[];
  retrieval_trace?: string[];
  planner_trace?: string[];
  decision_trace?: string[];
  business_rule_trace?: string[];
  memory_trace?: string[];
  evidence_tree?: EvidenceNode;
  confidence_breakdown?: ConfidenceBreakdown;
}

export interface HITLPending {
  status: "pending" | "not_found";
  data?: {
    candidate_name?: string;
    job_title?: string;
    client_name?: string;
    confidence?: number;
    reasoning?: string;
  };
}

export interface HITLResponse {
  session_id: string;
  decision: "approved" | "rejected";
}

export interface HITLResult {
  status: string;
  action: Recommendation;
  reasoning: string;
}

// NBA Queue
export interface NBAAction {
  candidate_name: string;
  session_id: string;
  status: "approved" | "rejected";
  confidence: number;
  reasoning: string;
  action: Recommendation;
  created_at?: string;
}

export interface NBAQueue {
  actions: NBAAction[];
}

// Explainability
export interface EvidenceNode {
  type: string;
  title: string;
  description: string;
  score: number;
  source_id?: string;
  children?: EvidenceNode[];
}

export interface ConfidenceBreakdown {
  candidate_fit_score: number;
  top_knowledge_score: number;
  memory_score: number;
  client_health: number;
  priority_urgency_score: number;
  rule_adjustment: number;
  base_score: number;
}

// Session logs
export interface SessionLogs {
  logs: string[];
}

// Outcome
export interface OutcomeRequest {
  recommendation_id: string;
  outcome: "success" | "failure";
  notes?: string;
}

// UI State types
export interface Notification {
  id: string;
  type: "approval" | "rejection" | "recommendation" | "system";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

export interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon?: string;
  href?: string;
  action?: () => void;
  category: "navigation" | "candidate" | "client" | "action";
  keywords?: string[];
}

export type Theme = "dark" | "light";

export interface BootStep {
  label: string;
  detail?: string;
  status: "pending" | "loading" | "done" | "error";
}
