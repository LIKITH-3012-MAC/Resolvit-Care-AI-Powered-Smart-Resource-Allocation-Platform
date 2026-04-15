"use client";

import React, { useEffect, useState } from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { MoreHorizontal, MapPin, Clock } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { reportsApi } from "@/lib/api-client";
import { formatDistanceToNow } from "date-fns";

// Simple Badge fallback for premium glass UI
const Badge = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${className}`}>
    {children}
  </div>
);

export const UrgentQueue = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await reportsApi.getAll({ limit: 5 });
        setItems(response.data);
      } catch (err) {
        console.error("Failed to fetch urgent queue", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-4 w-32 bg-white/5 rounded" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-white/[0.02] border border-white/5 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
          Urgent Action Queue
        </h3>
        <button className="text-[10px] font-bold text-primary hover:underline">View All</button>
      </div>

      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {items.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: i * 0.1 }}
            >
              <GlassCard className="p-4 bg-white/[0.02] border-white/[0.04] hover:bg-white/[0.04] cursor-pointer group">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-3">
                    <div className="text-primary font-mono text-[10px] bg-primary/10 px-2 py-0.5 rounded">
                      REP-{item.id}
                    </div>
                    <div className="text-xs font-bold truncate max-w-[200px]">{item.title || "Untitled Report"}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`text-xs font-black ${item.urgency_score > 0.8 ? 'text-red-400' : 'text-amber-400'}`}>
                      {Math.round((item.urgency_score || 0) * 100)}
                    </div>
                    <div className="w-1 h-1 rounded-full bg-white/20" />
                    <MoreHorizontal className="w-3 h-3 text-muted-foreground" />
                  </div>
                </div>

                <div className="flex items-center justify-between mt-4">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                      <MapPin className="w-3 h-3" />
                      {item.location_name}
                    </div>
                    <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      {formatDistanceToNow(new Date(item.created_at))} ago
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className="bg-white/[0.05] border border-white/[0.08]">
                      {item.status}
                    </Badge>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};
