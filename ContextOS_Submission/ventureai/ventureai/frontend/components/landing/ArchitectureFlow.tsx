"use client";

import { useRef, useState, useEffect } from "react";
import { motion, useInView } from "framer-motion";
import Image from "next/image";

const PIPELINE_LAYERS = [
  {
    name: "Candidate Profile",
    details: "Universal ingestion of applicant context, metadata indexing, and structural skills mappings."
  },
  {
    name: "Enterprise Knowledge Base",
    details: "Aggregating interactions across client emails, shared calendars, call transcripts, and legacy CRM footprints."
  },
  {
    name: "Planner Memory Loop",
    details: "Capturing real-time recruiter match approvals and rejections to adapt the neural retrieval weights dynamically."
  },
  {
    name: "Deterministic Policy Rules",
    details: "Enforcing business constraints: spatial compliance checks, suppression flags, active client hiring freezes."
  },
  {
    name: "Multi-Signal Match Decision",
    details: "Synthesizing signals via autonomous planner agents into a singular, clean match confidence rating."
  },
  {
    name: "Human-in-the-Loop Consent",
    details: "Interactive gate callback: decisions wait for human approval before execution writeback."
  }
];

export default function ArchitectureFlow() {
  const containerRef = useRef<HTMLDivElement>(null);
  const inView = useInView(containerRef, { once: false, margin: "-150px" });
  const [activeStep, setActiveStep] = useState(0);

  // Cycle the highlight index when container is in view to simulate living system scroll highlight
  useEffect(() => {
    if (!inView) return;
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % PIPELINE_LAYERS.length);
    }, 2800);
    return () => clearInterval(interval);
  }, [inView]);

  return (
    <section ref={containerRef} id="architecture" className="py-44 px-8 bg-[#F4F1EA] text-[#4E5D5A]">
      <div className="max-w-6xl mx-auto">
        
        {/* Section Header */}
        <div className="mb-24 text-left">
          <p className="text-[10px] font-mono tracking-widest uppercase mb-4 text-[#4E5D5A]/60">
            — System Pipeline
          </p>
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-serif font-light text-[#4E5D5A] leading-tight max-w-3xl">
            A linear sequence of context.
          </h2>
          <p className="text-xs text-[#4E5D5A]/70 max-w-md mt-6 leading-relaxed">
            Six layers of indexing and governance transform raw workplace footprint data into precise placements.
          </p>
        </div>

        {/* Two Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-start">
          
          {/* Left Column: Editorial Architecture Timeline */}
          <div className="lg:col-span-7 space-y-10 relative">
            {PIPELINE_LAYERS.map((layer, index) => {
              const isActive = activeStep === index;
              return (
                <div 
                  key={layer.name} 
                  onClick={() => setActiveStep(index)}
                  className="group cursor-pointer block"
                >
                  {/* Horizontal line divider */}
                  <div className="w-full h-px bg-[#4E5D5A]/10 relative overflow-hidden mb-6">
                    {isActive && (
                      <motion.div 
                        layoutId="timeline-glow-bar"
                        className="absolute inset-y-0 left-0 w-32 bg-[#F9A66C]"
                        transition={{ type: "spring", stiffness: 80, damping: 15 }}
                      />
                    )}
                  </div>

                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 transition-opacity duration-500">
                    <div className="flex items-center gap-6">
                      {/* Index number */}
                      <span className={`font-mono text-xs ${isActive ? "text-[#F9A66C] font-semibold" : "text-[#4E5D5A]/40"}`}>
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      {/* Title */}
                      <h3 className={`text-xl md:text-2xl font-light transition-colors ${isActive ? "text-[#4E5D5A] font-medium" : "text-[#4E5D5A]/50 group-hover:text-[#4E5D5A]/80"}`}>
                        {layer.name}
                      </h3>
                    </div>

                    {/* Details block */}
                    <div className="md:w-80 pl-12 md:pl-0">
                      <p className={`text-xs leading-relaxed transition-colors duration-500 ${isActive ? "text-[#4E5D5A]/80" : "text-[#4E5D5A]/40"}`}>
                        {layer.details}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
            
            {/* Subtle bottom divider */}
            <div className="w-full h-px bg-[#4E5D5A]/10 mt-6" />
          </div>

          {/* Right Column: Vertical Photo Frame */}
          <div className="lg:col-span-5 flex flex-col items-center lg:sticky lg:top-24">
            <div className="w-full max-w-sm aspect-[3/4] overflow-hidden rounded-2xl border border-[#4E5D5A]/10 bg-[#EFE8DE] p-2 shadow-sm relative group">
              <div className="w-full h-full rounded-xl overflow-hidden relative">
                <Image
                  src="/arch_vertical.png"
                  alt="ContextOS System Architecture Pipeline Sketch"
                  fill
                  className="object-cover grayscale hover:grayscale-0 transition-all duration-700 ease-out scale-102 group-hover:scale-100"
                  sizes="(max-w-768px) 100vw, 400px"
                  priority
                />
              </div>
            </div>
            <p className="text-[10px] text-[#6A756F]/60 font-mono mt-4 uppercase tracking-wider text-center">
              Figure 3.4 — Sequence flow & neural indexing bounds
            </p>
          </div>

        </div>

      </div>
    </section>
  );
}
