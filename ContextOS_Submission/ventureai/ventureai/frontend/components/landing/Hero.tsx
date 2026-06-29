"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, ChevronDown } from "lucide-react";

export default function Hero() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true });

  return (
    <section
      ref={ref}
      className="relative min-h-screen flex flex-col items-center justify-between bg-[#F7F5EF] text-[#4E5D5A] overflow-hidden py-12 px-8"
      aria-label="Hero section"
    >
      {/* Top minimal navigation */}
      <nav className="w-full max-w-6xl mx-auto flex items-center justify-between z-20">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-[#4E5D5A] flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-3 h-3 text-[#F7F5EF]">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span className="font-semibold text-xs tracking-widest uppercase text-[#4E5D5A]">ContextOS</span>
        </div>
        <div className="flex items-center gap-8 text-xs font-medium tracking-wide">
          <a href="#architecture" className="text-[#4E5D5A]/70 hover:text-[#4E5D5A] transition-colors hidden sm:block">Architecture</a>
          <a href="#technology" className="text-[#4E5D5A]/70 hover:text-[#4E5D5A] transition-colors hidden sm:block">Technology</a>
          <Link
            href="/command-center"
            className="px-4 py-2 rounded-full border border-[#4E5D5A]/20 bg-[#F4F1EA] hover:bg-[#EFE8DE] text-[#4E5D5A] hover:border-[#4E5D5A]/40 transition-all text-xs font-semibold shadow-sm"
          >
            Launch Platform
          </Link>
        </div>
      </nav>

      {/* Hero content */}
      <div className="w-full max-w-5xl mx-auto text-center z-10 my-auto flex flex-col items-center gap-12">
        <div className="space-y-6">
          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 0.6 } : {}}
            transition={{ duration: 0.8 }}
            className="text-[10px] font-mono tracking-widest uppercase text-[#4E5D5A]/80"
          >
            ContextOS — Systems Architecture
          </motion.p>

          <motion.h1
            initial={{ opacity: 0, y: 15 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="text-5xl sm:text-7xl md:text-[92px] lg:text-[108px] text-[#4E5D5A] font-light leading-[0.95] tracking-tight max-w-4xl mx-auto font-serif"
          >
            Every hiring decision <br />
            already has <br />
            the answer.
          </motion.h1>
        </div>

        {/* Stunning architectural/brutalist structure image (almost monochrome, negative space) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={inView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 1.2, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full max-w-3xl h-64 md:h-96 overflow-hidden rounded-[24px] border border-[#4E5D5A]/10 shadow-sm"
        >
          <Image
            src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600&q=80"
            alt="Brutalist glass and concrete structure"
            fill
            priority
            className="object-cover object-center brightness-[0.95] contrast-[1.02] filter grayscale opacity-90 transition-transform duration-[10s] hover:scale-105"
            sizes="(max-width: 768px) 100vw, 80vw"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#F7F5EF]/30 to-transparent" />
        </motion.div>

        <div className="space-y-6">
          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-lg md:text-xl font-light text-[#4E5D5A]/80 tracking-wide max-w-lg mx-auto"
          >
            ContextOS finds it.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="flex items-center justify-center gap-4"
          >
            <Link
              href="/command-center"
              className="editorial-btn-primary px-6 py-3 text-xs font-semibold flex items-center gap-2"
            >
              Explore Platform
              <ArrowRight className="w-3.5 h-3.5 text-[#4E5D5A]/60" />
            </Link>
            <a
              href="#architecture"
              className="px-6 py-3 rounded-full border border-[#4E5D5A]/10 hover:border-[#4E5D5A]/35 text-[#4E5D5A]/70 hover:text-[#4E5D5A] text-xs font-semibold transition-all"
            >
              View Architecture
            </a>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="w-full flex flex-col items-center gap-1.5"
      >
        <span className="text-[9px] text-[#4E5D5A]/50 font-mono tracking-widest">SCROLL TO READ</span>
        <ChevronDown className="w-3.5 h-3.5 text-[#4E5D5A]/50 scroll-indicator" />
      </motion.div>
    </section>
  );
}
