import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Geist_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ContextOS — Enterprise AI Operating System",
  description:
    "The Context Layer for Workforce Intelligence. Hybrid Retrieval, Planner Memory, Business Rules, Human Approval — one operating system.",
  keywords: ["AI", "recruiting", "intelligence", "NBA", "enterprise", "LangGraph"],
  openGraph: {
    title: "ContextOS",
    description: "Enterprise AI Operating System for Workforce Intelligence",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <body className="antialiased">
        {/* Grain texture overlay */}
        <div className="grain-overlay" aria-hidden="true" />
        {children}
      </body>
    </html>
  );
}
