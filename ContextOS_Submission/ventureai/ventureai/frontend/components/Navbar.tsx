"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, Command, User, Moon, Sun, ChevronDown, X, CheckCircle, Zap, AlertCircle, Settings } from "lucide-react";
import Link from "next/link";
import { cn, timeAgo } from "@/lib/utils";

interface Notification {
  id: string;
  type: "approval" | "rejection" | "recommendation" | "system";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

interface NavbarProps {
  breadcrumbs?: Array<{ label: string; href?: string }>;
  onToggleTheme?: () => void;
  isDark?: boolean;
}

const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: "1",
    type: "approval",
    title: "Recommendation Approved",
    message: "Ananya Sharma to TechCorp (94% confidence)",
    timestamp: new Date(Date.now() - 120000),
    read: false,
  },
  {
    id: "2",
    type: "recommendation",
    title: "New Match Found",
    message: "Divya Menon matched with DataCo Inc.",
    timestamp: new Date(Date.now() - 600000),
    read: false,
  },
  {
    id: "3",
    type: "system",
    title: "System Health",
    message: "All services operational",
    timestamp: new Date(Date.now() - 3600000),
    read: true,
  },
];

const notifIcon = (type: Notification["type"]) => {
  switch (type) {
    case "approval": return <CheckCircle className="w-4 h-4 text-[#1D8F88]" />;
    case "rejection": return <X className="w-4 h-4 text-[#F17A7E]" />;
    case "recommendation": return <Zap className="w-4 h-4 text-[#1D8F88]" />;
    case "system": return <AlertCircle className="w-4 h-4 text-[#FFC94B]" />;
  }
};

export default function Navbar({ breadcrumbs = [], onToggleTheme, isDark = true }: NavbarProps) {
  const [showNotif, setShowNotif] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(MOCK_NOTIFICATIONS);

  const unread = notifications.filter((n) => !n.read).length;

  const markAllRead = () =>
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));

  // Keyboard shortcut hint display
  const [showKbHint, setShowKbHint] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setShowKbHint(true), 2000);
    const t2 = setTimeout(() => setShowKbHint(false), 6000);
    return () => { clearTimeout(t); clearTimeout(t2); };
  }, []);

  return (
    <header
      className="flex items-center justify-between px-5 h-12 border-b border-[#4E5D5A]/10 flex-shrink-0"
      style={{ background: "var(--color-canvas-secondary, #F4F1EA)" }}
      role="banner"
    >
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-1.5 text-sm" aria-label="Breadcrumb">
        {breadcrumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-1.5">
            {i > 0 && <span className="breadcrumb-sep text-[#6A756F]/40">/</span>}
            {crumb.href && i < breadcrumbs.length - 1 ? (
              <Link href={crumb.href} className="text-[#6A756F] hover:text-[#4E5D5A] transition-colors">
                {crumb.label}
              </Link>
            ) : (
              <span className={i === breadcrumbs.length - 1 ? "text-[#4E5D5A] font-medium" : "text-[#6A756F]"}>
                {crumb.label}
              </span>
            )}
          </span>
        ))}
      </nav>

      {/* Right side actions */}
      <div className="flex items-center gap-2">
        {/* ⌘K hint */}
        <AnimatePresence>
          {showKbHint && (
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="hidden sm:flex items-center gap-1 text-xs text-[#6A756F]/60 mr-2"
            >
              <Command className="w-3 h-3" />
              <span>K</span>
              <span className="text-[#6A756F]/40">to search</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Theme toggle */}
        {onToggleTheme && (
          <button
            onClick={onToggleTheme}
            className="w-8 h-8 flex items-center justify-center rounded-md text-[#6A756F] hover:text-[#4E5D5A] hover:bg-[#EFE8DE]/60 transition-colors"
            aria-label="Toggle theme"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        )}

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => { setShowNotif(!showNotif); setShowProfile(false); }}
            className="relative w-8 h-8 flex items-center justify-center rounded-md text-[#6A756F] hover:text-[#4E5D5A] hover:bg-[#EFE8DE]/60 transition-colors"
            aria-label={`Notifications ${unread > 0 ? `(${unread} unread)` : ""}`}
            aria-expanded={showNotif}
          >
            <Bell className="w-4 h-4" />
            {unread > 0 && (
              <span className="notification-badge absolute top-1 right-1 w-2 h-2 bg-[#1D8F88] rounded-full" />
            )}
          </button>

          <AnimatePresence>
            {showNotif && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowNotif(false)} />
                <motion.div
                  initial={{ opacity: 0, y: -8, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -8, scale: 0.97 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-10 w-80 bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl z-50 shadow-xl"
                  role="menu"
                  aria-label="Notifications"
                >
                  <div className="flex items-center justify-between px-4 py-3 border-b border-[#4E5D5A]/10">
                    <span className="text-sm font-medium text-[#4E5D5A]">Activity</span>
                    <button
                      onClick={markAllRead}
                      className="text-xs text-[#6A756F] hover:text-[#1D8F88] transition-colors"
                    >
                      Mark all read
                    </button>
                  </div>
                  <div className="max-h-72 overflow-y-auto">
                    {notifications.map((notif) => (
                      <div
                        key={notif.id}
                        className={cn(
                          "flex gap-3 px-4 py-3 border-b border-[#4E5D5A]/10 last:border-0",
                          !notif.read && "bg-[#1D8F88]/5"
                        )}
                        role="menuitem"
                      >
                        <div className="mt-0.5 flex-shrink-0">{notifIcon(notif.type)}</div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium text-[#4E5D5A] truncate">{notif.title}</p>
                          <p className="text-xs text-[#6A756F] mt-0.5 truncate">{notif.message}</p>
                        </div>
                        <div className="text-xs text-[#6A756F]/70 flex-shrink-0 ml-2">
                          {timeAgo(notif.timestamp)}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        {/* Profile menu */}
        <div className="relative">
          <button
            onClick={() => { setShowProfile(!showProfile); setShowNotif(false); }}
            className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-[#EFE8DE]/60 transition-colors"
            aria-label="Profile menu"
            aria-expanded={showProfile}
          >
            <div className="w-6 h-6 rounded-full bg-[#4A6163] flex items-center justify-center text-[#F7F5EF] text-xs font-medium">
              R
            </div>
            <span className="text-xs text-[#6A756F] hidden sm:block">Recruiter</span>
            <ChevronDown className="w-3 h-3 text-[#6A756F]/80" />
          </button>

          <AnimatePresence>
            {showProfile && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowProfile(false)} />
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-10 w-48 bg-[#F4F1EA] border border-[#4E5D5A]/10 rounded-xl z-50 shadow-xl py-1"
                  role="menu"
                >
                  <div className="px-4 py-2 border-b border-[#4E5D5A]/10 mb-1">
                    <p className="text-xs font-semibold text-[#4E5D5A]">Recruiter</p>
                    <p className="text-xs text-[#6A756F]">recruiter@contextos.ai</p>
                  </div>
                  <Link
                    href="/command-center/settings"
                    className="flex items-center gap-2 px-4 py-2 text-xs text-[#6A756F] hover:text-[#4E5D5A] hover:bg-[#EFE8DE]/60 transition-colors"
                    role="menuitem"
                    onClick={() => setShowProfile(false)}
                  >
                    <Settings className="w-3.5 h-3.5" />
                    Platform Configuration
                  </Link>
                  <button
                    className="w-full flex items-center gap-2 px-4 py-2 text-xs text-[#6A756F] hover:text-[#4E5D5A] hover:bg-[#EFE8DE]/60 transition-colors"
                    role="menuitem"
                  >
                    <User className="w-3.5 h-3.5" />
                    Profile
                  </button>
                  <div className="border-t border-[#4E5D5A]/10 mt-1 pt-1">
                    <button
                      className="w-full flex items-center gap-2 px-4 py-2 text-xs text-[#F17A7E] hover:bg-[#EFE8DE]/60 transition-colors"
                      role="menuitem"
                    >
                      Sign out
                    </button>
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
