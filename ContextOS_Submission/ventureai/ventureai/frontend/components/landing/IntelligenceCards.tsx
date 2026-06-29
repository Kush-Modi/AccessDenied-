"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import Image from "next/image";

const CARDS = [
  {
    label: "Knowledge retrieval",
    stat: "Multi-Source context mapping",
    desc: "Aggregating interactions across emails, meetings, and shared context, indexed directly into candidate files.",
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
    bgClass: "bg-[#F4F1EA] text-[#4E5D5A] border-[#4E5D5A]/10",
    imgClass: "grayscale contrast-100",
    accent: "bg-[#F9A66C]"
  },
  {
    label: "LangGraph Orchestrator",
    stat: "Autonomous agent cycles",
    desc: "A ReAct agent framework bound with custom MCP tools, driving autonomous matching validation.",
    image: "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&q=80",
    bgClass: "bg-[#4A6163] text-[#F7F5EF] border-white/5",
    imgClass: "grayscale brightness-90 contrast-110",
    accent: "bg-[#FFC94B]"
  },
  {
    label: "Recruiter memory loops",
    stat: "Continuous feedback weights",
    desc: "Captures placement feedback history to dynamically adjust planner confidence vectors over time.",
    image: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80",
    bgClass: "bg-[#F4F1EA] text-[#4E5D5A] border-[#4E5D5A]/10",
    imgClass: "grayscale contrast-100",
    accent: "bg-[#F17A7E]"
  },
  {
    label: "Auditable validation",
    stat: "Hierarchical evidence trees",
    desc: "Every recommendation outputs an explainable tree tracing candidate matches directly back to source documents.",
    image: "https://images.unsplash.com/photo-1518005020951-eccb494ad742?w=800&q=80",
    bgClass: "bg-[#4A6163] text-[#F7F5EF] border-white/5",
    imgClass: "grayscale brightness-90 contrast-110",
    accent: "bg-[#1D8F88]"
  },
  {
    label: "Policy engine rules",
    stat: "Deterministic compliance check",
    desc: "Governed by twelve active policies regulating location mismatches, suppression files, and hiring freezes.",
    image: "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80",
    bgClass: "bg-[#F4F1EA] text-[#4E5D5A] border-[#4E5D5A]/10",
    imgClass: "grayscale contrast-100",
    accent: "bg-[#23CED9]"
  }
];

export default function IntelligenceCards() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  return (
    <section ref={ref} className="py-44 px-8 bg-[#EFE8DE] text-[#4E5D5A]">
      <div className="max-w-6xl mx-auto">
        
        {/* Section Header */}
        <div className="mb-24">
          <p className="text-[10px] font-mono tracking-widest uppercase mb-4 text-[#4E5D5A]/60">
            — Core Capabilities
          </p>
          <h2 className="text-4xl sm:text-6xl font-serif font-light text-[#4E5D5A] leading-none">
            Built for precision.
          </h2>
        </div>

        {/* Alternating magazine grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {CARDS.map((card, i) => (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 15 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className={`rounded-[24px] border overflow-hidden flex flex-col justify-between p-6 h-[480px] shadow-sm transition-transform duration-500 hover:scale-[1.005] ${card.bgClass}`}
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-mono tracking-wider uppercase opacity-60">
                    {card.stat}
                  </span>
                  <span className={`w-2 h-2 rounded-full ${card.accent}`} />
                </div>
                
                <h3 className="text-2xl font-serif font-light tracking-tight">
                  {card.label}
                </h3>
                
                <p className="text-xs leading-relaxed opacity-85">
                  {card.desc}
                </p>
              </div>

              {/* Architectural image footer in card */}
              <div className="relative w-full h-52 mt-6 overflow-hidden rounded-[16px]">
                <Image
                  src={card.image}
                  alt={card.label}
                  fill
                  className={`object-cover object-center transition-transform duration-1000 hover:scale-105 ${card.imgClass}`}
                  sizes="(max-width: 768px) 100vw, 30vw"
                />
              </div>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
}
