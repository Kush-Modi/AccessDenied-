"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-[#F7F5EF] text-[#4E5D5A] py-32 px-8 border-t border-[#4E5D5A]/10">
      <div className="max-w-4xl mx-auto flex flex-col items-center text-center">
        
        {/* Footer Manifesto */}
        <div className="max-w-2xl space-y-12 mb-16">
          <p className="text-[10px] font-mono tracking-widest uppercase text-[#4E5D5A]/60">
            — In Summary
          </p>
          
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-serif font-light leading-tight tracking-tight">
            Context isn't <br />
            another feature. <br />
            <span className="text-[#097C87]">It's the operating system</span> <br />
            behind every <br />
            great hiring decision.
          </h2>
        </div>

        {/* Elegant Action Button */}
        <div className="mb-24">
          <Link
            href="/command-center"
            className="editorial-btn-primary px-10 py-5 text-xs font-semibold inline-flex items-center gap-2"
          >
            Launch ContextOS Platform
            <ArrowRight className="w-4 h-4 text-[#4E5D5A]/60" />
          </Link>
        </div>

        {/* Footer Info Lines */}
        <div className="w-full pt-12 border-t border-[#4E5D5A]/10 flex flex-col md:flex-row items-center justify-between gap-6 text-[10px] font-mono text-[#4E5D5A]/50">
          <div>
            <span>SYSTEM: FASTAPI + LANGGRAPH · MCP GATEWAY</span>
          </div>
          <div>
            <span>CONTEXTOS © 2026 · BUILT FOR XLVENTURES</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
