"use client";

import { useMemo } from "react";
import { Copy, Terminal, Server, Clock, ShieldCheck, X } from "lucide-react";

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

export default function IncidentDetails({
    incident,
    onClose,
}: {
    incident: Incident;
    onClose: () => void;
}) {
    const color = severityColor[incident.severity] || "#94a3b8";

    return (
        <div className="rounded-xl border border-slate-700 overflow-hidden h-fit sticky top-6 shadow-2xl animate-slide-in bg-slate-900">

            {/* Header */}
            <div className="px-6 py-4 flex items-center justify-between border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-slate-800 border border-slate-700 text-lg font-bold" style={{ color: color }}>
                        {incident.severity[0]}
                    </div>
                    <div>
                        <p className="text-xs font-bold uppercase tracking-widest text-slate-500">
                            Incident Details
                        </p>
                        <p className="font-mono font-bold text-base text-slate-200">
                            {incident.incident_id}
                        </p>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    className="w-8 h-8 rounded-full hover:bg-slate-800 flex items-center justify-center text-slate-400 transition-colors"
                >
                    <X size={18} />
                </button>
            </div>

            {/* Body */}
            <div className="p-6 flex flex-col gap-6 max-h-[80vh] overflow-y-auto custom-scrollbar">

                {/* Severity + Confidence Grid */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-xl p-4 border bg-slate-900/50" style={{ borderColor: `${color}30` }}>
                        <p className="text-xs mb-1 text-slate-400 uppercase tracking-wider font-semibold">Severity</p>
                        <p className="text-xl font-bold" style={{ color }}>{incident.severity}</p>
                    </div>
                    <div className="rounded-xl p-4 border border-slate-700 bg-slate-800/50">
                        <p className="text-xs mb-1 text-slate-400 uppercase tracking-wider font-semibold">Confidence</p>
                        <div className="flex items-center gap-2">
                            <ShieldCheck size={18} className="text-emerald-400" />
                            <p className="text-xl font-bold text-slate-200">
                                {(incident.confidence * 100).toFixed(1)}%
                            </p>
                        </div>
                    </div>
                </div>

                {/* Summary */}
                <div className="space-y-2">
                    <p className="text-xs font-bold uppercase tracking-widest text-slate-500 flex items-center gap-2">
                        <Terminal size={14} /> Executive Summary
                    </p>
                    <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700 text-sm leading-relaxed text-slate-300">
                        {incident.summary}
                    </div>
                </div>

                {/* Host */}
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-700">
                    <span className="text-xs text-slate-400 uppercase font-bold tracking-wider flex items-center gap-2">
                        <Server size={14} /> Affected Host
                    </span>
                    <span className="font-mono text-sm text-sky-400 bg-sky-950/30 px-2 py-0.5 rounded border border-sky-900">
                        {incident.host}
                    </span>
                </div>

                {/* MITRE Tags */}
                {incident.mitre_techniques?.length > 0 && (
                    <div className="space-y-2">
                        <p className="text-xs font-bold uppercase tracking-widest text-slate-500">
                            MITRE ATT&CK
                        </p>
                        <div className="flex flex-wrap gap-2">
                            {incident.mitre_techniques.map((t) => (
                                <span key={t} className="px-3 py-1 rounded-md text-xs font-mono font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 hover:bg-indigo-500/20 transition-colors cursor-default">
                                    {t}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Timeline */}
                {incident.timeline?.length > 0 && (
                    <div className="space-y-3">
                        <p className="text-xs font-bold uppercase tracking-widest text-slate-500 flex items-center gap-2">
                            <Clock size={14} /> Attack Timeline
                        </p>
                        <div className="relative pl-4 space-y-4 border-l border-slate-700 ml-1">
                            {incident.timeline.map((event, idx) => (
                                <div key={idx} className="relative">
                                    <div className="absolute -left-[21px] top-1.5 w-3 h-3 rounded-full bg-slate-800 border-2 border-sky-500" />
                                    <p className="text-xs text-slate-400 leading-relaxed group-hover:text-slate-200 transition-colors">
                                        {event}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

            </div>

            {/* Footer */}
            <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/50 text-xs text-slate-500 flex justify-between items-center">
                <span>ID: {incident.incident_id}</span>
                <span>{new Date(incident.timestamp).toLocaleString()}</span>
            </div>
        </div>
    );
}
