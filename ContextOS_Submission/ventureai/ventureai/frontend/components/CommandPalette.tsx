"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Search, Command, Users, Building2, Briefcase,
  LayoutDashboard, GitBranch, Activity, BarChart3,
  HeartPulse, Settings, Zap, X
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Command Center", href: "/command-center", icon: LayoutDashboard, category: "navigation" },
  { label: "AI Planner", href: "/command-center/planner", icon: GitBranch, category: "navigation" },
  { label: "Candidate Intelligence", href: "/command-center/candidates", icon: Users, category: "navigation" },
  { label: "Client Intelligence", href: "/command-center/clients", icon: Building2, category: "navigation" },
  { label: "Decision Queue", href: "/command-center/decision-queue", icon: Zap, category: "navigation" },
  { label: "Execution Timeline", href: "/command-center/execution-timeline", icon: Activity, category: "navigation" },
  { label: "Decision Analytics", href: "/command-center/analytics", icon: BarChart3, category: "navigation" },
  { label: "Platform Health", href: "/command-center/platform-health", icon: HeartPulse, category: "navigation" },
  { label: "Platform Configuration", href: "/command-center/settings", icon: Settings, category: "navigation" },
];

type CommandItem = {
  id: string;
  label: string;
  description?: string;
  icon: React.ElementType;
  href?: string;
  action?: () => void;
  category: string;
};

interface CommandPaletteProps {
  candidates?: Array<{ id: string; name: string; current_position?: string }>;
  clients?: Array<{ id: string; name: string }>;
  jobs?: Array<{ id: string; title: string; clients?: { name: string } }>;
}

export default function CommandPalette({
  candidates = [],
  clients = [],
  jobs = [],
}: CommandPaletteProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Build combined items list
  const allItems: CommandItem[] = [
    ...NAV_ITEMS.map((item) => ({ ...item, id: item.href, icon: item.icon })),
    ...candidates.map((c) => ({
      id: c.id,
      label: c.name,
      description: c.current_position,
      icon: Users,
      href: `/command-center/candidates/${c.id}`,
      category: "candidate",
    })),
    ...clients.map((c) => ({
      id: c.id,
      label: c.name,
      description: "Client",
      icon: Building2,
      href: `/command-center/clients/${c.id}`,
      category: "client",
    })),
    ...jobs.map((j) => ({
      id: j.id,
      label: j.title,
      description: j.clients?.name,
      icon: Briefcase,
      href: `/command-center/decision-queue`,
      category: "job",
    })),
  ];

  const filtered = query
    ? allItems.filter(
        (item) =>
          item.label.toLowerCase().includes(query.toLowerCase()) ||
          item.description?.toLowerCase().includes(query.toLowerCase()) ||
          item.category.toLowerCase().includes(query.toLowerCase())
      )
    : NAV_ITEMS.map((item) => ({ ...item, id: item.href }));

  const groupedItems = filtered.reduce<Record<string, CommandItem[]>>((acc, item) => {
    const cat = item.category;
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {});

  const flatFiltered = Object.values(groupedItems).flat();

  const handleSelect = useCallback(
    (item: CommandItem) => {
      if (item.href) router.push(item.href);
      if (item.action) item.action();
      setOpen(false);
      setQuery("");
    },
    [router]
  );

  // Keyboard shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setOpen(false);
        setQuery("");
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Arrow key navigation
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelected((s) => Math.min(s + 1, flatFiltered.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelected((s) => Math.max(s - 1, 0));
      } else if (e.key === "Enter" && flatFiltered[selected]) {
        handleSelect(flatFiltered[selected]);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, flatFiltered, selected, handleSelect]);

  useEffect(() => {
    setSelected(0);
  }, [query]);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 50);
  }, [open]);

  const categoryLabels: Record<string, string> = {
    navigation: "Navigation",
    candidate: "Candidates",
    client: "Clients",
    job: "Jobs",
  };

  return (
    <>
      <AnimatePresence>
        {open && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-[1000] bg-black/60 command-backdrop"
              onClick={() => { setOpen(false); setQuery(""); }}
            />

            {/* Palette */}
            <motion.div
              initial={{ opacity: 0, scale: 0.96, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: -10 }}
              transition={{ duration: 0.15, ease: "easeOut" }}
              className="fixed top-[20vh] left-1/2 -translate-x-1/2 z-[1001] w-full max-w-xl"
              role="dialog"
              aria-label="Command palette"
              aria-modal="true"
            >
              <div className="glass-card border-zinc-700/60 overflow-hidden shadow-2xl shadow-black/50">
                {/* Search input */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-zinc-800">
                  <Search className="w-4 h-4 text-zinc-500 flex-shrink-0" />
                  <input
                    ref={inputRef}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search candidates, clients, jobs, pages…"
                    className="flex-1 bg-transparent text-sm text-zinc-200 placeholder-zinc-600 outline-none"
                    aria-label="Search"
                    autoComplete="off"
                    spellCheck={false}
                  />
                  <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 text-xs font-mono text-zinc-600 bg-zinc-800 rounded border border-zinc-700">
                      ESC
                    </kbd>
                    <button onClick={() => { setOpen(false); setQuery(""); }} aria-label="Close command palette">
                      <X className="w-4 h-4 text-zinc-600 hover:text-zinc-400 transition-colors" />
                    </button>
                  </div>
                </div>

                {/* Results */}
                <div className="max-h-80 overflow-y-auto py-2" role="listbox">
                  {flatFiltered.length === 0 ? (
                    <div className="px-4 py-8 text-center text-zinc-600 text-sm">
                      No results for &quot;{query}&quot;
                    </div>
                  ) : (
                    Object.entries(groupedItems).map(([category, items]) => (
                      <div key={category}>
                        <div className="px-4 py-1.5 text-xs font-medium text-zinc-600 uppercase tracking-wider">
                          {categoryLabels[category] || category}
                        </div>
                        {items.map((item) => {
                          const globalIdx = flatFiltered.findIndex((f) => f.id === item.id);
                          const Icon = item.icon;
                          return (
                            <button
                              key={item.id}
                              onClick={() => handleSelect(item)}
                              role="option"
                              aria-selected={globalIdx === selected}
                              className={cn(
                                "w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors text-sm",
                                globalIdx === selected
                                  ? "bg-indigo-500/10 text-indigo-300"
                                  : "text-zinc-300 hover:bg-zinc-800/50"
                              )}
                            >
                              <Icon className="w-4 h-4 flex-shrink-0 opacity-60" />
                              <span className="flex-1 truncate">{item.label}</span>
                              {item.description && (
                                <span className="text-xs text-zinc-600 truncate max-w-[120px]">
                                  {item.description}
                                </span>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    ))
                  )}
                </div>

                {/* Footer */}
                <div className="px-4 py-2 border-t border-zinc-800 flex items-center gap-4 text-xs text-zinc-600">
                  <span className="flex items-center gap-1">
                    <kbd className="px-1 py-0.5 font-mono bg-zinc-800 rounded border border-zinc-700">↑↓</kbd>
                    navigate
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1 py-0.5 font-mono bg-zinc-800 rounded border border-zinc-700">↵</kbd>
                    select
                  </span>
                  <span className="flex items-center gap-1 ml-auto">
                    <Command className="w-3 h-3" />
                    <span>K</span>
                    <span>to toggle</span>
                  </span>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
