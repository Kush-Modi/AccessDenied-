"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Play, Terminal, UserCheck, ShieldCheck } from "lucide-react";

export default function DemoPreview() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section ref={ref} className="py-44 px-8 bg-[#4E5D5A] text-[#F7F5EF] overflow-hidden">
      <div className="max-w-5xl mx-auto">
        
        {/* Section Header */}
        <div className="text-center mb-24 max-w-xl mx-auto space-y-4">
          <p className="text-[10px] font-mono tracking-widest uppercase text-[#F7F5EF]/60">
            — Operational Interface
          </p>
          <h2 className="text-4xl sm:text-5xl font-serif font-light leading-tight">
            See the system act.
          </h2>
          <p className="text-xs text-[#F7F5EF]/80 leading-relaxed">
            The platform translates multiple signals into a singular interface, maintaining explainability at every juncture.
          </p>
        </div>

        {/* Floating CSS MacBook Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.98 }}
          animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
          className="relative max-w-4xl mx-auto"
        >
          {/* Subtle architectural background shadow */}
          <div className="absolute inset-0 -translate-y-4 blur-3xl bg-black/15 rounded-full" />

          {/* MacBook Screen Lid Frame */}
          <div className="relative bg-zinc-900 p-2.5 rounded-t-3xl border-t border-x border-zinc-700 shadow-2xl">
            {/* Screen bezel */}
            <div className="relative aspect-[16/10] overflow-hidden bg-[#121212] border-[8px] border-black rounded-lg">
              {/* Webcam notch */}
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-28 h-3.5 bg-black rounded-b-md z-30" />
              
              {/* Mock Dashboard Preview Screen Content */}
              <div className="w-full h-full text-zinc-400 font-sans text-[10px] p-3 select-none flex flex-col justify-between">
                
                {/* Dashboard top header bar */}
                <div className="flex items-center justify-between border-b border-white/5 pb-2.5">
                  <div className="flex items-center gap-3">
                    {/* Fake dots */}
                    <div className="flex gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-red-500/60" />
                      <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/60" />
                      <div className="w-1.5 h-1.5 rounded-full bg-green-500/60" />
                    </div>
                    <span className="font-mono text-[8px] opacity-40">localhost:3000/command-center</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#1D8F88]" />
                    <span className="text-[9px] font-mono opacity-65">System: Active</span>
                  </div>
                </div>

                {/* Dashboard Inner workspace body */}
                <div className="flex-1 grid grid-cols-12 gap-3 py-3 overflow-hidden">
                  
                  {/* Dashboard Mock Sidebar */}
                  <div className="col-span-3 border-r border-white/5 pr-2 flex flex-col gap-2">
                    <div className="h-4 bg-white/10 rounded w-2/3" />
                    <div className="space-y-1.5 mt-2">
                      <div className="h-3 bg-[#F9A66C]/10 border border-[#F9A66C]/20 rounded px-1.5 py-0.5 text-[#F9A66C] text-[8px] font-medium flex items-center gap-1">
                        <UserCheck className="w-2.5 h-2.5" /> Command Center
                      </div>
                      <div className="h-3 bg-white/5 rounded px-1.5 py-0.5 text-zinc-500 flex items-center gap-1">
                        <ShieldCheck className="w-2.5 h-2.5" /> Decision Queue
                      </div>
                      <div className="h-3 bg-white/5 rounded px-1.5 py-0.5 text-zinc-500 flex items-center gap-1">
                        <Terminal className="w-2.5 h-2.5" /> Platform Health
                      </div>
                    </div>
                  </div>

                  {/* Dashboard Main Candidate Workspace Mock */}
                  <div className="col-span-6 space-y-3 flex flex-col justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-white text-xs font-serif font-light">Ananya Sharma</h4>
                          <p className="text-[8px] opacity-50">Candidate fit matches Senior Architect profile</p>
                        </div>
                        <span className="px-1.5 py-0.5 bg-[#1D8F88]/10 text-[#1D8F88] rounded text-[8px] border border-[#1D8F88]/20">94% Fit</span>
                      </div>
                      
                      {/* Skill tags */}
                      <div className="flex flex-wrap gap-1.5">
                        {["TypeScript", "Rust", "Distributed Systems", "MCP"].map(tag => (
                          <span key={tag} className="px-1.5 py-0.5 bg-white/5 rounded text-[8px] border border-white/5 text-zinc-300">{tag}</span>
                        ))}
                      </div>
                    </div>

                    {/* Agent Live Trace block mock */}
                    <div className="bg-black/40 border border-white/5 p-2 rounded-lg font-mono text-[8px] space-y-1.5 flex-1 mt-1 overflow-hidden">
                      <div className="text-white/60 flex items-center gap-1">
                        <span className="text-[#F9A66C] font-bold">▶</span> [Agent Planner] Loading matching context...
                      </div>
                      <div className="text-zinc-500 pl-3">
                        - Checked 12 business rules: No blocks.
                      </div>
                      <div className="text-zinc-500 pl-3">
                        - Retrieved placement history (1 success placement).
                      </div>
                      <div className="text-[#1D8F88] pl-3 font-semibold">
                        ✓ Recommendation completed. Triggering HITL review block.
                      </div>
                    </div>
                  </div>

                  {/* Dashboard Decision / Action Panel Mock */}
                  <div className="col-span-3 bg-white/5 rounded-lg border border-white/5 p-2.5 flex flex-col justify-between">
                    <div className="space-y-2">
                      <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-wide">Next Best Action</span>
                      <h5 className="text-white text-[10px] font-serif font-light leading-tight">Approve placement proposal</h5>
                      <p className="text-[8px] opacity-60">Client: TechCorp Bangalore</p>
                    </div>

                    <div className="space-y-1.5 pt-2">
                      <div className="w-full h-5 rounded bg-[#1D8F88] hover:bg-[#1D8F88]/90 text-white font-semibold text-[8px] flex items-center justify-center cursor-pointer transition-all">
                        Approve Decision
                      </div>
                      <div className="w-full h-5 rounded border border-white/10 hover:border-white/20 text-zinc-400 text-[8px] flex items-center justify-center cursor-pointer transition-all">
                        Reject
                      </div>
                    </div>
                  </div>

                </div>

                {/* Dashboard bottom stats status bar */}
                <div className="border-t border-white/5 pt-2 flex items-center justify-between text-[7px] font-mono opacity-50">
                  <span>Session: ses_ananya_092</span>
                  <span>Latency: 142ms</span>
                  <span>Rules Verified: 12/12</span>
                </div>

              </div>
            </div>
          </div>

          {/* MacBook Bottom Base Keyboard Frame */}
          <div className="relative h-3 bg-gradient-to-r from-zinc-700 via-zinc-800 to-zinc-700 rounded-b-2xl shadow-xl border-t border-zinc-600 flex justify-center">
            {/* Display notch groove */}
            <div className="w-20 h-1 bg-zinc-950 rounded-b-md" />
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="text-center mt-20"
        >
          <Link
            href="/command-center"
            className="editorial-btn-primary px-8 py-4 text-xs font-semibold inline-flex items-center gap-2"
          >
            Launch Command Center
            <ArrowRight className="w-4 h-4 text-[#4E5D5A]/60" />
          </Link>
          <p className="text-[9px] text-[#F7F5EF]/50 mt-4 font-mono">
            Connects to FastAPI server at port 8000. No mock data.
          </p>
        </motion.div>

      </div>
    </section>
  );
}
