"use client";

import { use, useState } from "react";
import { motion } from "framer-motion";
import useSWR from "swr";
import { notFound } from "next/navigation";
import api from "@/lib/api";
import { cn, getInitials } from "@/lib/utils";
import { 
  MapPin, 
  Briefcase, 
  Mail, 
  Phone, 
  Award, 
  School, 
  FolderGit, 
  CheckCircle2,
  Sparkles,
  Zap,
  Check
} from "lucide-react";

function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton bg-[#4E5D5A]/10 animate-pulse", className)} />;
}

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function CandidateDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const [activeTab, setActiveTab] = useState<string>("Overview");

  const { data: candidates, isLoading } = useSWR("candidates", api.getCandidates);
  const candidate = candidates?.find((c) => c.id === id);

  if (!isLoading && candidates && !candidate) notFound();
  if (isLoading) {
    return (
      <div className="p-6 space-y-4 text-[#4E5D5A]">
        <div className="flex items-center gap-4">
          <Skeleton className="w-16 h-16 rounded-2xl" />
          <div className="space-y-2"><Skeleton className="h-5 w-40 rounded" /><Skeleton className="h-4 w-32 rounded" /></div>
        </div>
        <Skeleton className="h-10 w-full rounded-lg" />
        <Skeleton className="h-48 w-full rounded-lg" />
      </div>
    );
  }
  if (!candidate) return null;

  // Try to parse structured JSON from resume_text
  let parsedResume: any = null;
  try {
    if (candidate.resume_text && candidate.resume_text.trim().startsWith("{")) {
      parsedResume = JSON.parse(candidate.resume_text);
    }
  } catch (e) {
    // Fallback to null
  }

  // Construct dynamic tabs list
  const tabsList = ["Overview"];
  if (parsedResume) {
    if (parsedResume.work_experience?.length > 0) tabsList.push("Experience");
    if (parsedResume.education?.length > 0) tabsList.push("Education");
    if (parsedResume.projects?.length > 0) tabsList.push("Projects");
  }
  tabsList.push("Skills", "Timeline", "Memory", "Recommendations");

  return (
    <div className="p-6 text-[#4E5D5A] bg-[#F7F5EF] min-h-full">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-start gap-5 mb-6">
        <div className="w-16 h-16 rounded-2xl bg-[#4A6163] flex items-center justify-center text-[#F7F5EF] font-bold text-xl flex-shrink-0">
          {getInitials(candidate.name)}
        </div>
        <div>
          <h1 className="text-[#4E5D5A] font-bold text-xl">{candidate.name}</h1>
          <p className="text-[#6A756F]">{candidate.current_position}</p>
          <div className="flex items-center gap-4 mt-2 text-xs text-[#6A756F]/80">
            <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" />{candidate.experience_years} years</span>
            <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{candidate.location}</span>
          </div>
        </div>
      </motion.div>

      <div className="flex items-center gap-1 mb-6 border-b border-[#4E5D5A]/10 overflow-x-auto whitespace-nowrap scrollbar-none">
        {tabsList.map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={cn("px-4 py-2 text-sm font-medium transition-all border-b-2 -mb-px",
              activeTab === tab ? "border-[#1D8F88] text-[#1D8F88]" : "border-transparent text-[#6A756F] hover:text-[#4E5D5A]")}>
            {tab}
          </button>
        ))}
      </div>

      <motion.div key={activeTab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
        {activeTab === "Overview" && (
          <div className="space-y-4 max-w-2xl">
            <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl shadow-sm space-y-4">
              <h2 className="text-[#4E5D5A] font-semibold text-sm">Resume Summary</h2>
              <p className="text-[#6A756F] text-sm leading-relaxed">
                {parsedResume ? parsedResume.summary : (candidate.resume_text || "No resume summary available.")}
              </p>
              
              {parsedResume && (
                <div className="pt-4 border-t border-[#4E5D5A]/10 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-[#6A756F]">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-[#1D8F88]" />
                    <span>{parsedResume.email || candidate.email || "No email available"}</span>
                  </div>
                  {parsedResume.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-[#1D8F88]" />
                      <span>{parsedResume.phone}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-[#1D8F88]" />
                    <span>{parsedResume.location || candidate.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-[#1D8F88]" />
                    <span>Total Experience: {parsedResume.experience_years || candidate.experience_years} years</span>
                  </div>
                </div>
              )}

              {!parsedResume && (
                <div className="mt-4 pt-4 border-t border-[#4E5D5A]/10 grid grid-cols-2 gap-4 text-sm">
                  <div><span className="text-[#6A756F]/70 text-xs">Experience</span><p className="text-[#4E5D5A] mt-0.5">{candidate.experience_years} years</p></div>
                  <div><span className="text-[#6A756F]/70 text-xs">Location</span><p className="text-[#4E5D5A] mt-0.5">{candidate.location}</p></div>
                  <div><span className="text-[#6A756F]/70 text-xs">Position</span><p className="text-[#4E5D5A] mt-0.5">{candidate.current_position}</p></div>
                  <div><span className="text-[#6A756F]/70 text-xs">Status</span><p className="text-[#1D8F88] mt-0.5">Available</p></div>
                </div>
              )}
            </div>

            {parsedResume?.achievements?.length > 0 && (
              <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl shadow-sm space-y-3">
                <h2 className="text-[#4E5D5A] font-semibold text-sm flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-[#FFC94B]" />
                  Achievements &amp; Awards
                </h2>
                <ul className="space-y-2">
                  {parsedResume.achievements.map((ach: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2.5 text-sm text-[#6A756F] leading-relaxed">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#1D8F88] mt-1.5 flex-shrink-0" />
                      <span>{ach}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === "Experience" && parsedResume && (
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm space-y-6">
            <h2 className="text-[#4E5D5A] font-semibold text-sm flex items-center gap-1.5">
              <Briefcase className="w-4 h-4 text-[#1D8F88]" />
              Work Experience
            </h2>
            {parsedResume.work_experience?.length > 0 ? (
              <div className="relative border-l border-[#4E5D5A]/10 pl-5 ml-2.5 space-y-6">
                {parsedResume.work_experience.map((work: any, idx: number) => (
                  <div key={idx} className="relative">
                    <div className="absolute -left-[26px] top-1.5 w-3.5 h-3.5 rounded-full border border-[#1D8F88] bg-[#F4F1EA] flex items-center justify-center">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#1D8F88]" />
                    </div>
                    <div>
                      <h3 className="text-[#4E5D5A] font-bold text-sm">{work.job_title}</h3>
                      <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-[#6A756F] font-medium mt-0.5">
                        <span className="text-[#1D8F88]">{work.organization}</span>
                        <span>•</span>
                        <span>{work.dates}</span>
                      </div>
                      {work.description && (
                        <p className="text-xs text-[#6A756F] mt-2 leading-relaxed whitespace-pre-line">{work.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#6A756F]">No work experience details available.</p>
            )}
          </div>
        )}

        {activeTab === "Education" && parsedResume && (
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm space-y-5">
            <h2 className="text-[#4E5D5A] font-semibold text-sm flex items-center gap-1.5">
              <School className="w-4 h-4 text-[#1D8F88]" />
              Education &amp; Credentials
            </h2>
            {parsedResume.education?.length > 0 ? (
              <div className="space-y-4">
                {parsedResume.education.map((edu: any, idx: number) => (
                  <div key={idx} className="border-b border-[#4E5D5A]/5 pb-3.5 last:border-0 last:pb-0">
                    <h3 className="text-[#4E5D5A] font-bold text-sm">
                      {edu.degree || "Degree Details"} {edu.major ? `in ${edu.major}` : ""}
                    </h3>
                    <div className="flex flex-wrap items-center justify-between gap-2 mt-1 text-xs text-[#6A756F]">
                      <span className="font-medium text-[#4E5D5A]/80">{edu.organization}</span>
                      <span>{edu.dates}</span>
                    </div>
                    {edu.gpa && (
                      <div className="mt-1.5 inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[#1D8F88]/10 text-[10px] font-mono text-[#1D8F88] font-bold">
                        Grade: {edu.gpa}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#6A756F]">No education details available.</p>
            )}
          </div>
        )}

        {activeTab === "Projects" && parsedResume && (
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm space-y-5">
            <h2 className="text-[#4E5D5A] font-semibold text-sm flex items-center gap-1.5">
              <FolderGit className="w-4 h-4 text-[#1D8F88]" />
              Projects
            </h2>
            {parsedResume.projects?.length > 0 ? (
              <div className="space-y-4">
                {parsedResume.projects.map((proj: any, idx: number) => (
                  <div key={idx} className="border-b border-[#4E5D5A]/5 pb-3.5 last:border-0 last:pb-0">
                    <h3 className="text-[#4E5D5A] font-bold text-sm">{proj.title}</h3>
                    {proj.description && (
                      <p className="text-xs text-[#6A756F] mt-1 leading-relaxed">{proj.description}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#6A756F]">No project details available.</p>
            )}
          </div>
        )}

        {activeTab === "Skills" && (
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm">
            <h2 className="text-[#4E5D5A] font-semibold text-sm mb-4">Skill Profile — {candidate.skills?.length} skills</h2>
            <div className="flex flex-wrap gap-2">
              {candidate.skills?.map((skill, i) => (
                <motion.span key={skill} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.04 }}
                  className="px-3 py-1.5 rounded-lg text-sm border bg-[#EFE8DE] border-[#4E5D5A]/10 text-[#4E5D5A]">{skill}</motion.span>
              ))}
            </div>
          </div>
        )}
        {activeTab === "Timeline" && (
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm">
            <h2 className="text-[#4E5D5A] font-semibold text-sm mb-4">Knowledge Interactions</h2>
            <p className="text-[#6A756F] text-sm">Knowledge timeline is populated during agent analysis via Hybrid Retrieval.</p>
            <p className="text-[#6A756F]/70 text-xs mt-2 font-mono">Run Agent on this candidate to see interaction history.</p>
          </div>
        )}
        {activeTab === "Memory" && (
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm">
            <h2 className="text-[#4E5D5A] font-semibold text-sm mb-4">Planner Memory</h2>
            <p className="text-[#6A756F] text-sm">Memory context is loaded from Planner Memory during analysis.</p>
            <div className="mt-4 p-3 bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded-lg font-mono text-xs space-y-1">
              <p className="text-[#6A756F]">Candidate ID: {candidate.id}</p>
              <p className="text-[#6A756F]/70">Run analysis to compute memory score and feedback history.</p>
            </div>
          </div>
        )}
        {activeTab === "Recommendations" && (
          <div className="bg-[#F4F1EA] border border-[#4E5D5A]/10 p-5 rounded-xl max-w-2xl shadow-sm">
            <h2 className="text-[#4E5D5A] font-semibold text-sm mb-4">AI Recommendations</h2>
            <p className="text-[#6A756F] text-sm">Go to Command Center → Select this candidate → Run Agent to generate recommendations.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
