"use client";

import { Activity, AlertOctagon, AlertTriangle, CheckCircle, Shield } from "lucide-react";

interface Counts {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
}

const CARDS = [
    { key: "total", label: "Total Incidents", color: "#38bdf8", icon: Activity },
    { key: "critical", label: "Critical", color: "#dc2626", icon: AlertOctagon },
    { key: "high", label: "High", color: "#ef4444", icon: AlertTriangle },
    { key: "medium", label: "Medium", color: "#f97316", icon: Shield },
    { key: "low", label: "Low", color: "#22c55e", icon: CheckCircle },
] as const;

export default function StatsCards({ counts }: { counts: Counts }) {
    return (
        <div className="grid grid-cols-5 gap-4">
            {CARDS.map(({ key, label, color, icon: Icon }) => {
                const value = counts[key as keyof Counts];
                const isActive = value > 0;

                return (
                    <div
                        key={key}
                        className={`rounded-xl p-4 border transition-all duration-300 relative overflow-hidden group ${isActive ? "shadow-lg" : "opacity-80"
                            }`}
                        style={{
                            background: "linear-gradient(145deg, #1e293b, #0f172a)",
                            borderColor: isActive ? color : "#334155",
                            boxShadow: isActive ? `0 4px 20px ${color}20` : "none",
                        }}
                    >
                        {/* Glow effect */}
                        {isActive && (
                            <div
                                className="absolute -right-4 -top-4 w-24 h-24 rounded-full blur-2xl opacity-20 pointer-events-none group-hover:opacity-30 transition-opacity"
                                style={{ background: color }}
                            />
                        )}

                        <div className="flex items-center justify-between mb-3 relative z-10">
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                                {label}
                            </span>
                            <Icon
                                size={20}
                                style={{ color: isActive ? color : "#64748b" }}
                                className={isActive ? "animate-pulse" : ""}
                            />
                        </div>

                        <div className="text-3xl font-bold tracking-tight relative z-10" style={{ color: isActive ? "#f8fafc" : "#94a3b8" }}>
                            {value}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
