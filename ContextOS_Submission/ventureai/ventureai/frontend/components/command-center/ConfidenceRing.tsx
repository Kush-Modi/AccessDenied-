"use client";
import { cn, formatConfidenceInt, getConfidenceColor } from "@/lib/utils";

interface ConfidenceRingProps {
  value: number; // 0–1
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
}

export default function ConfidenceRing({ value, size = 64, strokeWidth = 5, showLabel = true }: ConfidenceRingProps) {
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - value * circumference;

  const color =
    value >= 0.8 ? "#1D8F88" :
    value >= 0.6 ? "#FFC94B" :
    "#F17A7E";

  return (
    <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`Confidence: ${formatConfidenceInt(value)}`}>
        {/* Track */}
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#4E5D5A" strokeOpacity="0.1" strokeWidth={strokeWidth} />
        {/* Fill */}
        <circle
          cx={size / 2} cy={size / 2} r={radius} fill="none"
          stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1)" }}
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn("text-xs font-mono font-bold", getConfidenceColor(value))}>
            {formatConfidenceInt(value)}
          </span>
        </div>
      )}
    </div>
  );
}
