"use client";
import { motion } from "framer-motion";
import type { ConfidenceBreakdown } from "@/types";

interface EvidenceCardsProps {
  breakdown: ConfidenceBreakdown;
  businessRuleTrace: string[];
  memoryTrace: string[];
}

interface EvidenceRowProps {
  label: string;
  weight: string;
  score: number;
  detail: string;
  delay?: number;
}

function EvidenceRow({ label, weight, score, detail, delay = 0 }: EvidenceRowProps) {
  const pct = Math.round(score * 100);
  const color = score >= 0.8 ? "bg-[#1D8F88]" : score >= 0.6 ? "bg-[#FFC94B]" : "bg-[#F17A7E]";
  const textColor = score >= 0.8 ? "text-[#1D8F88]" : score >= 0.6 ? "text-[#FFC94B]" : "text-[#F17A7E]";

  return (
    <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay }}
      className="space-y-1.5">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[#4E5D5A] text-xs font-medium">{label}</span>
          <span className="ml-2 text-[#6A756F]/60 text-xs font-mono">{weight}</span>
        </div>
        <span className={`text-xs font-mono font-bold ${textColor}`}>{pct}%</span>
      </div>
      <div className="h-1 bg-[#4E5D5A]/10 rounded-full overflow-hidden">
        <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 0.8, delay: delay + 0.2, ease: "easeOut" }}
          className={`h-full rounded-full ${color}`} />
      </div>
      <p className="text-[#6A756F]/80 text-xs">{detail}</p>
    </motion.div>
  );
}

export default function EvidenceCards({ breakdown, businessRuleTrace, memoryTrace }: EvidenceCardsProps) {
  const adj = breakdown.rule_adjustment;
  const ruleText = businessRuleTrace.length > 0
    ? businessRuleTrace[0]
    : adj > 0 ? `+${(adj * 100).toFixed(0)}% boost applied` : adj < 0 ? `${(adj * 100).toFixed(0)}% reduction applied` : "No adjustments applied";

  return (
    <div className="bg-[#EFE8DE] rounded-xl p-4 space-y-4 border border-[#4E5D5A]/10 shadow-inner">
      <p className="text-xs text-[#6A756F] font-mono uppercase tracking-wider">Evidence Chain</p>

      <EvidenceRow label="Candidate Fit" weight="35%" score={breakdown.candidate_fit_score} detail="Skill profiling & experience alignment" delay={0} />
      <EvidenceRow label="Enterprise Knowledge" weight="25%" score={breakdown.top_knowledge_score} detail="Interaction history, CRM, meeting notes" delay={0.05} />
      <EvidenceRow label="Planner Memory" weight="20%" score={breakdown.memory_score} detail={memoryTrace[3] || "Historical decision context"} delay={0.1} />
      <EvidenceRow label="Client Health" weight="10%" score={breakdown.client_health} detail="Account health & engagement metrics" delay={0.15} />
      <EvidenceRow label="Priority / Urgency" weight="10%" score={breakdown.priority_urgency_score} detail="Hiring urgency signal" delay={0.2} />

      {/* Business Rules */}
      <div className="pt-2 border-t border-[#4E5D5A]/10">
        <p className="text-xs font-semibold text-[#4E5D5A] mb-1">Business Rules</p>
        <p className="text-xs text-[#6A756F]">{ruleText}</p>
        {adj !== 0 && (
          <span className={`text-xs font-mono ${adj > 0 ? "text-[#1D8F88]" : "text-[#F17A7E]"}`}>
            Score adjustment: {adj > 0 ? "+" : ""}{(adj * 100).toFixed(1)}%
          </span>
        )}
      </div>

      {/* Final */}
      <div className="pt-2 border-t border-[#4E5D5A]/10 flex items-center justify-between">
        <span className="text-[#4E5D5A] text-xs font-semibold">Final Decision Confidence</span>
        <span className="text-[#4E5D5A] font-mono font-bold text-sm">
          {Math.round(breakdown.base_score * 100 + adj * 100)}%
        </span>
      </div>
    </div>
  );
}
