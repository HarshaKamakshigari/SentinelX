"use client";

import { AlertTriangle, Shield, CheckCircle, Flame } from "lucide-react";

interface Incident {
    incident_id: string;
    timestamp: string;
    host: string;
    summary: string;
    severity: string;
    confidence: number;
    mitre_techniques: string[];
    timeline: string[];
    agents_invoked: string[];
    details: Record<string, unknown>;
}

const severityColor: Record<string, string> = {
    CRITICAL: "#dc2626",
    HIGH: "#ef4444",
    MEDIUM: "#f97316",
    LOW: "#22c55e",
};

const severityBg: Record<string, string> = {
    CRITICAL: "bg-red-500/10",
    HIGH: "bg-red-500/10",
    MEDIUM: "bg-orange-500/10",
    LOW: "bg-emerald-500/10",
};

const severityText: Record<string, string> = {
    CRITICAL: "text-red-500",
    HIGH: "text-red-500",
    MEDIUM: "text-orange-500",
    LOW: "text-emerald-500",
};

function formatTime(ts: string) {
    try {
        const d = new Date(ts);
        return d.toLocaleString("en-IN", {
            day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
        });
    } catch {
        return ts;
    }
}

export default function IncidentTable({
    incidents,
    selected,
    onSelect,
}: {
    incidents: Incident[];
    selected: Incident | null;
    onSelect: (i: Incident) => void;
}) {
    return (
        <div className="overflow-hidden">
            {/* Table header */}
            <div className="grid grid-cols-12 gap-2 px-4 py-3 text-xs font-bold uppercase tracking-wider text-slate-500 border-b border-slate-800 bg-slate-900/50">
                <div className="col-span-2">ID</div>
                <div className="col-span-2">Host</div>
                <div className="col-span-2">Severity</div>
                <div className="col-span-3">Confidence</div>
                <div className="col-span-3 text-right">Time</div>
            </div>

            {/* Table rows */}
            <div className="max-h-[60vh] overflow-y-auto custom-scrollbar">
                {incidents.map((inc, idx) => {
                    const isSelected = selected?.incident_id === inc.incident_id;
                    return (
                        <div
                            key={inc.incident_id}
                            onClick={() => onSelect(inc)}
                            className={`grid grid-cols-12 gap-2 px-4 py-3 border-b border-slate-800/50 cursor-pointer transition-all duration-200 group items-center ${isSelected ? "bg-sky-500/10 border-l-2 border-l-sky-500" : "hover:bg-slate-800/50 border-l-2 border-l-transparent"
                                } animate-fade-in-up`}
                            style={{ animationDelay: `${idx * 50}ms` }}
                        >
                            {/* ID */}
                            <div className="col-span-2 font-mono text-xs font-semibold text-slate-400 group-hover:text-sky-400 transition-colors">
                                {inc.incident_id}
                            </div>

                            {/* Host */}
                            <div className="col-span-2 text-xs text-slate-300 truncate font-medium">
                                {inc.host}
                            </div>

                            {/* Severity badge */}
                            <div className="col-span-2">
                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold border border-transparent ${severityBg[inc.severity]} ${severityText[inc.severity]}`}>
                                    {inc.severity === "CRITICAL" || inc.severity === "HIGH" ? <Flame size={10} /> : inc.severity === "MEDIUM" ? <AlertTriangle size={10} /> : <CheckCircle size={10} />}
                                    {inc.severity}
                                </span>
                            </div>

                            {/* Confidence */}
                            <div className="col-span-3 flex items-center gap-3">
                                <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ease-out ${inc.confidence > 0.8 ? "bg-gradient-to-r from-red-500 to-orange-500" :
                                                inc.confidence > 0.5 ? "bg-gradient-to-r from-orange-400 to-yellow-400" : "bg-emerald-500"
                                            }`}
                                        style={{ width: `${(inc.confidence * 100)}%` }}
                                    />
                                </div>
                                <span className="text-[10px] font-mono font-bold text-slate-500 tabular-nums">
                                    {(inc.confidence * 100).toFixed(0)}%
                                </span>
                            </div>

                            {/* Timestamp */}
                            <div className="col-span-3 text-right text-[10px] font-mono text-slate-500 group-hover:text-slate-400">
                                {formatTime(inc.timestamp)}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
