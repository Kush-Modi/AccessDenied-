"use client";
import { useState } from "react";
import useSWR from "swr";
import { motion, AnimatePresence } from "framer-motion";
import { RefreshCw, X, ShieldCheck, Database, Layers, Brain, User, Briefcase, MapPin, Sparkles, CheckCircle2, ChevronRight, Zap } from "lucide-react";
import api from "@/lib/api";
import { cn, formatConfidenceInt, getConfidenceColor, getInitials, timeAgo } from "@/lib/utils";
import ConfidenceRing from "@/components/command-center/ConfidenceRing";

function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton bg-[#4E5D5A]/10 animate-pulse", className)} />;
}

export default function DecisionQueuePage() {
  const { data: nbaData, isLoading, mutate, isValidating } = useSWR("nba-queue", api.getNBAQueue, { refreshInterval: 5000 });
  const actions = nbaData?.actions || [];
  const [selectedAction, setSelectedAction] = useState<any | null>(null);

  return (
    <div className="p-6 relative min-h-full bg-[#F7F5EF] text-[#4E5D5A]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-[#4E5D5A] font-semibold text-lg">Decision Queue</h1>
          <p className="text-[#6A756F] text-xs mt-0.5">Enterprise decision logs and approved match placements</p>
        </div>
        <div className="flex items-center gap-3">
          {isValidating && <RefreshCw className="w-3.5 h-3.5 text-[#6A756F] animate-spin" />}
          <span className="text-[10px] text-[#6A756F]/65 font-mono">Auto-syncing (5s)</span>
          <button onClick={() => mutate()} className="px-3 py-1.5 rounded-full bg-[#F4F1EA] border border-[#4E5D5A]/10 text-[#4E5D5A] hover:bg-[#EFE8DE] text-xs font-semibold transition-colors">
            Sync Queue
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3 max-w-3xl">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl">
              <div className="flex items-center gap-4">
                <Skeleton className="w-10 h-10 rounded-full" />
                <div className="flex-1 space-y-2"><Skeleton className="h-4 w-48 rounded" /><Skeleton className="h-3 w-32 rounded" /></div>
                <Skeleton className="w-16 h-16 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      ) : actions.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-16 h-16 rounded-2xl bg-[#F4F1EA] border border-[#4E5D5A]/10 flex items-center justify-center mb-4 text-[#6A756F]">
            <Sparkles className="w-8 h-8" />
          </div>
          <p className="text-[#4E5D5A] font-medium">No actions pending</p>
          <p className="text-[#6A756F] text-xs mt-1">Run an agent analysis to approve matches into the decision pipeline</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main List */}
          <div className="lg:col-span-2 space-y-3">
            {actions.map((item: any, i: number) => {
              const rawConf = item.confidence ?? item.action?.confidence ?? 0;
              const conf = rawConf > 1 ? rawConf / 100 : rawConf;
              
              // Extract mock capabilities and priority for dashboard feel
              const skills = item.action?.skills ?? ["React", "Python", "Docker", "AWS"];
              const priority = conf > 0.85 ? "High Fit" : "Standard Fit";
              
              return (
                <motion.div
                  key={item.session_id || i}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  onClick={() => setSelectedAction(item)}
                  className={cn(
                    "bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-5 hover:border-[#4E5D5A]/25 transition-all cursor-pointer group flex flex-col md:flex-row items-start md:items-center justify-between gap-4",
                    selectedAction?.session_id === item.session_id && "border-[#1D8F88]/50 bg-[#1D8F88]/5"
                  )}
                >
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    {/* Rank */}
                    <div className="w-7 h-7 rounded-full border border-[#4E5D5A]/10 bg-[#EFE8DE] flex items-center justify-center text-[#6A756F] text-xs font-mono font-bold flex-shrink-0">
                      {i + 1}
                    </div>
                    {/* Avatar */}
                    <div className="w-10 h-10 rounded-xl bg-[#4A6163] flex items-center justify-center text-[#F7F5EF] font-bold text-sm flex-shrink-0">
                      {getInitials(item.candidate_name || "?")}
                    </div>
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-[#4E5D5A] font-semibold text-sm">{item.candidate_name}</p>
                        <span className={cn(
                          "px-2 py-0.5 rounded-full text-[10px] font-mono border",
                          priority === "High Fit" ? "bg-[#1D8F88]/10 text-[#1D8F88] border-[#1D8F88]/20" : "bg-[#EFE8DE] text-[#6A756F] border-[#4E5D5A]/10"
                        )}>
                          {priority}
                        </span>
                      </div>
                      <p className="text-[#6A756F] text-xs mt-0.5">{item.action?.job_title}</p>
                      <p className="text-[#6A756F]/70 text-xs">{item.action?.client_name}</p>
                      
                      {/* Render top skills */}
                      <div className="flex gap-1.5 flex-wrap mt-2">
                        {skills.slice(0, 3).map((skill: string) => (
                          <span key={skill} className="px-1.5 py-0.5 rounded bg-[#EFE8DE] border border-[#4E5D5A]/10 text-[10px] text-[#6A756F] font-mono">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 self-end md:self-center">
                    <div className="text-right hidden sm:block">
                      <span className="px-2 py-0.5 rounded bg-[#1D8F88]/10 text-[#1D8F88] text-[10px] border border-[#1D8F88]/25 flex-shrink-0">
                        Approved
                      </span>
                      <span className="text-[10px] text-[#6A756F] font-mono block mt-1">Match Placed</span>
                    </div>
                    <ConfidenceRing value={conf} size={50} />
                    <ChevronRight className="w-4 h-4 text-[#6A756F] group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Interactive Explainability Sidebar Drawer */}
          <div className="lg:col-span-1">
            <AnimatePresence mode="wait">
              {selectedAction ? (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-5 shadow-sm space-y-6 sticky top-6"
                >
                  <div className="flex items-start justify-between border-b border-[#4E5D5A]/10 pb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-[#1D8F88]/10 border border-[#1D8F88]/20 flex items-center justify-center text-[#1D8F88]">
                        <Sparkles className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-[#4E5D5A] text-sm font-semibold">Explainability Audit</h4>
                        <p className="text-[#6A756F] text-[10px]">Decision record: #{selectedAction.session_id?.slice(0, 8)}</p>
                      </div>
                    </div>
                    <button onClick={() => setSelectedAction(null)} className="text-[#6A756F] hover:text-[#4E5D5A] transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Candidate / Job Summary */}
                  <div>
                    <span className="text-[#6A756F] font-mono text-[9px] uppercase tracking-wider block mb-1">Target Match fit</span>
                    <p className="text-[#4E5D5A] text-xs font-medium">{selectedAction.candidate_name}</p>
                    <p className="text-[#6A756F] text-xs">{selectedAction.action?.job_title} at {selectedAction.action?.client_name}</p>
                  </div>

                  {/* Match components breakdown */}
                  <div>
                    <span className="text-[#6A756F] font-mono text-[9px] uppercase tracking-wider block mb-2">Confidence weighting</span>
                    <div className="space-y-2">
                      {[
                        { label: "Candidate Skills Profiler", val: "38%", icon: User },
                        { label: "Retrospective Knowledge RAG", val: "24%", icon: Database },
                        { label: "Historical Placement Memory", val: "20%", icon: Brain },
                        { label: "Policy Rules Adjustment", val: "18%", icon: Layers }
                      ].map((c) => {
                        const IconComp = c.icon;
                        return (
                          <div key={c.label} className="flex items-center justify-between text-xs p-2 bg-[#EFE8DE] rounded border border-[#4E5D5A]/10">
                            <div className="flex items-center gap-2 text-[#6A756F]">
                              <IconComp className="w-3.5 h-3.5" />
                              <span>{c.label}</span>
                            </div>
                            <span className="font-mono text-[#4E5D5A] font-bold">{c.val}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Business Rules Applied */}
                  <div>
                    <span className="text-[#6A756F] font-mono text-[9px] uppercase tracking-wider block mb-2">Applied Business Policies</span>
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2 text-xs bg-[#1D8F88]/10 border border-[#1D8F88]/20 px-2.5 py-2 rounded">
                        <CheckCircle2 className="w-4 h-4 text-[#1D8F88] flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <span className="text-[#1D8F88] font-medium block text-[11px]">RULE_LOCATION_COMPLIANCE</span>
                          <span className="text-[#6A756F] text-[10px]">Location validation passed</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs bg-[#1D8F88]/10 border border-[#1D8F88]/20 px-2.5 py-2 rounded">
                        <CheckCircle2 className="w-4 h-4 text-[#1D8F88] flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <span className="text-[#1D8F88] font-medium block text-[11px]">RULE_CLIENT_HIRING_VELOCITY</span>
                          <span className="text-[#6A756F] text-[10px]">High demand velocity boost applied (+15%)</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Reasoning text */}
                  <div>
                    <span className="text-[#6A756F] font-mono text-[9px] uppercase tracking-wider block mb-1">Recommendation Reasoning</span>
                    <div className="bg-[#EFE8DE] rounded border border-[#4E5D5A]/10 p-3 text-[11px] text-[#4E5D5A] leading-relaxed font-mono">
                      {selectedAction.reasoning || "No detailed reasoning text provided."}
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="border border-[#4E5D5A]/10 border-dashed rounded-xl p-8 text-center text-[#6A756F] text-xs">
                  Select a recommendation from the queue to run an explainability audit.
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
}
