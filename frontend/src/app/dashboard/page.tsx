"use client";

import React from "react";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { KPIGrid } from "@/components/dashboard/KPIGrid";
import { UrgentQueue } from "@/components/dashboard/UrgentQueue";
import { LiveAlerts } from "@/components/dashboard/LiveAlerts";
import { GlassCard } from "@/components/shared/GlassCard";
import { Map as MapIcon, Maximize2 } from "lucide-react";
import { reportsApi } from "@/lib/api-client";
import dynamic from "next/dynamic";

const EliteMap = dynamic(() => import("@/components/dashboard/EliteMap"), {
  ssr: false,
});

export default function DashboardPage() {
  const [reports, setReports] = React.useState<any[]>([]);
  
  React.useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await reportsApi.getAll();
        setReports(response.data);
      } catch (err) {
        console.error("Failed to fetch reports for map:", err);
      }
    };
    fetchReports();
  }, []);

  const mapMarkers = reports.map(r => ({
    lat: r.latitude || 17.3850,
    lng: r.longitude || 78.4867,
    title: r.title
  }));

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <DashboardHeader 
        title="Admin Command Center" 
        subtitle="AI-Powered Mission Control & Regional Intelligence Overview" 
      />

      {/* Primary Metrics Row */}
      <KPIGrid />

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Content Area: Map & Intelligence */}
        <div className="lg:col-span-2 space-y-8">
          <GlassCard className="p-0 border-white/[0.04] overflow-hidden min-h-[450px] relative group h-full">
            <div className="absolute top-4 left-4 z-20 flex items-center gap-3">
              <div className="bg-background/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2 text-white">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-widest ">Live Operations Map</span>
              </div>
            </div>
            
            <div className="absolute top-4 right-4 z-20">
               <button className="bg-background/80 backdrop-blur-md p-2 rounded-lg border border-white/10 hover:text-primary transition-colors text-white">
                 <Maximize2 className="w-4 h-4" />
               </button>
            </div>

            <div className="absolute inset-0 z-10 pointer-events-auto">
              {/* @ts-ignore */}
              <EliteMap markers={mapMarkers} />
            </div>

            {/* Map Overlay Controls */}
            <div className="absolute bottom-6 left-6 z-20 flex flex-col gap-2">
               <GlassCard className="p-3 bg-background/80 backdrop-blur-md border-white/10 w-48">
                 <div className="text-[10px] font-black uppercase text-muted-foreground mb-3 tracking-[0.2em]">Map Legend</div>
                 <div className="space-y-2">
                    <div className="flex items-center gap-2">
                       <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                       <span className="text-[9px] font-bold">Critical Case</span>
                    </div>
                    <div className="flex items-center gap-2">
                       <div className="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_rgba(255,0,102,0.5)]" />
                       <span className="text-[9px] font-bold">Active Mission</span>
                    </div>
                 </div>
               </GlassCard>
            </div>
            
            <div className="absolute bottom-6 right-6 z-20">
               <button className="bg-primary text-white rounded-full px-6 py-2 text-[10px] font-black uppercase tracking-widest shadow-xl hover:scale-105 transition-transform flex items-center gap-2">
                  <MapIcon className="w-3 h-3" />
                  Fullscreen Intel
               </button>
            </div>
          </GlassCard>

          <div className="grid md:grid-cols-2 gap-8">
             <GlassCard className="p-6">
                <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-6">Regional Distribution</h3>
                <div className="h-48 flex items-center justify-center border border-dashed border-white/10 rounded-xl bg-white/[0.01]">
                   <span className="text-[10px] font-bold uppercase text-muted-foreground">Resource Chart Influx...</span>
                </div>
             </GlassCard>
             <GlassCard className="p-6">
                <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-6">AI Priority Trend</h3>
                <div className="h-48 flex items-center justify-center border border-dashed border-white/10 rounded-xl bg-white/[0.01]">
                   <span className="text-[10px] font-bold uppercase text-muted-foreground">Urgency Velocity Plotting...</span>
                </div>
             </GlassCard>
          </div>
        </div>

        {/* Sidebar Analytics */}
        <div className="space-y-8">
          <GlassCard className="p-6">
            <UrgentQueue />
          </GlassCard>
          
          <GlassCard className="p-6">
            <LiveAlerts />
          </GlassCard>
          
          <GlassCard className="p-6 border-primary/20 bg-primary/5">
             <h3 className="text-xs font-black uppercase tracking-[0.2em] text-primary mb-4">AI Intelligence Note</h3>
             <p className="text-[11px] leading-relaxed text-blue-100/70">
               Current analysis predicts a <span className="text-white font-bold">12% increase</span> in food insecurity in the East Sector over the next 48 hours. Recommend proactive resource dispatch to Hub-B.
             </p>
             <button className="mt-4 text-[10px] font-black uppercase text-primary hover:underline">Read Full Analysis</button>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
