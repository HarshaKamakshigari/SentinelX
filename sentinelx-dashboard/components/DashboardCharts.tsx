"use client";

import { useMemo } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from "recharts";
import { ShieldAlert, Activity, Cpu } from "lucide-react";

interface Incident {
    incident_id: string;
    timestamp: string;
    severity: string;
    agents_invoked: string[];
}

const COLORS = {
    CRITICAL: "#dc2626",
    HIGH: "#ef4444",
    MEDIUM: "#f97316",
    LOW: "#22c55e",
};

export default function DashboardCharts({ incidents }: { incidents: Incident[] }) {
    // 1. Severity Distribution Data
    const severityData = useMemo(() => {
        const counts: Record<string, number> = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
        incidents.forEach((i) => {
            counts[i.severity] = (counts[i.severity] || 0) + 1;
        });
        return Object.entries(counts)
            .filter(([_, value]) => value > 0)
            .map(([name, value]) => ({ name, value }));
    }, [incidents]);

    // 2. Agent Usage Data
    const agentData = useMemo(() => {
        const counts: Record<string, number> = {};
        incidents.forEach((i) => {
            i.agents_invoked?.forEach((agent) => {
                counts[agent] = (counts[agent] || 0) + 1;
            });
        });
        return Object.entries(counts)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value);
    }, [incidents]);

    // 3. Incident Velocity (Timeline)
    const timelineData = useMemo(() => {
        const sorted = [...incidents].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
        const grouped: Record<string, number> = {};

        // Group by HH:MM
        sorted.forEach(i => {
            const time = new Date(i.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            grouped[time] = (grouped[time] || 0) + 1;
        });

        // If empty, return empty array
        if (Object.keys(grouped).length === 0) return [];

        return Object.entries(grouped).map(([time, count]) => ({ time, count }));
    }, [incidents]);

    if (incidents.length === 0) return null;

    return (
        <div className="grid grid-cols-3 gap-6 mb-6 animate-fade-in-up">

            {/* Chart 1: Threat Distribution */}
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-md shadow-xl">
                <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
                    <ShieldAlert className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Threat Landscape</h3>
                </div>
                <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={severityData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                                stroke="none"
                            >
                                {severityData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || "#8884d8"} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px' }}
                                itemStyle={{ color: '#e2e8f0' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Chart 2: Agent Activity */}
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-md shadow-xl">
                <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
                    <Cpu className="w-4 h-4 text-violet-400" />
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Agent Workload</h3>
                </div>
                <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={agentData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} vertical={false} />
                            <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <Tooltip
                                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px' }}
                            />
                            <Bar dataKey="value" fill="#818cf8" radius={[4, 4, 0, 0]} barSize={20} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Chart 3: Timeline */}
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 backdrop-blur-md shadow-xl">
                <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
                    <Activity className="w-4 h-4 text-sky-400" />
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Incident Velocity</h3>
                </div>
                <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={timelineData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} vertical={false} />
                            <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} allowDecimals={false} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px' }}
                            />
                            <Line
                                type="monotone"
                                dataKey="count"
                                stroke="#38bdf8"
                                strokeWidth={3}
                                dot={{ fill: '#0f172a', stroke: '#38bdf8', strokeWidth: 2, r: 4 }}
                                activeDot={{ r: 6, fill: '#38bdf8' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

        </div>
    );
}
