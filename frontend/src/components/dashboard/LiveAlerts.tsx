"use client";

import React from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { Bell, Shield, Info, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

const alerts = [
  {
    type: "report",
    message: "New medical report in Block C",
    time: "2m ago",
    icon: Info,
    color: "bg-cyan-500",
  },
  {
    type: "match",
    message: "Volunteer matched to Task #842",
    time: "5m ago",
    icon: Shield,
    color: "bg-emerald-500",
  },
  {
    type: "urgency",
    message: "District 2 heat level rising",
    time: "12m ago",
    icon: AlertTriangle,
    color: "bg-amber-500",
  },
  {
    type: "system",
    message: "Predictive model recalibrated",
    time: "20m ago",
    icon: Bell,
    color: "bg-primary",
  },
];

export const LiveAlerts = () => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
          Live Operational Pulse
        </h3>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-bold text-emerald-500 uppercase">Live</span>
        </div>
      </div>

      <div className="space-y-4">
        {alerts.map((alert, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex gap-4 group"
          >
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full ${alert.color} flex items-center justify-center border-2 border-background z-10 scale-90 group-hover:scale-100 transition-transform`}>
                <alert.icon className="w-4 h-4 text-white" />
              </div>
              {i < alerts.length - 1 && <div className="w-px flex-1 bg-white/[0.06] my-1" />}
            </div>
            <div className="pb-4">
              <p className="text-xs font-bold leading-tight mb-1 group-hover:text-primary transition-colors">
                {alert.message}
              </p>
              <p className="text-[10px] text-muted-foreground">{alert.time}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
