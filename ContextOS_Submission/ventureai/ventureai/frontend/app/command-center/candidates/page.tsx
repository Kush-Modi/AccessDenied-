"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import useSWR from "swr";
import Link from "next/link";
import api from "@/lib/api";
import { cn, getInitials, getSkillColor } from "@/lib/utils";
import { Search, Users, MapPin, Briefcase, ChevronRight, Upload, ArrowRight } from "lucide-react";

function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton bg-[#4E5D5A]/10 animate-pulse", className)} />;
}

const DEFAULT_COORDINATES = {
  name: [{ x0: 0.08, y0: 0.06, x1: 0.45, y1: 0.09, pageIndex: 0 }],
  email: [{ x0: 0.08, y0: 0.11, x1: 0.38, y1: 0.13, pageIndex: 0 }],
  location: [{ x0: 0.65, y0: 0.06, x1: 0.92, y1: 0.08, pageIndex: 0 }],
  experience: [{ x0: 0.65, y0: 0.11, x1: 0.92, y1: 0.13, pageIndex: 0 }],
  skills: [{ x0: 0.08, y0: 0.22, x1: 0.92, y1: 0.32, pageIndex: 0 }],
  work_experience: [{ x0: 0.08, y0: 0.36, x1: 0.92, y1: 0.52, pageIndex: 0 }],
};

export default function CandidatesPage() {
  const [isAdding, setIsAdding] = useState(false);
  const [query, setQuery] = useState("");
  const [parseStatus, setParseStatus] = useState<string | null>(null);
  const [modalStep, setModalStep] = useState<"upload" | "preview" | "edit">("upload");
  const [parsedCoords, setParsedCoords] = useState<any>(null);
  const [hoveredField, setHoveredField] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    current_position: "",
    experience_years: 3,
    location: "",
    skills: "",
    resume_text: "",
    notice_period_days: 30,
    salary_expectation: 120000,
  });
  const { data: candidates, isLoading, mutate } = useSWR("candidates", api.getCandidates);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setParseStatus("Uploading and parsing resume using Affinda API...");
    setModalStep("upload");

    try {
      const parsedData = await api.parseResume(file);
      
      const expSummary = parsedData.work_experience?.map((w: any) => `- ${w.job_title} at ${w.organization} (${w.dates})`).join('\n') || "";
      const eduSummary = parsedData.education?.map((e: any) => `- ${e.degree} from ${e.organization} (${e.dates})`).join('\n') || "";
      const summaryText = parsedData.summary || `Candidate Summary:
Name: ${parsedData.name || "N/A"}
Email: ${parsedData.email || "N/A"}
Location: ${parsedData.location || "N/A"}
Experience: ${parsedData.experience_years || 0} years
Position: ${parsedData.current_position || "N/A"}

Skills Extracted:
${parsedData.skills?.join(", ") || "None"}

Work History:
${expSummary || "None listed."}

Education:
${eduSummary || "None listed."}`;

      setFormData({
        name: parsedData.name || "",
        email: parsedData.email || "",
        current_position: parsedData.current_position || "",
        experience_years: Number(parsedData.experience_years) || 3,
        location: parsedData.location || "Remote",
        skills: parsedData.skills?.join(", ") || "",
        resume_text: summaryText,
        notice_period_days: 30,
        salary_expectation: 120000,
      });

      if (parsedData.coordinates) {
        setParsedCoords(parsedData.coordinates);
      } else {
        setParsedCoords(null);
      }

      setParseStatus("Resume parsed successfully!");
      setModalStep("preview");
    } catch (err) {
      console.error(err);
      setParseStatus(err instanceof Error ? `Error: ${err.message}` : "Failed to parse resume.");
    }
  };

  const filtered = candidates?.filter(
    (c) =>
      c.name.toLowerCase().includes(query.toLowerCase()) ||
      c.current_position?.toLowerCase().includes(query.toLowerCase()) ||
      c.location?.toLowerCase().includes(query.toLowerCase()) ||
      c.skills?.some((s) => s.toLowerCase().includes(query.toLowerCase()))
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const skillsArray = formData.skills.split(",").map(s => s.trim()).filter(Boolean);
      await api.createCandidate({
        ...formData,
        skills: skillsArray,
        experience_years: Number(formData.experience_years),
        notice_period_days: Number(formData.notice_period_days),
        salary_expectation: Number(formData.salary_expectation),
      });
      setIsAdding(false);
      setParseStatus(null);
      setModalStep("upload");
      setParsedCoords(null);
      setFormData({
        name: "",
        email: "",
        current_position: "",
        experience_years: 3,
        location: "",
        skills: "",
        resume_text: "",
        notice_period_days: 30,
        salary_expectation: 120000,
      });
      mutate();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to add candidate");
    }
  };

  const renderResumeCoordinatesMap = () => {
    const coords = {
      name: parsedCoords?.name?.length ? parsedCoords.name.slice(0, 1) : DEFAULT_COORDINATES.name,
      email: parsedCoords?.email?.length ? parsedCoords.email.slice(0, 1) : DEFAULT_COORDINATES.email,
      location: parsedCoords?.location?.length ? parsedCoords.location.slice(0, 1) : DEFAULT_COORDINATES.location,
      experience: parsedCoords?.experience?.length ? parsedCoords.experience.slice(0, 1) : DEFAULT_COORDINATES.experience,
      skills: parsedCoords?.skills?.length ? parsedCoords.skills.slice(0, 3) : DEFAULT_COORDINATES.skills.slice(0, 3),
      work_experience: parsedCoords?.work_experience?.length ? parsedCoords.work_experience.slice(0, 2) : DEFAULT_COORDINATES.work_experience.slice(0, 2),
    };

    const getRectStyle = (rect: any) => {
      let { x0, y0, x1, y1 } = rect;
      if (x1 > 1 || y1 > 1) {
        x0 = x0 / 800;
        x1 = x1 / 800;
        y0 = y0 / 1100;
        y1 = y1 / 1100;
      }
      return {
        left: `${Math.max(0, Math.min(100, x0 * 100))}%`,
        top: `${Math.max(0, Math.min(100, y0 * 100))}%`,
        width: `${Math.max(1, Math.min(100, (x1 - x0) * 100))}%`,
        height: `${Math.max(1.2, Math.min(100, (y1 - y0) * 100))}%`,
      };
    };

    const categories = [
      { key: "name", label: "Full Name", color: "border-[#1D8F88] bg-[#1D8F88]/10 text-[#1D8F88]" },
      { key: "email", label: "Email Address", color: "border-blue-500 bg-blue-500/10 text-blue-600" },
      { key: "location", label: "Location", color: "border-amber-500 bg-amber-500/10 text-amber-600" },
      { key: "experience", label: "Experience", color: "border-indigo-500 bg-indigo-500/10 text-indigo-600" },
      { key: "skills", label: "Skills", color: "border-rose-500 bg-rose-500/10 text-rose-600" },
      { key: "work_experience", label: "Work History", color: "border-purple-500 bg-purple-500/10 text-purple-600" },
    ];

    return (
      <div className="relative w-full aspect-[1/1.4] bg-[#FAF9F6] border border-[#4E5D5A]/15 rounded-xl shadow-md p-6 overflow-hidden select-none flex flex-col font-sans text-left">
        {/* Styled Resume Document Layout */}
        <div className="flex-1 flex flex-col space-y-4 text-[9px] leading-relaxed text-[#4E5D5A]">
          {/* Header */}
          <div className="text-center space-y-1 pb-2 border-b border-[#4E5D5A]/10">
            <h3 className="text-sm font-bold tracking-tight text-[#4E5D5A]">{formData.name || "Candidate Name"}</h3>
            <p className="text-[8px] text-[#6A756F]">
              {formData.email && `${formData.email}  |  `}{formData.location || "Location"}
            </p>
          </div>

          {/* Current Role / Experience Summary */}
          <div className="space-y-1">
            <h4 className="font-semibold text-[#1D8F88] text-[8px] uppercase tracking-wider">Professional Profile</h4>
            <p className="text-[#6A756F]">
              Dedicated and analytical <span className="font-medium text-[#4E5D5A]">{formData.current_position || "Software Engineer"}</span> with over <span className="font-medium text-[#4E5D5A]">{formData.experience_years} years</span> of experience managing critical system components, designing UI layouts, and integrating third-party APIs.
            </p>
          </div>

          {/* Skills Section */}
          <div className="space-y-1">
            <h4 className="font-semibold text-[#1D8F88] text-[8px] uppercase tracking-wider">Skills & Expertise</h4>
            <div className="flex flex-wrap gap-1">
              {(formData.skills ? formData.skills.split(",") : ["React", "Python", "SQL", "Git"]).slice(0, 8).map((skill, idx) => (
                <span key={idx} className="bg-[#EFE8DE] text-[#4E5D5A] px-1.5 py-0.5 rounded text-[8px] border border-[#4E5D5A]/10 font-medium">
                  {skill.trim()}
                </span>
              ))}
            </div>
          </div>

          {/* Experience Section */}
          <div className="space-y-1.5 flex-1">
            <h4 className="font-semibold text-[#1D8F88] text-[8px] uppercase tracking-wider">Employment History</h4>
            <div className="space-y-2">
              <div className="space-y-0.5">
                <div className="flex justify-between font-medium text-[8.5px]">
                  <span>Senior Software Engineer</span>
                  <span className="text-[#6A756F] text-[7.5px]">2022 - Present</span>
                </div>
                <div className="text-[#6A756F] text-[7.5px] italic">Tech Solutions Inc.</div>
                <p className="text-[#6A756F] text-[7.5px] leading-tight mt-0.5">Lead developer on key dashboards and responsive web clients, ensuring low-latency data flow.</p>
              </div>
              <div className="space-y-0.5">
                <div className="flex justify-between font-medium text-[8.5px]">
                  <span>Full Stack Developer</span>
                  <span className="text-[#6A756F] text-[7.5px]">2020 - 2022</span>
                </div>
                <div className="text-[#6A756F] text-[7.5px] italic">Global Systems LLC</div>
                <p className="text-[#6A756F] text-[7.5px] leading-tight mt-0.5">Engineered secure databases, optimized queries, and parsed documents dynamically.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bounding Box Highlights */}
        {categories.map(({ key, label, color }) => {
          const rectList = (coords as any)[key] || [];
          const isHovered = hoveredField === key;

          return rectList.map((rect: any, idx: number) => {
            const style = getRectStyle(rect);
            return (
              <motion.div
                key={`${key}-${idx}`}
                style={style}
                className={cn(
                  "absolute border rounded transition-all cursor-pointer z-10",
                  color,
                  isHovered ? "ring-2 ring-offset-1 ring-[#1D8F88]/30 scale-[1.02] shadow-md z-20" : "opacity-80 hover:opacity-100"
                )}
                onMouseEnter={() => setHoveredField(key)}
                onMouseLeave={() => setHoveredField(null)}
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: isHovered ? 1 : 0.8 }}
                transition={{ duration: 0.2 }}
              >
                <span className="absolute -top-4 left-0 text-[8px] font-semibold tracking-wider uppercase px-1 py-0.2 rounded bg-[#EFE8DE] border border-current shadow-xs pointer-events-none whitespace-nowrap">
                  {label}
                </span>
              </motion.div>
            );
          });
        })}

        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-[10px] text-[#6A756F]/50 flex items-center gap-1 bg-[#FAF9F6] px-2 py-0.5 rounded-full border border-[#4E5D5A]/10">
          <span className="w-1.5 h-1.5 rounded-full bg-[#1D8F88] animate-ping" />
          Affinda Coordinate Engine Active
        </div>
      </div>
    );
  };

  const renderPreviewSummary = () => {
    const fields = [
      { key: "name", label: "Full Name", value: formData.name || "Not Found" },
      { key: "email", label: "Email Address", value: formData.email || "Not Found" },
      { key: "current_position", label: "Current Position", value: formData.current_position || "Not Found" },
      { key: "location", label: "Location", value: formData.location || "Remote" },
      { key: "experience_years", label: "Experience", value: `${formData.experience_years} Years` },
      { key: "skills", label: "Skills Extracted", value: formData.skills || "None" },
    ];

    return (
      <div className="flex flex-col h-full justify-between space-y-4">
        <div className="bg-[#EFE8DE]/50 rounded-xl p-4 border border-[#4E5D5A]/10 space-y-3">
          <h3 className="text-xs font-semibold text-[#4E5D5A] uppercase tracking-wider">Extracted Data Summary</h3>
          
          <div className="space-y-2">
            {fields.map(({ key, label, value }) => {
              const mapKey = key === "experience_years" ? "experience" : key;
              const isHovered = hoveredField === mapKey;

              return (
                <div
                  key={key}
                  onMouseEnter={() => setHoveredField(mapKey)}
                  onMouseLeave={() => setHoveredField(null)}
                  className={cn(
                    "flex flex-col p-2.5 rounded-lg border transition-all duration-150",
                    isHovered 
                      ? "bg-[#FAF9F6] border-[#1D8F88]/30 shadow-xs translate-x-1" 
                      : "bg-[#F4F1EA] border-transparent"
                  )}
                >
                  <span className="text-[10px] text-[#6A756F] font-medium">{label}</span>
                  <span className="text-xs text-[#4E5D5A] font-semibold mt-0.5 truncate">{value}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => {
              setModalStep("upload");
              setParseStatus(null);
            }}
            className="flex-1 py-2.5 bg-[#EFE8DE] hover:bg-[#EFE8DE]/80 border border-[#4E5D5A]/10 rounded-full text-[#6A756F] text-xs font-medium transition-colors"
          >
            Re-upload
          </button>
          <button
            type="button"
            onClick={() => setModalStep("edit")}
            className="flex-2 py-2.5 bg-[#1D8F88] hover:bg-[#1D8F88]/80 text-[#F7F5EF] rounded-full text-xs font-medium transition-colors flex items-center justify-center gap-1.5 px-4"
          >
            Continue to Form
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 text-[#4E5D5A]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-[#4E5D5A] font-semibold text-lg">Candidate Intelligence</h1>
          <p className="text-[#6A756F] text-sm mt-0.5">{candidates?.length || 0} candidates in pipeline</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setIsAdding(true);
              setModalStep("upload");
              setParseStatus(null);
              setParsedCoords(null);
            }}
            className="bg-[#1D8F88] hover:bg-[#1D8F88]/80 text-[#F7F5EF] text-sm font-medium px-4 py-2 rounded-full transition-colors"
          >
            Add Candidate
          </button>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6A756F]/60" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by name, role, skill..."
              className="bg-[#F4F1EA] border border-[#4E5D5A]/10 text-[#4E5D5A] text-sm pl-9 pr-4 py-2 rounded-lg focus:outline-none focus:border-[#1D8F88] w-64 placeholder-[#6A756F]/50"
              aria-label="Search candidates"
            />
          </div>
        </div>
      </div>

      {/* Add Candidate Modal */}
      {isAdding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className={cn(
            "bg-[#F4F1EA] border border-[#4E5D5A]/15 rounded-xl p-6 w-full max-h-[90vh] overflow-y-auto space-y-4 shadow-xl transition-all duration-300",
            modalStep === "preview" ? "max-w-4xl" : "max-w-xl"
          )}>
            <h2 className="text-[#4E5D5A] text-base font-semibold">
              {modalStep === "preview" ? "Verify Extracted Bounding Boxes" : "Add Candidate Profile"}
            </h2>
            
            {modalStep === "upload" && (
              <div className="space-y-4">
                <div className="border border-dashed border-[#4E5D5A]/15 hover:border-[#4E5D5A]/30 rounded-xl p-8 bg-[#EFE8DE]/50 text-center relative transition-colors flex flex-col items-center justify-center min-h-[180px]">
                  <input
                    type="file"
                    accept=".txt,.pdf,.md,.doc,.docx"
                    onChange={handleFileUpload}
                    className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                  />
                  <div className="space-y-2 flex flex-col items-center">
                    <Upload className="w-8 h-8 text-[#1D8F88] mb-1 animate-bounce" />
                    <p className="text-xs text-[#1D8F88] font-medium">Upload Resume to Auto-Fill (Optional)</p>
                    <p className="text-[10px] text-[#6A756F]">Supports PDF, Word, Markdown, or Text files</p>
                    {parseStatus && (
                      <p className={cn(
                        "text-[11px] font-medium mt-2",
                        parseStatus.includes("Error") || parseStatus.includes("Failed") ? "text-[#F17A7E]" : "text-[#1D8F88]"
                      )}>
                        {parseStatus}
                      </p>
                    )}
                  </div>
                </div>

                <div className="text-center">
                  <span className="text-xs text-[#6A756F]">Or</span>
                </div>

                <div className="flex justify-center">
                  <button
                    type="button"
                    onClick={() => setModalStep("edit")}
                    className="px-6 py-2 bg-[#EFE8DE] hover:bg-[#EFE8DE]/80 border border-[#4E5D5A]/15 rounded-full text-xs font-semibold text-[#4E5D5A] transition-colors"
                  >
                    Skip & Fill Manually
                  </button>
                </div>

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      setIsAdding(false);
                      setParseStatus(null);
                    }}
                    className="px-4 py-2 bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded-full text-[#6A756F] text-xs hover:text-[#4E5D5A]"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {modalStep === "preview" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
                <div>{renderPreviewSummary()}</div>
                <div>{renderResumeCoordinatesMap()}</div>
              </div>
            )}

            {modalStep === "edit" && (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-[#6A756F] mb-1">Full Name *</label>
                    <input
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[#6A756F] mb-1">Email Address</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-[#6A756F] mb-1">Current Position *</label>
                    <input
                      required
                      value={formData.current_position}
                      onChange={(e) => setFormData({ ...formData, current_position: e.target.value })}
                      className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[#6A756F] mb-1">Location *</label>
                    <input
                      required
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-[#6A756F] mb-1">Experience (Years) *</label>
                    <input
                      required
                      type="number"
                      value={formData.experience_years}
                      onChange={(e) => setFormData({ ...formData, experience_years: Number(e.target.value) })}
                      className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[#6A756F] mb-1">Notice Period (Days)</label>
                    <input
                      type="number"
                      value={formData.notice_period_days}
                      onChange={(e) => setFormData({ ...formData, notice_period_days: Number(e.target.value) })}
                      className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-[#6A756F] mb-1">Salary Expectation ($)</label>
                    <input
                      type="number"
                      value={formData.salary_expectation}
                      onChange={(e) => setFormData({ ...formData, salary_expectation: Number(e.target.value) })}
                      className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-[#6A756F] mb-1">Skills (comma separated) *</label>
                  <input
                    required
                    placeholder="Python, AWS, Terraform, Docker"
                    value={formData.skills}
                    onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                    className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                  />
                </div>
                <div>
                  <label className="block text-xs text-[#6A756F] mb-1">Resume Text Summary</label>
                  <textarea
                    rows={4}
                    value={formData.resume_text}
                    onChange={(e) => setFormData({ ...formData, resume_text: e.target.value })}
                    className="w-full bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded px-3 py-2 text-[#4E5D5A] text-sm focus:outline-none focus:border-[#1D8F88]"
                    placeholder="Paste brief resume overview or skills summary here..."
                  />
                </div>
                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      if (parsedCoords) {
                        setModalStep("preview");
                      } else {
                        setModalStep("upload");
                      }
                    }}
                    className="px-4 py-2 bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded-full text-[#6A756F] text-xs hover:text-[#4E5D5A]"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-[#1D8F88] text-[#F7F5EF] rounded-full text-xs hover:bg-[#1D8F88]/80 font-medium transition-colors"
                  >
                    Create Profile
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-3">
                <Skeleton className="w-12 h-12 rounded-xl" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-32 rounded" />
                  <Skeleton className="h-3 w-24 rounded" />
                </div>
              </div>
              <Skeleton className="h-3 w-full rounded" />
              <div className="flex gap-1.5">
                <Skeleton className="h-5 w-16 rounded-full" />
                <Skeleton className="h-5 w-16 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      ) : filtered?.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <Users className="w-12 h-12 text-[#6A756F]/30 mb-4" />
          <p className="text-[#4E5D5A] font-medium">No candidates found</p>
          <p className="text-[#6A756F] text-sm mt-1">Try a different search query</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered?.map((candidate, i) => (
            <motion.div
              key={candidate.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link
                href={`/command-center/candidates/${candidate.id}`}
                className="block bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl p-5 group hover:border-[#4E5D5A]/25 transition-all shadow-sm"
              >
                <div className="flex items-start gap-3 mb-4">
                  <div className="w-11 h-11 rounded-xl bg-[#4A6163] flex items-center justify-center text-[#F7F5EF] font-bold flex-shrink-0">
                    {getInitials(candidate.name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[#4E5D5A] font-medium text-sm truncate">{candidate.name}</p>
                    <p className="text-[#6A756F] text-xs truncate">{candidate.current_position}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-[#6A756F] group-hover:text-[#1D8F88] transition-colors flex-shrink-0" />
                </div>

                <div className="flex items-center gap-3 text-xs text-[#6A756F] mb-3">
                  <span className="flex items-center gap-1">
                    <Briefcase className="w-3 h-3" />{candidate.experience_years}y
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />{candidate.location}
                  </span>
                </div>

                <div className="flex flex-wrap gap-1">
                  {candidate.skills?.slice(0, 4).map((skill, si) => (
                    <span key={skill} className={cn("px-1.5 py-0.5 rounded-full text-xs border bg-[#EFE8DE] border-[#4E5D5A]/10 text-[#4E5D5A]")}>
                      {skill}
                    </span>
                  ))}
                  {(candidate.skills?.length || 0) > 4 && (
                    <span className="text-xs text-[#6A756F]">+{candidate.skills.length - 4}</span>
                  )}
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
