"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";

const TECH_STACK = [
  { name: "FastAPI", desc: "REST API Gateway", color: "text-[#1D8F88]" },
  { name: "LangGraph", desc: "ReAct Agent Graph", color: "text-[#4A6163]" },
  { name: "MCP Protocol", desc: "Tool Transport Layer", color: "text-[#F9A66C]" },
  { name: "Redis", desc: "Cache & Session Store", color: "text-[#F17A7E]" },
  { name: "Supabase", desc: "PostgreSQL + pgvector", color: "text-[#1D8F88]" },
  { name: "Groq LLM", desc: "Inference Engine", color: "text-[#FFC94B]" },
  { name: "pgvector", desc: "Semantic Search", color: "text-[#4A6163]" },
  { name: "Next.js 15", desc: "React Framework", color: "text-[#4E5D5A]" },
  { name: "React Flow", desc: "Node Graph UI", color: "text-[#23CED9]" },
  { name: "Framer Motion", desc: "Animation Engine", color: "text-[#F17A7E]" },
];

export default function TechStack() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  return (
    <section 
      ref={ref} 
      id="technology" 
      className="py-32 px-8 text-[#4E5D5A] relative overflow-hidden"
      style={{
        backgroundImage: "url('/tech_bg.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* Editorial warm overlay for high contrast, legibility, and premium texture integration */}
      <div className="absolute inset-0 bg-[#E7DDD0]/85 pointer-events-none" />

      <div className="relative max-w-5xl mx-auto z-10">
        
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16 space-y-4"
        >
          <p className="text-[10px] font-mono tracking-widest uppercase text-[#4E5D5A]/60">
            — Technology Stack
          </p>
          <h2 className="text-4xl sm:text-5xl font-serif font-light text-[#4E5D5A]">
            Built on the right primitives.
          </h2>
        </motion.div>

        {/* Tech Badges Grid */}
        <div className="flex flex-wrap justify-center gap-3 max-w-4xl mx-auto">
          {TECH_STACK.map((tech, i) => (
            <motion.div
              key={tech.name}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={inView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.6, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }}
              className="bg-[#F4F1EA]/95 border border-[#4E5D5A]/12 px-5 py-4 rounded-[16px] shadow-sm cursor-default hover:border-[#4E5D5A]/30 hover:bg-[#F4F1EA] transition-all flex flex-col justify-between w-40 min-h-[90px]"
            >
              <span className={`text-xs font-semibold tracking-wide ${tech.color} block`}>
                {tech.name}
              </span>
              <span className="text-[10px] text-[#4E5D5A]/70 mt-1 block">
                {tech.desc}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Pipeline Flow text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 0.6 } : {}}
          transition={{ delay: 0.8 }}
          className="mt-16 flex items-center justify-center gap-3 flex-wrap text-[10px] font-mono text-[#4E5D5A]/70"
        >
          {["FastAPI", "→", "LangGraph", "→", "MCP", "→", "Redis", "→", "Supabase", "→", "Next.js"].map(
            (item, i) => (
              <span
                key={i}
                className={item === "→" ? "opacity-30" : "font-semibold"}
              >
                {item}
              </span>
            )
          )}
        </motion.div>

      </div>
    </section>
  );
}
