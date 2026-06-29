"use client";
import { Settings, Server, Database, Brain, Shield } from "lucide-react";

const CONFIG_SECTIONS = [
  {
    title: "API Configuration",
    icon: Server,
    items: [
      { label: "Backend URL", value: "http://127.0.0.1:8000", type: "text" },
      { label: "Polling Interval (NBA Queue)", value: "5000ms", type: "text" },
      { label: "Health Check Interval", value: "30000ms", type: "text" },
    ],
  },
  {
    title: "Decision Weights",
    icon: Brain,
    items: [
      { label: "Candidate Fit Score", value: "35%", type: "range" },
      { label: "Enterprise Knowledge (RAG)", value: "25%", type: "range" },
      { label: "Planner Memory", value: "20%", type: "range" },
      { label: "Client Health", value: "10%", type: "range" },
      { label: "Priority / Urgency", value: "10%", type: "range" },
    ],
  },
  {
    title: "Retrieval Configuration",
    icon: Database,
    items: [
      { label: "Similarity Threshold", value: "0.75", type: "text" },
      { label: "Top K Results", value: "5", type: "text" },
      { label: "Embedding Model", value: "pgvector (Supabase)", type: "text" },
    ],
  },
  {
    title: "Business Rules",
    icon: Shield,
    items: [
      { label: "Active Rules", value: "12 / 12", type: "text" },
      { label: "Rules Source", value: "rules.yaml (loaded at startup)", type: "text" },
    ],
  },
];

export default function SettingsPage() {
  return (
    <div className="p-6 max-w-2xl bg-[#F7F5EF] text-[#4E5D5A] min-h-full">
      <div className="mb-6 flex items-center gap-3">
        <Settings className="w-5 h-5 text-[#6A756F]" />
        <h1 className="text-[#4E5D5A] font-semibold text-lg">Platform Configuration</h1>
      </div>
      <div className="space-y-6">
        {CONFIG_SECTIONS.map((section) => {
          const Icon = section.icon;
          return (
            <div key={section.title} className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl overflow-hidden shadow-sm">
              <div className="flex items-center gap-2 px-5 py-3 border-b border-[#4E5D5A]/10">
                <Icon className="w-4 h-4 text-[#6A756F]" />
                <h2 className="text-[#4E5D5A] text-sm font-semibold">{section.title}</h2>
              </div>
              <div className="divide-y divide-[#4E5D5A]/10">
                {section.items.map((item) => (
                  <div key={item.label} className="flex items-center justify-between px-5 py-3 hover:bg-[#EFE8DE]/50 transition-colors">
                    <span className="text-[#6A756F] text-sm">{item.label}</span>
                    <span className="text-[#4E5D5A] text-sm font-mono">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
        <p className="text-[#6A756F]/65 text-xs font-mono">
          Configuration is loaded from the FastAPI backend and local environment. Modifying these values requires restarting the server.
        </p>
      </div>
    </div>
  );
}
