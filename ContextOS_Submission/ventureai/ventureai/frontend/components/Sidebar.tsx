"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard, Zap, Users, Building2,
  GitBranch, Activity, BarChart3, HeartPulse,
  Settings, ChevronRight, Layers
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_SECTIONS = [
  {
    items: [
      { label: "Command Center", href: "/command-center", icon: LayoutDashboard },
      { label: "Decision Queue", href: "/command-center/decision-queue", icon: Zap },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { label: "Candidate Intelligence", href: "/command-center/candidates", icon: Users },
      { label: "Client Intelligence", href: "/command-center/clients", icon: Building2 },
    ],
  },
  {
    label: "Platform",
    items: [
      { label: "AI Planner", href: "/command-center/planner", icon: GitBranch },
      { label: "Execution Timeline", href: "/command-center/execution-timeline", icon: Activity },
    ],
  },
  {
    label: "Operations",
    items: [
      { label: "Decision Analytics", href: "/command-center/analytics", icon: BarChart3 },
      { label: "Platform Health", href: "/command-center/platform-health", icon: HeartPulse },
      { label: "Platform Configuration", href: "/command-center/settings", icon: Settings },
    ],
  },
];

interface SidebarProps {
  healthStatus?: string;
}

export default function Sidebar({ healthStatus = "healthy" }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className="h-full flex flex-col"
      style={{ background: "var(--color-sidebar-bg)", borderRight: "1px solid var(--color-context-border)", width: "var(--color-sidebar-width)" }}
      aria-label="Main navigation"
    >
      {/* Logo */}
      <div className="px-4 py-5 border-b border-[var(--color-context-border)] flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-[#1D8F88] flex items-center justify-center flex-shrink-0">
          <Layers className="w-4 h-4 text-[#F7F5EF]" />
        </div>
        <div>
          <span className="text-[#4E5D5A] text-sm font-semibold tracking-tight">ContextOS</span>
          <p className="text-[#6A756F] text-[10px] font-mono leading-none mt-0.5">v1.0 · Enterprise</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-5">
        {NAV_SECTIONS.map((section, si) => (
          <div key={si}>
            {section.label && (
              <div className="px-2 mb-1 text-[10px] font-medium text-[#6A756F] uppercase tracking-widest">
                {section.label}
              </div>
            )}
            <ul className="space-y-0.5" role="list">
              {section.items.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== "/command-center" && pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <li key={item.label}>
                    <Link
                      href={item.href}
                      aria-current={isActive ? "page" : undefined}
                      className={cn(
                        "flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm transition-all duration-150 group relative",
                        isActive
                          ? "sidebar-item-active text-[#4E5D5A] font-semibold"
                          : "text-[#6A756F] hover:text-[#4E5D5A] hover:bg-[#EFE8DE]"
                      )}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="sidebar-active"
                          className="absolute left-0 top-0 bottom-0 w-0.5 bg-[#1D8F88] rounded-full"
                          transition={{ type: "spring", stiffness: 400, damping: 30 }}
                        />
                      )}
                      <Icon
                        className={cn(
                          "w-4 h-4 flex-shrink-0 transition-colors",
                          isActive ? "text-[#1D8F88]" : "text-[#6A756F] group-hover:text-[#4E5D5A]"
                        )}
                      />
                      <span className="truncate">{item.label}</span>
                      {isActive && (
                        <ChevronRight className="w-3 h-3 ml-auto text-[#1D8F88] opacity-60" />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* System status footer */}
      <div className="px-4 py-3 border-t border-[var(--color-context-border)]">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "w-2 h-2 rounded-full flex-shrink-0 status-pulse",
              healthStatus === "ok" || healthStatus === "healthy"
                ? "bg-[#1D8F88]"
                : "bg-[#FFC94B]"
            )}
          />
          <span className="text-xs text-[#6A756F] font-mono">
            System{" "}
            <span
              className={
                healthStatus === "ok" || healthStatus === "healthy"
                  ? "text-[#1D8F88]"
                  : "text-[#FFC94B]"
              }
            >
              {healthStatus === "ok" ? "Healthy" : healthStatus}
            </span>
          </span>
        </div>
        <Link
          href="/"
          className="mt-2 block text-xs text-[#6A756F] hover:text-[#4E5D5A] transition-colors"
        >
          ← Back to Landing
        </Link>
      </div>
    </aside>
  );
}
