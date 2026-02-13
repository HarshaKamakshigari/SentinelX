"use client";

import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Radar, RefreshCcw, ShieldCheck } from "lucide-react";
import StatsCards from "@/components/StatsCards";
import IncidentTable from "@/components/IncidentTable";
import IncidentDetails from "@/components/IncidentDetails";
import DashboardCharts from "@/components/DashboardCharts";

const API_BASE = "http://localhost:8001";

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

export default function DashboardPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selected, setSelected] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const fetchIncidents = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/incidents`);
      setIncidents(res.data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch {
      // Backend might not be running yet — silent fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 3000);
    return () => clearInterval(interval);
  }, [fetchIncidents]);

  // Severity counts
  const counts = {
    total: incidents.length,
    critical: incidents.filter((i) => i.severity === "CRITICAL").length,
    high: incidents.filter((i) => i.severity === "HIGH").length,
    medium: incidents.filter((i) => i.severity === "MEDIUM").length,
    low: incidents.filter((i) => i.severity === "LOW").length,
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans selection:bg-sky-500/30">

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/80 backdrop-blur-xl px-6 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-gradient-to-br from-sky-400 to-indigo-600 shadow-lg shadow-sky-500/20">
            <Radar className="text-white" size={20} />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white leading-tight">
              SentinelX <span className="opacity-50 font-medium">SOC</span>
            </h1>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold">
              Live Threat Monitoring
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-emerald-400 font-semibold">SYSTEM ONLINE</span>
          </div>
          <div className="flex items-center gap-2">
            <RefreshCcw size={12} className="animate-spin-slow" />
            <span>Updated: {lastUpdated}</span>
          </div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto p-6 flex flex-col gap-6">
        {/* Stats Row */}
        <StatsCards counts={counts} />

        {/* Charts Row */}
        <DashboardCharts incidents={incidents} />

        {/* Main Content (Table + Detail) */}
        <div className="flex gap-6 items-start">

          {/* Incident Table */}
          <div className={`transition-all duration-500 ease-in-out ${selected ? "w-3/5" : "w-full"}`}>
            {loading ? (
              <div className="flex items-center justify-center py-32 rounded-xl border border-dashed border-slate-700 bg-slate-900/50">
                <div className="flex flex-col items-center gap-4">
                  <div className="w-10 h-10 border-4 border-slate-700 border-t-sky-500 rounded-full animate-spin" />
                  <span className="text-slate-400 text-sm font-medium animate-pulse">Establishing secure uplink...</span>
                </div>
              </div>
            ) : incidents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-32 rounded-xl border border-dashed border-slate-700 bg-slate-900/50 gap-4 group cursor-default hover:bg-slate-800/30 transition-colors">
                <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <ShieldCheck size={32} className="text-slate-600 group-hover:text-emerald-500 transition-colors" />
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-slate-300">All Systems Secure</p>
                  <p className="text-sm text-slate-500">No active threats detected in the environment.</p>
                </div>
              </div>
            ) : (
              <div className="rounded-xl border border-slate-700 bg-slate-900 shadow-xl overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
                  <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Active Incidents</h3>
                  <span className="px-2 py-0.5 rounded text-xs bg-slate-700 text-slate-300 font-mono">
                    {incidents.length}
                  </span>
                </div>
                <IncidentTable
                  incidents={incidents}
                  selected={selected}
                  onSelect={setSelected}
                />
              </div>
            )}
          </div>

          {/* Detail Panel */}
          {selected && (
            <div className="w-2/5 sticky top-24">
              <IncidentDetails
                incident={selected}
                onClose={() => setSelected(null)}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
