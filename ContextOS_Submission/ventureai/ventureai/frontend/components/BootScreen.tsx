"use client";
import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

const BOOT_STEPS = [
  { label: "Planner Online", detail: "LangGraph ReAct Agent ready" },
  { label: "Knowledge Loaded", detail: "Hybrid retrieval engine active" },
  { label: "Redis Connected", detail: "Session cache & HITL bridge live" },
  { label: "Business Rules Loaded", detail: "12 rules active" },
  { label: "Memory Module Ready", detail: "Feedback learner initialized" },
  { label: "Embeddings Engine Ready", detail: "pgvector similarity search online" },
];

interface BootScreenProps {
  onComplete: () => void;
}

export default function BootScreen({ onComplete }: BootScreenProps) {
  const [currentStep, setCurrentStep] = useState(-1);
  const [done, setDone] = useState(false);
  const [exiting, setExiting] = useState(false);

  const advance = useCallback(() => {
    let step = 0;
    const interval = setInterval(() => {
      setCurrentStep(step);
      step++;
      if (step >= BOOT_STEPS.length) {
        clearInterval(interval);
        setTimeout(() => {
          setDone(true);
          setTimeout(() => {
            setExiting(true);
            setTimeout(onComplete, 600);
          }, 800);
        }, 500);
      }
    }, 420);
    return () => clearInterval(interval);
  }, [onComplete]);

  useEffect(() => {
    const timer = setTimeout(advance, 400);
    return () => clearTimeout(timer);
  }, [advance]);

  return (
    <AnimatePresence>
      {!exiting && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
          className="fixed inset-0 z-[9999] flex flex-col items-center justify-center"
          style={{ background: "var(--color-canvas-primary, #F7F5EF)" }}
        >
          <div className="relative z-10 w-full max-w-lg px-8">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="mb-12 text-center"
            >
              <div className="inline-flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-[#1D8F88] flex items-center justify-center">
                  <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <span className="text-[#4E5D5A] text-xl font-semibold tracking-tight">ContextOS</span>
              </div>
              <p className="text-[#6A756F] font-mono text-sm tracking-wider uppercase">
                Initializing Enterprise Intelligence Layer...
              </p>
            </motion.div>

            {/* Boot steps */}
            <div className="space-y-3 font-mono text-sm mb-12 text-[#4E5D5A]">
              {BOOT_STEPS.map((step, i) => {
                const isVisible = i <= currentStep;
                const isDone = i < currentStep || (done && i === currentStep);
                return (
                  <AnimatePresence key={step.label}>
                    {isVisible && (
                      <motion.div
                        initial={{ opacity: 0, x: -12 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, ease: "easeOut" }}
                        className="flex items-center gap-3"
                      >
                        {/* Status icon */}
                        <span className="w-5 flex-shrink-0 flex items-center justify-center">
                          {isDone ? (
                            <motion.span
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              className="text-[#1D8F88] text-base font-semibold"
                            >
                              ✓
                            </motion.span>
                          ) : (
                            <span className="w-3 h-3 rounded-full border border-[#1D8F88] border-t-transparent animate-spin" />
                          )}
                        </span>
                        <span className={isDone ? "text-[#4E5D5A]" : "text-[#1D8F88]"}>
                          {step.label}
                        </span>
                        {isDone && step.detail && (
                          <motion.span
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.2 }}
                            className="text-[#6A756F]/70 text-xs ml-auto"
                          >
                            {step.detail}
                          </motion.span>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                );
              })}
            </div>

            {/* Done state */}
            <AnimatePresence>
              {done && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center"
                >
                  <div className="inline-flex items-center gap-2 text-[#1D8F88] font-mono text-sm">
                    <span>Launching Command Center</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 0.8, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Progress bar */}
            <div className="mt-8 h-px bg-[#4E5D5A]/10 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-[#1D8F88] to-[#23CED9]"
                initial={{ width: 0 }}
                animate={{
                  width: `${Math.min(((currentStep + 1) / BOOT_STEPS.length) * 100, 100)}%`,
                }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
