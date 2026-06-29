"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import useSWR from "swr";
import api from "@/lib/api";
import { TrendingUp, TrendingDown, Users, Zap, Brain, Database, Clock, CheckCircle } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string;
  sub: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  icon: React.ElementType;
  delay?: number;
  color?: string;
}

function useCountUp(target: number, duration = 1200) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setVal(target); clearInterval(timer); }
      else setVal(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return val;
}

function Sparkline({ data }: { data: number[] }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 80, h = 28;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * h}`).join(" ");
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <polyline points={pts} fill="none" stroke="#1D8F88" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function MetricCard({ label, value, sub, trend = "neutral", trendValue, icon: Icon, delay = 0, color = "text-[#1D8F88]" }: MetricCardProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
      className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 hover:border-[#4E5D5A]/25 rounded-xl transition-all shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center border border-[#4E5D5A]/10 bg-[#EFE8DE]`}>
          <Icon className={`w-4 h-4 ${color}`} />
        </div>
        <Sparkline data={[40, 55, 48, 70, 62, 78, 85, 72, 88, 92]} />
      </div>
      <div className="count-up">
        <p className="text-2xl font-bold text-[#4E5D5A] font-mono">{value}</p>
      </div>
      <p className="text-[#6A756F] text-xs mt-0.5">{label}</p>
      <div className="flex items-center gap-1.5 mt-2">
        {trend === "up" && <TrendingUp className="w-3 h-3 text-[#1D8F88]" />}
        {trend === "down" && <TrendingDown className="w-3 h-3 text-[#F17A7E]" />}
        {trendValue && (
          <span className={`text-xs font-mono ${trend === "up" ? "text-[#1D8F88]" : trend === "down" ? "text-[#F17A7E]" : "text-[#6A756F]"}`}>
            {trendValue}
          </span>
        )}
        <span className="text-[#6A756F]/60 text-xs">{sub}</span>
      </div>
    </motion.div>
  );
}

export default function AnalyticsPage() {
  const { data: nbaData } = useSWR("nba-queue", api.getNBAQueue);
  const { data: candidates } = useSWR("candidates", api.getCandidates);
  const { data: clients } = useSWR("clients", api.getClients);

  const approved = nbaData?.actions.length || 0;
  const total = candidates?.length || 0;
  const accuracy = total > 0 ? Math.round((approved / total) * 100) : 0;

  return (
    <div className="p-6 bg-[#F7F5EF] text-[#4E5D5A] min-h-full">
      <div className="mb-6">
        <h1 className="text-[#4E5D5A] font-semibold text-lg">Decision Analytics</h1>
        <p className="text-[#6A756F] text-sm mt-0.5">Intelligence performance metrics</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard label="Recommendation Accuracy" value={`${accuracy}%`} sub="approved / analyzed" trend="up" trendValue="+12%" icon={CheckCircle} delay={0} color="text-[#1D8F88]" />
        <MetricCard label="Business Rule Hit Rate" value="68%" sub="rules triggered per run" trend="up" trendValue="+5%" icon={Zap} delay={0.08} color="text-[#FFC94B]" />
        <MetricCard label="Knowledge Items Retrieved" value="4.2" sub="avg per analysis" trend="up" trendValue="+0.8" icon={Database} delay={0.16} color="text-[#4A6163]" />
        <MetricCard label="Avg Decision Time" value="~8s" sub="agent runtime" trend="down" trendValue="-2s" icon={Clock} delay={0.24} color="text-[#1D8F88]" />
        <MetricCard label="Candidates in Pipeline" value={String(total)} sub="total candidates" trend="neutral" icon={Users} delay={0.32} color="text-[#4A6163]" />
        <MetricCard label="Active Client Accounts" value={String(clients?.length || 0)} sub="total clients" trend="neutral" icon={Brain} delay={0.4} color="text-[#1D8F88]" />
        <MetricCard label="Approved Placements" value={String(approved)} sub="in NBA queue" trend="up" trendValue={`+${approved}`} icon={CheckCircle} delay={0.48} color="text-[#1D8F88]" />
        <MetricCard label="Planner Memory Usage" value="12" sub="feedback records" trend="up" trendValue="+3" icon={Brain} delay={0.56} color="text-[#F17A7E]" />
      </div>

      {/* Top triggered rules */}
      <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm">
        <h2 className="text-[#4E5D5A] font-medium text-sm mb-4">Top Triggered Business Rules</h2>
        <div className="space-y-3">
          {[
            { name: "High Priority Client", hits: 24, action: "increase_confidence", pct: 80 },
            { name: "Urgent Hiring Needed", hits: 18, action: "increase_confidence", pct: 60 },
            { name: "Low Client Health", hits: 12, action: "decrease_confidence", pct: 40 },
            { name: "Long Notice Period", hits: 8, action: "decrease_confidence", pct: 27 },
            { name: "Missing Mandatory Skills", hits: 6, action: "decrease_confidence", pct: 20 },
          ].map((rule, i) => (
            <motion.div key={rule.name} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
              className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#6A756F]">{rule.name}</span>
                <div className="flex items-center gap-2">
                  <span className={`font-mono ${rule.action.includes("increase") ? "text-[#1D8F88]" : "text-[#F17A7E]"}`}>
                    {rule.action.includes("increase") ? "↑ boost" : "↓ reduce"}
                  </span>
                  <span className="text-[#6A756F]/60">{rule.hits} hits</span>
                </div>
              </div>
              <div className="h-1 bg-[#4E5D5A]/10 rounded-full overflow-hidden">
                <motion.div initial={{ width: 0 }} animate={{ width: `${rule.pct}%` }} transition={{ duration: 0.7, delay: i * 0.07 + 0.3 }}
                  className={`h-full rounded-full ${rule.action.includes("increase") ? "bg-[#1D8F88]" : "bg-[#F17A7E]"}`} />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
