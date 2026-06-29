"use client";
import { useState, useEffect } from "react";
import useSWR from "swr";
import api from "@/lib/api";
import { cn, getInitials } from "@/lib/utils";
import { motion } from "framer-motion";
import { Building2, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";

function HealthRing({ value }: { value: number }) {
  const size = 56, sw = 5;
  const r = (size - sw * 2) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (value / 100) * circ;
  const color = value >= 70 ? "#1D8F88" : value >= 40 ? "#FFC94B" : "#F17A7E";
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#4E5D5A" strokeOpacity="0.1" strokeWidth={sw} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={sw}
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 1s ease" }} />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-mono font-bold" style={{ color }}>{value}%</span>
      </div>
    </div>
  );
}

function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton bg-[#4E5D5A]/10 animate-pulse", className)} />;
}

export default function ClientsPage() {
  const [isAddingClient, setIsAddingClient] = useState(false);
  const [isAddingJob, setIsAddingJob] = useState(false);
  const [clientForm, setClientForm] = useState({
    name: "",
    industry: "Technology",
    account_health: 90,
  });
  const [jobForm, setJobForm] = useState({
    client_id: "",
    title: "",
    skills: "",
    location: "",
    salary_range: "20-30 LPA",
    description_text: "",
  });

  const { data: clients, isLoading, mutate } = useSWR("clients", api.getClients);

  // Set default client_id when clients load or modal opens
  useEffect(() => {
    if (clients && clients.length > 0 && !jobForm.client_id) {
      setJobForm((prev) => ({ ...prev, client_id: clients[0].id }));
    }
  }, [clients, jobForm.client_id]);

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createClient(clientForm);
      setIsAddingClient(false);
      setClientForm({ name: "", industry: "Technology", account_health: 90 });
      mutate();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to add client");
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const skillsArray = jobForm.skills.split(",").map((s) => s.trim()).filter(Boolean);
      await api.createJob({
        client_id: jobForm.client_id,
        title: jobForm.title,
        required_skills: skillsArray,
        location: jobForm.location,
        salary_range: jobForm.salary_range,
        description_text: jobForm.description_text,
      });
      setIsAddingJob(false);
      setJobForm({
        client_id: clients?.[0]?.id || "",
        title: "",
        skills: "",
        location: "",
        salary_range: "20-30 LPA",
        description_text: "",
      });
      mutate();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to add job opening");
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 bg-[#F7F5EF] min-h-full">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 space-y-3 rounded-xl">
            <div className="flex items-center gap-3">
              <Skeleton className="w-11 h-11 rounded-xl" />
              <div className="flex-1 space-y-2"><Skeleton className="h-4 w-32 rounded" /><Skeleton className="h-3 w-20 rounded" /></div>
              <Skeleton className="w-14 h-14 rounded-full" />
            </div>
            <Skeleton className="h-3 w-full rounded" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="p-6 bg-[#F7F5EF] text-[#4E5D5A] min-h-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-[#4E5D5A] font-semibold text-lg">Client Intelligence</h1>
          <p className="text-[#6A756F] text-sm mt-0.5">{clients?.length || 0} client accounts</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsAddingClient(true)}
            className="bg-[#1D8F88] hover:bg-[#1D8F88]/80 text-[#F7F5EF] text-sm font-medium px-4 py-2 rounded-full transition-colors"
          >
            Add Client Firm
          </button>
          <button
            onClick={() => {
              if (clients && clients.length > 0) {
                setJobForm((prev) => ({ ...prev, client_id: clients[0].id }));
              }
              setIsAddingJob(true);
            }}
            className="bg-[#F4F1EA] border border-[#4E5D5A]/10 text-[#4E5D5A] hover:bg-[#EFE8DE] text-sm font-medium px-4 py-2 rounded-full transition-colors"
          >
            Add Job Opening
          </button>
        </div>
      </div>

      {/* Add Client Modal */}
      {isAddingClient && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/15 rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <h2 className="text-[#4E5D5A] text-base font-semibold">Add Client Firm</h2>
            <form onSubmit={handleCreateClient} className="space-y-4">
              <div>
                <label className="block text-xs text-[#6A756F] mb-1">Firm Name *</label>
                <input
                  required
                  value={clientForm.name}
                  onChange={(e) => setClientForm({ ...clientForm, name: e.target.value })}
                  className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                  placeholder="e.g. NetSecure, TechCorp"
                />
              </div>
              <div>
                <label className="block text-xs text-[#6A756F] mb-1">Industry</label>
                <input
                  value={clientForm.industry}
                  onChange={(e) => setClientForm({ ...clientForm, industry: e.target.value })}
                  className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                  placeholder="e.g. Technology, Finance"
                />
              </div>
              <div>
                <label className="block text-xs text-[#6A756F] mb-1">Initial Account Health (0-100)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={clientForm.account_health}
                  onChange={(e) => setClientForm({ ...clientForm, account_health: Number(e.target.value) })}
                  className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                />
              </div>
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddingClient(false)}
                  className="px-4 py-2 bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded-full text-[#6A756F] text-sm hover:text-[#4E5D5A]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#1D8F88] text-[#F7F5EF] rounded-full text-sm hover:bg-[#1D8F88]/80"
                >
                  Create Client
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Job Opening Modal */}
      {isAddingJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/15 rounded-xl p-6 w-full max-w-lg space-y-4 shadow-xl">
            <h2 className="text-[#4E5D5A] text-base font-semibold">Add Job Opening</h2>
            <form onSubmit={handleCreateJob} className="space-y-4">
              <div>
                <label className="block text-xs text-[#6A756F] mb-1">Select Client Firm *</label>
                <select
                  required
                  value={jobForm.client_id}
                  onChange={(e) => setJobForm({ ...jobForm, client_id: e.target.value })}
                  className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                >
                  {clients?.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-[#6A756F] mb-1">Job Title *</label>
                  <input
                    required
                    value={jobForm.title}
                    onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })}
                    className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    placeholder="e.g. Senior Security Engineer"
                  />
                </div>
                <div>
                  <label className="block text-xs text-[#6A756F] mb-1">Location *</label>
                  <input
                    required
                    value={jobForm.location}
                    onChange={(e) => setJobForm({ ...jobForm, location: e.target.value })}
                    className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    placeholder="e.g. Remote, Bangalore"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-[#6A756F] mb-1">Salary Range</label>
                  <input
                    value={jobForm.salary_range}
                    onChange={(e) => setJobForm({ ...jobForm, salary_range: e.target.value })}
                    className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    placeholder="e.g. 20-30 LPA, $130k-150k"
                  />
                </div>
                <div>
                  <label className="block text-xs text-[#6A756F] mb-1">Required Skills (comma separated) *</label>
                  <input
                    required
                    value={jobForm.skills}
                    onChange={(e) => setJobForm({ ...jobForm, skills: e.target.value })}
                    className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    placeholder="Python, AWS, Terraform"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs text-[#6A756F] mb-1">Job Description</label>
                <textarea
                  rows={4}
                  value={jobForm.description_text}
                  onChange={(e) => setJobForm({ ...jobForm, description_text: e.target.value })}
                  className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                  placeholder="Enter details about responsibilities, tools, and background requirements..."
                />
              </div>
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddingJob(false)}
                  className="px-4 py-2 bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded-full text-[#6A756F] text-sm hover:text-[#4E5D5A]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#1D8F88] text-[#F7F5EF] rounded-full text-sm hover:bg-[#1D8F88]/80"
                >
                  Post Job Opening
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {clients?.map((client, i) => (
          <motion.div key={client.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
            className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-5 hover:border-[#4E5D5A]/25 transition-all shadow-sm">
            <div className="flex items-start gap-3 mb-4">
              <div className="w-11 h-11 rounded-xl bg-[#4A6163] flex items-center justify-center text-[#F7F5EF] font-bold flex-shrink-0">
                {getInitials(client.name)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[#4E5D5A] font-medium text-sm">{client.name}</p>
                <p className="text-[#6A756F] text-xs">{client.industry || "Enterprise"}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  {client.hiring_freeze ? (
                    <span className="flex items-center gap-1 text-xs text-[#F17A7E]"><AlertCircle className="w-3 h-3" />Freeze</span>
                  ) : client.high_priority ? (
                    <span className="flex items-center gap-1 text-xs text-[#1D8F88]"><TrendingUp className="w-3 h-3" />High Priority</span>
                  ) : (
                    <span className="flex items-center gap-1 text-xs text-[#1D8F88]"><CheckCircle className="w-3 h-3" />Active</span>
                  )}
                </div>
              </div>
              <HealthRing value={client.account_health} />
            </div>
            <div className="h-px bg-[#4E5D5A]/10 mb-3" />
            <div className="flex items-center gap-4 text-xs text-[#6A756F]">
              <span className="flex items-center gap-1"><Building2 className="w-3 h-3" />{client.location || "Remote"}</span>
              <span className="ml-auto font-mono">Health: {client.account_health}%</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
