"use client";

import React from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { AlertCircle, Users, Zap, Clock, TrendingUp } from "lucide-react";

const kpis = [
  {
    label: "Active Crisis Zones",
    value: "14",
    change: "+2 since yesterday",
    icon: AlertCircle,
    color: "text-red-400",
    glow: "shadow-[0_0_20px_rgba(239,68,68,0.15)]",
  },
  {
    label: "Unresolved Cases",
    value: "128",
    change: "-12 from avg",
    icon: Zap,
    color: "text-primary",
    glow: "shadow-[0_0_20px_rgba(139,92,246,0.15)]",
  },
  {
    label: "Volunteer Readiness",
    value: "82%",
    change: "342 active now",
    icon: Users,
    color: "text-cyan-400",
    glow: "shadow-[0_0_20px_rgba(34,211,238,0.15)]",
  },
  {
    label: "Avg. Response Time",
    value: "1.2h",
    change: "+5m latency",
    icon: Clock,
    color: "text-amber-400",
    glow: "shadow-[0_0_20px_rgba(251,191,36,0.15)]",
  },
];

export const KPIGrid = () => {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {kpis.map((kpi, i) => (
        <GlassCard key={i} className={`p-6 border-white/[0.04] relative group hover:scale-[1.02] ${kpi.glow}`}>
          <div className="flex justify-between items-start mb-4">
            <div className={`p-3 rounded-lg bg-white/[0.03] border border-white/[0.06] group-hover:scale-110 transition-transform`}>
              <kpi.icon className={`w-5 h-5 ${kpi.color}`} />
            </div>
            <TrendingUp className="w-4 h-4 text-muted-foreground opacity-20" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">
              {kpi.label}
            </h3>
            <div className="text-3xl font-black tracking-tight">{kpi.value}</div>
            <p className="text-[10px] font-medium text-muted-foreground mt-2 flex items-center gap-1">
              <span className={kpi.change.includes("+") && kpi.color.includes("red") ? "text-red-400" : "text-emerald-400"}>
                {kpi.change}
              </span>
            </p>
          </div>
        </GlassCard>
      ))}
    </div>
  );
};
