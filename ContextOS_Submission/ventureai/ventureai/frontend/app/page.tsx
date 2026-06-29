"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import BootScreen from "@/components/BootScreen";
import Hero from "@/components/landing/Hero";
import MissionStatement from "@/components/landing/MissionStatement";
import ArchitectureFlow from "@/components/landing/ArchitectureFlow";
import IntelligenceCards from "@/components/landing/IntelligenceCards";
import TechStack from "@/components/landing/TechStack";
import DemoPreview from "@/components/landing/DemoPreview";
import Footer from "@/components/landing/Footer";

export default function LandingPage() {
  const [booted, setBooted] = useState(false);
  const [hasBooted, setHasBooted] = useState(false);

  useEffect(() => {
    // Only show boot screen once per session
    const booted = sessionStorage.getItem("contextos-booted");
    if (booted) {
      setBooted(true);
      setHasBooted(true);
    }
  }, []);

  const handleBootComplete = () => {
    sessionStorage.setItem("contextos-booted", "true");
    setBooted(true);
    setHasBooted(true);
  };

  return (
    <>
      {!hasBooted && <BootScreen onComplete={handleBootComplete} />}
      <AnimatePresence>
        {booted && (
          <motion.main
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="min-h-screen bg-[#F7F5EF] text-[#4E5D5A]"
          >
            <Hero />
            <MissionStatement />
            <ArchitectureFlow />
            <IntelligenceCards />
            <TechStack />
            <DemoPreview />
            <Footer />
          </motion.main>
        )}
      </AnimatePresence>
    </>
  );
}
