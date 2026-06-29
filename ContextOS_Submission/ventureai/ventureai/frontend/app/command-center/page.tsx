"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import useSWR from "swr";
import api from "@/lib/api";
import { cn, getInitials, formatConfidenceInt, getConfidenceColor, getLogColor } from "@/lib/utils";
import type { Candidate, AnalysisResult, NBAAction } from "@/types";
import { Play, CheckCircle, XCircle, ChevronDown, User, MapPin, Briefcase, RefreshCw, Zap, Clock, AlertCircle, Layers, Brain, Database, Sparkles, Check, Loader2 } from "lucide-react";
import ConfidenceRing from "@/components/command-center/ConfidenceRing";
import EvidenceCards from "@/components/command-center/EvidenceCards";

function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton bg-[#4E5D5A]/10 animate-pulse", className)} />;
}

function NBACard({ item, rank }: { item: NBAAction; rank: number }) {
  return (
    <motion.div layout initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
      className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-4 hover:border-[#4E5D5A]/25 rounded-xl transition-colors">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-[#1D8F88]/10 border border-[#1D8F88]/20 flex items-center justify-center text-[#1D8F88] text-xs font-bold flex-shrink-0">
          #{rank}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[#4E5D5A] text-sm font-medium truncate">{item.candidate_name}</p>
          <p className="text-[#6A756F] text-xs truncate">{item.action?.job_title}</p>
          <p className="text-[#6A756F]/80 text-xs">{item.action?.client_name}</p>
        </div>
        <div className="flex-shrink-0 text-right">
          <span className={cn("text-sm font-mono font-semibold", getConfidenceColor(item.confidence))}>
            {formatConfidenceInt(item.confidence)}
          </span>
          <div className="mt-1">
            <span className="px-1.5 py-0.5 rounded-full bg-[#1D8F88]/10 text-[#1D8F88] text-xs border border-[#1D8F88]/20">approved</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

interface PipelineStep {
  name: string;
  status: "idle" | "running" | "completed";
  subtasks: { label: string; done: boolean }[];
  icon: any;
}

function LiveAgentPipeline({ logs }: { logs: string[] }) {
  const hasLog = (query: string) => logs.some(l => l.toLowerCase().includes(query.toLowerCase()));
  
  const step1_started = hasLog("[PLANNER AGENT] Starting") || hasLog("[PLANNER AGENT] Started");
  const step1_done = hasLog("Plan compiled") || hasLog("Plan generated");
  
  const step2_started = hasLog("[CANDIDATE AGENT]");
  const step2_done = hasLog("Skills inventory mapped") || hasLog("Candidate has");
  
  const step3_started = hasLog("[CLIENT AGENT]");
  const step3_done = hasLog("Policy bypass checked") || hasLog("Searching open roles");
  
  const step4_started = hasLog("[KNOWLEDGE AGENT]");
  const step4_done = hasLog("Retrieved 3 knowledge items") || hasLog("Retrieved 3 docs");
  
  const step5_started = hasLog("[ACTION PLANNER] Assembling") || hasLog("[ACTION PLANNER] Evaluating") || hasLog("Business Rules");
  const step5_done = hasLog("Running Business Rules") || hasLog("Awaiting recruiter response") || hasLog("GRAPH PAUSED");

  const step6_started = hasLog("HITL GATE") || hasLog("GRAPH PAUSED");
  const step6_done = hasLog("Awaiting human recruiter approval") || hasLog("Awaiting recruiter response") || hasLog("GRAPH PAUSED");

  const steps: PipelineStep[] = [
    {
      name: "Orchestration Planner",
      status: step1_done ? "completed" : step1_started ? "running" : "idle",
      icon: Brain,
      subtasks: [
        { label: "Building execution plan", done: step1_started },
        { label: "Generating LangGraph state routing", done: step1_done }
      ]
    },
    {
      name: "Candidate Profiler",
      status: step2_done ? "completed" : step2_started ? "running" : "idle",
      icon: User,
      subtasks: [
        { label: "Parsing profile credentials", done: step2_started },
        { label: "Extracting skills inventory matrix", done: step2_done }
      ]
    },
    {
      name: "Client Vacancy Scanner",
      status: step3_done ? "completed" : step3_started ? "running" : "idle",
      icon: Briefcase,
      subtasks: [
        { label: "Locating active client accounts", done: step3_started },
        { label: "Retrieving open vacancies", done: step3_done }
      ]
    },
    {
      name: "Knowledge RAG Search",
      status: step4_done ? "completed" : step4_started ? "running" : "idle",
      icon: Database,
      subtasks: [
        { label: "Executing retrospective query", done: step4_started },
        { label: "Ranking context overlaps", done: step4_done }
      ]
    },
    {
      name: "Policy Controls & Memory",
      status: step5_done ? "completed" : step5_started ? "running" : "idle",
      icon: Layers,
      subtasks: [
        { label: "Accessing placement feedback memory", done: step5_started },
        { label: "Evaluating business rules constraints", done: step5_done }
      ]
    },
    {
      name: "Decision Intelligence",
      status: step6_done ? "completed" : step6_started ? "running" : "idle",
      icon: Sparkles,
      subtasks: [
        { label: "Computing decision confidence weights", done: step6_started },
        { label: "Awaiting recruiter response", done: step6_done }
      ]
    }
  ];

  let ticker = 0;
  if (step1_done) ticker = 25;
  if (step2_done) ticker = 48;
  if (step3_done) ticker = 63;
  if (step4_done) ticker = 74;
  if (step5_done) ticker = 82;
  if (step6_started) ticker = 91;
  if (step6_done) ticker = 95;

  return (
    <div className="space-y-6 bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between border-b border-[#4E5D5A]/10 pb-4">
        <div>
          <h4 className="text-sm font-semibold text-[#4E5D5A]">Live Agent Reasoning Stream</h4>
          <p className="text-[11px] text-[#6A756F] mt-0.5">LangGraph routing and specialist agent node updates</p>
        </div>
        <div className="flex items-center gap-2 bg-[#1D8F88]/10 border border-[#1D8F88]/20 px-3 py-1.5 rounded-full">
          <Loader2 className="w-3.5 h-3.5 text-[#1D8F88] animate-spin" />
          <span className="text-xs font-mono font-bold text-[#1D8F88]">Confidence: {ticker}%</span>
        </div>
      </div>
      
      <div className="relative pl-6 space-y-6 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-px before:bg-[#4E5D5A]/10">
        {steps.map((step, i) => {
          const StepIcon = step.icon;
          const isIdle = step.status === "idle";
          const isRunning = step.status === "running";
          const isCompleted = step.status === "completed";

          return (
            <div key={i} className="relative group">
              <div className={cn(
                "absolute -left-[23px] top-0 w-6 h-6 rounded-full flex items-center justify-center border text-[10px] transition-all duration-300",
                isCompleted && "bg-[#1D8F88]/10 border-[#1D8F88]/35 text-[#1D8F88] shadow-sm",
                isRunning && "bg-[#F9A66C]/10 border-[#F9A66C]/35 text-[#F9A66C] status-pulse",
                isIdle && "bg-[#EFE8DE] border-[#4E5D5A]/10 text-[#6A756F]"
              )}>
                {isCompleted ? <Check className="w-3.5 h-3.5" /> : isRunning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <StepIcon className="w-3 h-3" />}
              </div>

              <div className="pl-4">
                <span className={cn(
                  "text-xs font-medium block transition-colors",
                  isCompleted && "text-[#4E5D5A]",
                  isRunning && "text-[#F9A66C] font-semibold",
                  isIdle && "text-[#6A756F]/65"
                )}>
                  {step.name}
                </span>
                
                {!isIdle && (
                  <div className="mt-1.5 space-y-1">
                    {step.subtasks.map((task, tIdx) => (
                      <div key={tIdx} className="flex items-center gap-1.5 text-[11px]">
                        <div className={cn(
                          "w-1.5 h-1.5 rounded-full",
                          task.done ? "bg-[#1D8F88]" : "bg-[#4E5D5A]/20 animate-pulse"
                        )} />
                        <span className={task.done ? "text-[#6A756F]" : "text-[#6A756F]/60"}>
                          {task.label}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function CommandCenterPage() {
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [showEvidence, setShowEvidence] = useState(false);
  const [optimisticDecision, setOptimisticDecision] = useState<"approved" | "rejected" | null>(null);
  const [toastMsg, setToastMsg] = useState<{ text: string; type: "success" | "error" | "warning" } | null>(null);
  const logsRef = useRef<HTMLDivElement>(null);

  const { data: candidates, isLoading: loadingCandidates } = useSWR("candidates", api.getCandidates);
  const { data: nbaData, mutate: mutateNBA } = useSWR("nba-queue", api.getNBAQueue, { refreshInterval: 5000 });

  const baseScore = analysis?.recommendation?.confidence_breakdown?.base_score || 0;
  const isSuppressed = analysis?.confidence === 0 && baseScore > 0;

  useEffect(() => {
    if (logsRef.current) logsRef.current.scrollTop = logsRef.current.scrollHeight;
  }, [logs]);

  useEffect(() => {
    if (!toastMsg) return;
    const t = setTimeout(() => setToastMsg(null), 4000);
    return () => clearTimeout(t);
  }, [toastMsg]);

  function cleanReasoning(text: string) {
    if (!text) return "";
    const index = text.search(/###|####|```|Hierarchical/i);
    if (index !== -1) {
      return text.substring(0, index).trim();
    }
    return text;
  }

  async function handleAnalyze() {
    if (!selectedCandidate) return;
    setIsAnalyzing(true);
    setAnalysis(null);
    setLogs([]);
    setShowEvidence(false);
    setOptimisticDecision(null);

    // Generate a unique session ID on the client side to enable real-time log polling
    const candidateIdClean = selectedCandidate.id.replace(/[^a-zA-Z0-9]/g, "");
    const randomHex = Math.random().toString(16).substring(2, 10);
    const sessionId = `session_${candidateIdClean}_${randomHex}`;

    // Poll the backend session logs every 1.5s while the request is running
    let isFinished = false;
    const pollInterval = setInterval(async () => {
      if (isFinished) return;
      try {
        const logData = await api.getSessionLogs(sessionId);
        if (logData && logData.logs && logData.logs.length > 0) {
          setLogs(logData.logs);
        }
      } catch (e) {
        // Logs might not be populated in Redis yet; ignore and continue polling
      }
    }, 1500);

    try {
      const result = await api.analyze(selectedCandidate.id, sessionId);
      isFinished = true;
      clearInterval(pollInterval);
      
      setAnalysis(result);
      if (result.session_id) {
        const logData = await api.getSessionLogs(result.session_id);
        setLogs(logData.logs || []);
      }
    } catch (err: unknown) {
      isFinished = true;
      clearInterval(pollInterval);
      const message = err instanceof Error ? err.message : "Analysis failed";
      setToastMsg({ text: message, type: "error" });
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleHITL(decision: "approved" | "rejected") {
    if (!analysis?.session_id) return;
    setOptimisticDecision(decision);
    try {
      await api.respondHITL(analysis.session_id, decision);
      setToastMsg({
        text: decision === "approved" ? "Approved and added to Decision Queue." : "Rejected. Decision logged.",
        type: decision === "approved" ? "success" : "warning",
      });
      await mutateNBA();
      setAnalysis(null);
      setLogs([]);
    } catch (err: unknown) {
      setOptimisticDecision(null);
      const message = err instanceof Error ? err.message : "HITL response failed";
      setToastMsg({ text: message, type: "error" });
    }
  }

  const nbaActions = nbaData?.actions || [];

  return (
    <div className="h-full flex flex-col bg-[#F7F5EF] text-[#4E5D5A]">
      <AnimatePresence>
        {toastMsg && (
          <motion.div initial={{ opacity: 0, y: -20, x: "-50%" }} animate={{ opacity: 1, y: 0, x: "-50%" }} exit={{ opacity: 0, y: -20, x: "-50%" }}
            className={cn("fixed top-4 left-1/2 z-[2000] px-4 py-3 rounded-full border text-sm font-medium shadow-lg",
              toastMsg.type === "success" && "bg-[#1D8F88] border-[#1D8F88] text-[#F7F5EF]",
              toastMsg.type === "error" && "bg-[#F17A7E] border-[#F17A7E] text-[#F7F5EF]",
              toastMsg.type === "warning" && "bg-[#FFC94B] border-[#FFC94B] text-[#4E5D5A]")}>
            {toastMsg.text}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex-1 flex overflow-hidden">
        {/* Left: Candidate Workspace */}
        <div className="flex-1 flex flex-col overflow-hidden border-r border-[#4E5D5A]/10">
          <div className="px-6 py-4 border-b border-[#4E5D5A]/10 flex items-center gap-4">
            <h1 className="text-[#4E5D5A] font-semibold text-sm">AI Command Center</h1>
            <span className="text-[#6A756F]/30">·</span>
            {loadingCandidates ? <Skeleton className="h-8 w-48 rounded-lg" /> : (
              <div className="relative">
                <select value={selectedCandidate?.id || ""} onChange={(e) => {
                  const c = candidates?.find((c) => c.id === e.target.value);
                  setSelectedCandidate(c || null); setAnalysis(null); setLogs([]);
                }} className="appearance-none bg-[#F4F1EA] border border-[#4E5D5A]/10 text-[#4E5D5A] text-sm pl-3 pr-8 py-1.5 rounded-lg focus:outline-none focus:border-[#1D8F88] cursor-pointer" aria-label="Select candidate">
                  <option value="">Select candidate...</option>
                  {candidates?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6A756F] pointer-events-none" />
              </div>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {selectedCandidate && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-[#4A6163] flex items-center justify-center text-[#F7F5EF] font-bold text-lg flex-shrink-0">
                    {getInitials(selectedCandidate.name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h2 className="text-[#4E5D5A] font-semibold">{selectedCandidate.name}</h2>
                    <p className="text-[#6A756F] text-sm">{selectedCandidate.current_position}</p>
                    <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-[#6A756F]/80">
                      <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" />{selectedCandidate.experience_years}y exp</span>
                      <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{selectedCandidate.location}</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {selectedCandidate.skills?.slice(0, 8).map((skill) => (
                        <span key={skill} className="px-2 py-0.5 rounded bg-[#EFE8DE] border border-[#4E5D5A]/10 text-xs text-[#4E5D5A]">{skill}</span>
                      ))}
                    </div>
                  </div>
                  <button onClick={handleAnalyze} disabled={isAnalyzing}
                    className={cn("flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
                      isAnalyzing ? "bg-[#1D8F88]/20 text-[#1D8F88] cursor-not-allowed"
                        : "bg-[#1D8F88] hover:bg-[#1D8F88]/80 text-[#F7F5EF] active:scale-[0.98] shadow-sm")}>
                    {isAnalyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                    {isAnalyzing ? "Analyzing..." : "Run Agent"}
                  </button>
                </div>
              </motion.div>
            )}

            {!selectedCandidate && !loadingCandidates && (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-16 h-16 rounded-2xl bg-[#F4F1EA] border border-[#4E5D5A]/10 flex items-center justify-center mb-4">
                  <User className="w-8 h-8 text-[#6A756F]" />
                </div>
                <p className="text-[#4E5D5A] font-medium mb-1">No candidate selected</p>
                <p className="text-[#6A756F] text-sm">Select a candidate from the dropdown to begin AI analysis</p>
              </div>
            )}

            <AnimatePresence>
              {logs.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
                  <LiveAgentPipeline logs={logs} />
                  
                  <details className="group border border-[#4E5D5A]/10 rounded-xl overflow-hidden bg-[#F4F1EA]/50">
                    <summary className="flex items-center justify-between px-4 py-2.5 text-xs font-mono text-[#6A756F] hover:bg-[#EFE8DE] cursor-pointer select-none">
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#1D8F88] status-pulse" />
                        <span>View Raw Orchestration Logs</span>
                      </div>
                      <ChevronDown className="w-3.5 h-3.5 transition-transform group-open:rotate-180" />
                    </summary>
                    <div ref={logsRef} className="max-h-48 overflow-y-auto p-4 font-mono text-xs space-y-1 bg-[#EFE8DE] border-t border-[#4E5D5A]/10">
                      {logs.map((line, i) => (
                        <motion.div key={i} initial={{ opacity: 0, x: -4 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.02 }}
                          className={getLogColor(line)}>{line}</motion.div>
                      ))}
                      <span className="terminal-cursor" />
                    </div>
                  </details>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {analysis && !isAnalyzing && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                  transition={{ type: "spring", stiffness: 200, damping: 20 }}>
                  <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-5 space-y-4 shadow-sm">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          {isSuppressed ? (
                            <>
                              <span className="px-2 py-0.5 rounded-full text-xs font-mono border bg-[#1D8F88]/10 text-[#1D8F88] border-[#1D8F88]/20">
                                AI Match Score: {formatConfidenceInt(baseScore)}
                              </span>
                              <span className="px-2 py-0.5 rounded-full text-xs font-mono border bg-[#F17A7E]/10 text-[#F17A7E] border-[#F17A7E]/20 font-bold">
                                Status: 🚫 Blocked by Enterprise Policy
                              </span>
                            </>
                          ) : (
                            <span className={cn("px-2 py-0.5 rounded-full text-xs font-mono border",
                              analysis.status === "awaiting_approval" ? "bg-[#FFC94B]/10 text-[#FFC94B] border-[#FFC94B]/20"
                                : analysis.status === "already_evaluated" ? "bg-[#1D8F88]/10 text-[#1D8F88] border-[#1D8F88]/20"
                                : "bg-[#EFE8DE] text-[#6A756F] border-[#4E5D5A]/10")}>
                              {analysis.status === "awaiting_approval" ? "Awaiting Approval"
                                : analysis.status === "already_evaluated" ? "Already Evaluated" : "No Match Found"}
                            </span>
                          )}
                        </div>
                        {analysis.recommendation && (
                          <div className="mt-2">
                            <h3 className="text-[#4E5D5A] font-semibold text-lg">{analysis.recommendation.job_title}</h3>
                            <p className="text-[#6A756F] text-sm">{analysis.recommendation.client_name}</p>
                          </div>
                        )}
                      </div>
                      {analysis.recommendation && (
                        <ConfidenceRing 
                          value={isSuppressed ? baseScore : analysis.confidence} 
                          size={72} 
                        />
                      )}
                    </div>

                    {analysis.status === "no_match_found" && (
                      <div className="flex items-center gap-2 text-[#FFC94B] text-sm">
                        <AlertCircle className="w-4 h-4" />No matching open roles found.
                      </div>
                    )}

                    {analysis.reasoning && (() => {
                      const rawText = cleanReasoning(analysis.reasoning);
                      
                      // Helper to extract by tag
                      const extract = (tag: string) => {
                        const regex = new RegExp(`\\[${tag}\\]:\\s*([\\s\\S]*?)(?=\\[[A-Z\\s]+\\]:|$)`, 'i');
                        const match = rawText.match(regex);
                        return match ? match[1].trim() : "";
                      };

                      const matchFit = extract("MATCH FIT");
                      const placementEvidence = extract("PLACEMENT EVIDENCE");
                      const gapsMitigation = extract("GAPS & MITIGATION");
                      const pitchHook = extract("RECRUITER PITCH HOOK");
                      const strengthsRaw = extract("KEY STRENGTHS");
                      
                      const keyStrengths = strengthsRaw
                        ? strengthsRaw.split(/\n|-|\*/).map(s => s.trim()).filter(s => s.length > 0)
                        : [];

                      const hasParsed = matchFit || placementEvidence || gapsMitigation || pitchHook || keyStrengths.length > 0;

                      if (!hasParsed) {
                        return (
                          <div className="bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded-lg p-3 text-xs text-[#4E5D5A] leading-relaxed font-sans font-medium">
                            <span className="text-[10px] font-mono font-bold tracking-wider text-[#1D8F88] uppercase block mb-1">Match Evaluation Summary</span>
                            {rawText}
                          </div>
                        );
                      }

                      return (
                        <div className="space-y-3">
                          <span className="text-[10px] font-mono font-bold tracking-wider text-[#1D8F88] uppercase block mb-1">Match Evaluation Summary</span>
                          
                          {matchFit && (
                            <div className="bg-[#1D8F88]/5 border border-[#1D8F88]/15 rounded-xl p-3.5 text-xs text-[#4E5D5A] space-y-1">
                              <div className="flex items-center gap-1.5 font-bold text-[#1D8F88] uppercase tracking-wider text-[10px] font-mono mb-1">
                                <Sparkles className="w-3.5 h-3.5" />
                                Match Fit
                              </div>
                              <p className="leading-relaxed font-medium">{matchFit}</p>
                            </div>
                          )}

                          {keyStrengths.length > 0 && (
                            <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-3.5 text-xs text-[#4E5D5A] space-y-2">
                              <div className="flex items-center gap-1.5 font-bold text-[#4E5D5A] uppercase tracking-wider text-[10px] font-mono">
                                <Zap className="w-3.5 h-3.5 text-[#FFC94B]" />
                                Key Strengths
                              </div>
                              <ul className="grid grid-cols-1 gap-1.5">
                                {keyStrengths.map((str, idx) => (
                                  <li key={idx} className="flex items-start gap-2 leading-relaxed">
                                    <div className="w-3.5 h-3.5 rounded-full bg-[#1D8F88]/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                                      <Check className="w-2.5 h-2.5 text-[#1D8F88]" />
                                    </div>
                                    <span className="font-medium">{str}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {placementEvidence && (
                            <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-3.5 text-xs text-[#4E5D5A] space-y-1">
                              <div className="flex items-center gap-1.5 font-bold text-[#4E5D5A] uppercase tracking-wider text-[10px] font-mono mb-1">
                                <Briefcase className="w-3.5 h-3.5 text-[#4E5D5A]/60" />
                                Placement Evidence
                              </div>
                              <p className="leading-relaxed font-medium">{placementEvidence}</p>
                            </div>
                          )}

                          {gapsMitigation && (
                            <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-3.5 text-xs text-[#4E5D5A] space-y-1">
                              <div className="flex items-center gap-1.5 font-bold text-[#4E5D5A] uppercase tracking-wider text-[10px] font-mono mb-1">
                                <AlertCircle className="w-3.5 h-3.5 text-[#6A756F]" />
                                Gaps &amp; Mitigation
                              </div>
                              <p className="leading-relaxed font-medium">{gapsMitigation}</p>
                            </div>
                          )}

                          {pitchHook && (
                            <div className="bg-[#FFC94B]/5 border-l-2 border-[#FFC94B] rounded-r-xl p-3.5 text-xs text-[#4E5D5A] space-y-1.5">
                              <div className="flex items-center gap-1.5 font-bold text-[#FFC94B] uppercase tracking-wider text-[10px] font-mono">
                                <Brain className="w-3.5 h-3.5" />
                                Recruiter Pitch Hook
                              </div>
                              <p className="leading-relaxed italic font-semibold text-[#4E5D5A]/90">"{pitchHook.replace(/^"|"$/g, '')}"</p>
                            </div>
                          )}
                        </div>
                      );
                    })()}

                    {analysis.confidence === 0 && analysis.status === "awaiting_approval" && (
                      <div className="bg-[#F17A7E]/10 border border-[#F17A7E]/20 rounded-lg p-3 text-xs text-[#F17A7E] flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#F17A7E]" />
                        <div>
                          <p className="font-semibold text-[#F17A7E] font-bold">🚫 Recommendation Blocked by Enterprise Policy</p>
                          <p className="text-[#6A756F] mt-1 leading-relaxed">Candidate is an excellent technical match, but enterprise governance prevented automatic recommendation.</p>
                        </div>
                      </div>
                    )}

                    {analysis.confidence_breakdown && (
                      <button onClick={() => setShowEvidence(!showEvidence)}
                        className="flex items-center gap-1.5 text-xs text-[#1D8F88] hover:text-[#1D8F88]/80 transition-colors">
                        <Layers className="w-3.5 h-3.5" />
                        {showEvidence ? "Hide" : "View"} Evidence Chain
                        <ChevronDown className={cn("w-3 h-3 transition-transform", showEvidence && "rotate-180")} />
                      </button>
                    )}

                    <AnimatePresence>
                      {showEvidence && analysis.confidence_breakdown && (
                        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
                          <EvidenceCards breakdown={analysis.confidence_breakdown} businessRuleTrace={analysis.business_rule_trace || []} memoryTrace={analysis.memory_trace || []} />
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {analysis.status === "awaiting_approval" && !optimisticDecision && (
                      <div className="flex gap-3 pt-2">
                        <button onClick={() => handleHITL("approved")}
                          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-full bg-[#1D8F88]/10 hover:bg-[#1D8F88]/20 border border-[#1D8F88]/20 text-[#1D8F88] font-medium text-sm transition-all"
                          aria-label="Approve recommendation">
                          <CheckCircle className="w-4 h-4" />Approve Pitch
                        </button>
                        <button onClick={() => handleHITL("rejected")}
                          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-full bg-[#F17A7E]/10 hover:bg-[#F17A7E]/20 border border-[#F17A7E]/20 text-[#F17A7E] font-medium text-sm transition-all"
                          aria-label="Reject recommendation">
                          <XCircle className="w-4 h-4" />Reject Pitch
                        </button>
                      </div>
                    )}

                    {optimisticDecision && (
                      <div className={cn("flex items-center justify-center gap-2 py-3 rounded-full text-sm font-medium",
                        optimisticDecision === "approved" ? "bg-[#1D8F88]/10 text-[#1D8F88]" : "bg-[#F17A7E]/10 text-[#F17A7E]")}>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Processing {optimisticDecision} decision...
                      </div>
                    )}

                    {analysis.status === "already_evaluated" && (
                      <div className="flex items-center gap-2 text-[#1D8F88] text-sm">
                        <Clock className="w-4 h-4" />Status: {analysis.nba_status?.toUpperCase()}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right: NBA Queue */}
        <div className="w-80 flex flex-col overflow-hidden flex-shrink-0 border-l border-[#4E5D5A]/10">
          <div className="px-5 py-4 border-b border-[#4E5D5A]/10 flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#1D8F88]" />
            <h2 className="text-[#4E5D5A] font-medium text-sm">Decision Queue</h2>
            <span className="ml-auto bg-[#1D8F88]/10 text-[#1D8F88] text-xs font-mono px-1.5 py-0.5 rounded-full">{nbaActions.length}</span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            <AnimatePresence>
              {nbaActions.length === 0 ? (
                <div className="py-12 text-center text-[#6A756F] text-sm">
                  <Zap className="w-8 h-8 mx-auto mb-3 opacity-30 text-[#6A756F]" />
                  <p>No approved recommendations yet.</p>
                  <p className="text-xs mt-1 text-[#6A756F]/70">Analyze and approve a match to populate the queue.</p>
                </div>
              ) : (
                nbaActions.map((action, i) => <NBACard key={action.session_id || i} item={action} rank={i + 1} />)
              )}
            </AnimatePresence>
          </div>
          <div className="px-4 py-2 border-t border-[#4E5D5A]/10 flex items-center gap-1.5 text-xs text-[#6A756F]">
            <RefreshCw className="w-3 h-3 text-[#6A756F]/60" />Auto-syncing every 5s
          </div>
        </div>
      </div>
    </div>
  );
}
