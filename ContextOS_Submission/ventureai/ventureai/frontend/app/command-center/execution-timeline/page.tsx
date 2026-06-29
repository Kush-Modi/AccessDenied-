"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { Calendar, Mail, FileText, MessageSquare, Building2, Filter } from "lucide-react";
import { cn, timeAgo } from "@/lib/utils";

const EVENT_TYPES = ["All", "Meeting", "CRM", "Email", "Note", "Placement"] as const;
type EventType = typeof EVENT_TYPES[number];

const MOCK_EVENTS = [
  { id: 1, type: "Meeting", title: "Initial Screening Call", subject: "Ananya Sharma", detail: "Discussed Python and cloud experience. Strong DevOps background confirmed.", timestamp: new Date(Date.now() - 1 * 86400000), icon: Calendar, color: "text-[#4A6163]", border: "border-[#4A6163]/20", bg: "bg-[#4A6163]/10" },
  { id: 2, type: "CRM", title: "TechCorp Account Update", subject: "TechCorp", detail: "Account health updated to 85%. High priority flag set by account manager.", timestamp: new Date(Date.now() - 2 * 86400000), icon: Building2, color: "text-[#1D8F88]", border: "border-[#1D8F88]/20", bg: "bg-[#1D8F88]/10" },
  { id: 3, type: "Email", title: "Candidate Follow-up", subject: "Divya Menon", detail: "Sent role details for Senior Data Engineer position at DataCo Inc.", timestamp: new Date(Date.now() - 3 * 86400000), icon: Mail, color: "text-[#1D8F88]", border: "border-[#1D8F88]/20", bg: "bg-[#1D8F88]/10" },
  { id: 4, type: "Note", title: "Recruiter Observation", subject: "Karthik Rajan", detail: "Candidate expressed interest in remote-only roles. Notice period: 30 days.", timestamp: new Date(Date.now() - 4 * 86400000), icon: FileText, color: "text-[#FFC94B]", border: "border-[#FFC94B]/20", bg: "bg-[#FFC94B]/10" },
  { id: 5, type: "Meeting", title: "Client Briefing", subject: "DataCo Inc.", detail: "Hiring manager outlined requirements for ML Engineer — urgency: critical.", timestamp: new Date(Date.now() - 5 * 86400000), icon: Calendar, color: "text-[#4A6163]", border: "border-[#4A6163]/20", bg: "bg-[#4A6163]/10" },
  { id: 6, type: "Placement", title: "Successful Placement", subject: "Ananya Sharma to TechCorp", detail: "Candidate formally accepted offer. Placement logged with outcome: success.", timestamp: new Date(Date.now() - 6 * 86400000), icon: MessageSquare, color: "text-[#1D8F88]", border: "border-[#1D8F88]/20", bg: "bg-[#1D8F88]/10" },
  { id: 7, type: "CRM", title: "FinTech Solutions Update", subject: "FinTech Solutions", detail: "Hiring freeze lifted. 3 new JDs opened. Re-activating pipeline.", timestamp: new Date(Date.now() - 7 * 86400000), icon: Building2, color: "text-[#1D8F88]", border: "border-[#1D8F88]/20", bg: "bg-[#1D8F88]/10" },
  { id: 8, type: "Email", title: "Interview Feedback", subject: "Rohan Kumar", detail: "Technical round passed. Awaiting final round scheduling with hiring manager.", timestamp: new Date(Date.now() - 8 * 86400000), icon: Mail, color: "text-[#1D8F88]", border: "border-[#1D8F88]/20", bg: "bg-[#1D8F88]/10" },
];

export default function ExecutionTimelinePage() {
  const [activeFilter, setActiveFilter] = useState<EventType>("All");

  const filtered = MOCK_EVENTS.filter(
    (e) => activeFilter === "All" || e.type === activeFilter
  );

  return (
    <div className="p-6 max-w-3xl bg-[#F7F5EF] text-[#4E5D5A] min-h-full">
      <div className="mb-6">
        <h1 className="text-[#4E5D5A] font-semibold text-lg">Execution Timeline</h1>
        <p className="text-[#6A756F] text-sm mt-0.5">Knowledge interactions across candidates and clients</p>
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-1.5 mb-8 flex-wrap">
        <Filter className="w-4 h-4 text-[#6A756F] mr-1" />
        {EVENT_TYPES.map((type) => (
          <button key={type} onClick={() => setActiveFilter(type)}
            className={cn("px-3 py-1 rounded-full text-xs font-medium transition-all",
              activeFilter === type
                ? "bg-[#1D8F88] text-[#F7F5EF]"
                : "bg-[#EFE8DE] border border-[#4E5D5A]/10 text-[#6A756F] hover:text-[#4E5D5A]")}>
            {type}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="relative">
        <div className="timeline-line bg-[#4E5D5A]/10" />
        <div className="space-y-0 pl-12">
          {filtered.map((event, i) => {
            const Icon = event.icon;
            return (
              <motion.div key={event.id}
                initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
                className="relative pb-6 last:pb-0">
                {/* Timeline dot */}
                <div className={cn("absolute -left-9 top-1 w-8 h-8 rounded-full border flex items-center justify-center", event.border, event.bg)}>
                  <Icon className={cn("w-4 h-4", event.color)} />
                </div>

                {/* Card */}
                <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl hover:border-[#4E5D5A]/25 p-4 transition-all shadow-sm">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <div>
                      <span className={cn("text-[10px] font-mono uppercase tracking-wider", event.color)}>{event.type}</span>
                      <h3 className="text-[#4E5D5A] text-sm font-semibold">{event.title}</h3>
                      <p className="text-[#6A756F] text-xs">{event.subject}</p>
                    </div>
                    <span className="text-xs text-[#6A756F]/65 font-mono flex-shrink-0">{timeAgo(event.timestamp)}</span>
                  </div>
                  <p className="text-[#6A756F] text-xs leading-relaxed mt-2">{event.detail}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
