"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";

export default function MissionStatement() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section 
      ref={ref} 
      className="relative py-48 px-8 text-[#4E5D5A] overflow-hidden"
      style={{
        backgroundImage: "url('/thesis_bg.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* Editorial warm overlay for high contrast, legibility, and premium texture integration */}
      <div className="absolute inset-0 bg-[#EFE8DE]/85 pointer-events-none" />

      <div className="relative max-w-5xl mx-auto flex flex-col items-center z-10">
        {/* Thesis label */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 0.6 } : {}}
          transition={{ duration: 0.5 }}
          className="text-[10px] font-mono tracking-widest uppercase mb-16 text-[#4E5D5A]"
        >
          — Our Thesis
        </motion.p>

        {/* Centered Large Manifesto */}
        <div className="w-full text-center space-y-16 max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-4xl sm:text-6xl md:text-7xl font-serif font-light leading-tight tracking-tight text-[#4E5D5A]"
          >
            Every recruiter <br />
            already has <br />
            the answers.
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="text-2xl sm:text-3xl md:text-4xl font-light leading-relaxed tracking-wide text-[#4E5D5A]/70 max-w-2xl mx-auto"
          >
            They're buried inside <br />
            <span className="text-[#4E5D5A] font-medium">emails</span>,{" "}
            <span className="text-[#4E5D5A] font-medium">meetings</span>,{" "}
            <span className="text-[#4E5D5A] font-medium">CRM updates</span>, <br />
            <span className="text-[#4E5D5A] font-medium">feedback</span>, and{" "}
            <span className="text-[#4E5D5A] font-medium">memory</span>.
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="text-4xl sm:text-6xl md:text-7xl font-serif font-light tracking-tight text-[#097C87] pt-8"
          >
            ContextOS <br />
            connects them.
          </motion.div>
        </div>

        {/* Muted supporting thesis statement */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 0.5 } : {}}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="mt-24 border-t border-[#4E5D5A]/10 pt-8 w-full max-w-lg text-center"
        >
          <p className="text-xs uppercase tracking-wider font-semibold">
            Decisions with Context, Not Presumptions.
          </p>
          <p className="text-xs mt-2 leading-relaxed">
            By connecting raw workspace footprints back to hiring outcomes, ContextOS helps teams act on what their records truly mean.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
