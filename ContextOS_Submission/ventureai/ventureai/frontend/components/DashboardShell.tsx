"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";
import CommandPalette from "@/components/CommandPalette";
import useSWR from "swr";
import api from "@/lib/api";

interface DashboardShellProps {
  children: React.ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

export default function DashboardShell({ children, breadcrumbs = [] }: DashboardShellProps) {
  const [leftWidth, setLeftWidth] = useState(240);
  const [isDragging, setIsDragging] = useState(false);

  const { data: health } = useSWR("health", () => api.health(), { refreshInterval: 30000 });
  const { data: candidates } = useSWR("candidates", () => api.getCandidates(), { revalidateOnFocus: false });
  const { data: clients } = useSWR("clients", () => api.getClients(), { revalidateOnFocus: false });

  const healthStatus = health?.status || "unknown";

  // Resizable sidebar
  useEffect(() => {
    if (!isDragging) return;
    const handleMove = (e: MouseEvent) => {
      const newWidth = Math.max(180, Math.min(320, e.clientX));
      setLeftWidth(newWidth);
    };
    const handleUp = () => setIsDragging(false);
    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", handleUp);
    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup", handleUp);
    };
  }, [isDragging]);

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "var(--color-canvas-primary, #F7F5EF)" }}>
      {/* Sidebar */}
      <div style={{ width: leftWidth, flexShrink: 0 }}>
        <Sidebar healthStatus={healthStatus} />
      </div>

      {/* Resizer */}
      <div
        className={`resizer ${isDragging ? "dragging" : ""}`}
        onMouseDown={() => setIsDragging(true)}
        role="separator"
        aria-label="Resize sidebar"
        aria-valuenow={leftWidth}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft") setLeftWidth((w) => Math.max(180, w - 10));
          if (e.key === "ArrowRight") setLeftWidth((w) => Math.min(320, w + 10));
        }}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar breadcrumbs={breadcrumbs} />
        <main className="flex-1 overflow-y-auto page-enter">
          {children}
        </main>
      </div>

      {/* Global Command Palette */}
      <CommandPalette
        candidates={candidates?.map((c) => ({ id: c.id, name: c.name, current_position: c.current_position }))}
        clients={clients?.map((c) => ({ id: c.id, name: c.name }))}
      />
    </div>
  );
}
