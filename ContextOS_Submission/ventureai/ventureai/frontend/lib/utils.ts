import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatConfidence(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatConfidenceInt(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function getConfidenceColor(value: number): string {
  if (value >= 0.8) return "text-emerald-400";
  if (value >= 0.6) return "text-amber-400";
  return "text-red-400";
}

export function getConfidenceBgColor(value: number): string {
  if (value >= 0.8) return "bg-emerald-500";
  if (value >= 0.6) return "bg-amber-500";
  return "bg-red-500";
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case "healthy":
    case "operational":
    case "ok":
    case "loaded":
    case "ready":
    case "active":
      return "text-emerald-400";
    case "degraded":
    case "warning":
      return "text-amber-400";
    case "error":
    case "down":
    case "unhealthy":
      return "text-red-400";
    default:
      return "text-zinc-400";
  }
}

export function getStatusDotColor(status: string): string {
  switch (status.toLowerCase()) {
    case "healthy":
    case "operational":
    case "ok":
    case "loaded":
    case "ready":
    case "active":
      return "bg-emerald-400";
    case "degraded":
    case "warning":
      return "bg-amber-400";
    case "error":
    case "down":
    case "unhealthy":
      return "bg-red-400";
    default:
      return "bg-zinc-400";
  }
}

export function timeAgo(date: Date | string): string {
  const now = new Date();
  const d = typeof date === "string" ? new Date(date) : date;
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function truncate(str: string, n: number): string {
  return str.length > n ? str.slice(0, n) + "…" : str;
}

export function slugify(str: string): string {
  return str.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function getSkillColor(index: number): string {
  const colors = [
    "bg-indigo-500/15 text-indigo-300 border-indigo-500/20",
    "bg-violet-500/15 text-violet-300 border-violet-500/20",
    "bg-blue-500/15 text-blue-300 border-blue-500/20",
    "bg-cyan-500/15 text-cyan-300 border-cyan-500/20",
    "bg-teal-500/15 text-teal-300 border-teal-500/20",
    "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
    "bg-amber-500/15 text-amber-300 border-amber-500/20",
  ];
  return colors[index % colors.length];
}

export const LOG_COLORS: Record<string, string> = {
  ">>>": "text-indigo-400",
  "<<<": "text-emerald-400",
  "!!!": "text-amber-400",
  ERROR: "text-red-400",
  WARN: "text-amber-400",
  INFO: "text-zinc-400",
};

export function getLogColor(line: string): string {
  if (line.includes(">>>")) return "text-indigo-400";
  if (line.includes("<<<")) return "text-emerald-400";
  if (line.includes("!!!") || line.includes("PAUSED"))
    return "text-amber-400";
  if (line.toLowerCase().includes("error")) return "text-red-400";
  if (line.toLowerCase().includes("completed") || line.includes("✓"))
    return "text-emerald-400";
  return "text-zinc-400";
}

export function generateId(): string {
  return Math.random().toString(36).slice(2, 9);
}
