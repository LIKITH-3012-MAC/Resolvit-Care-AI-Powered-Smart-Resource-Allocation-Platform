"use client";

import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/shared/GlassCard";
import { ArrowRight, BarChart3, Users, Zap } from "lucide-react";

export const Hero = () => {
  return (
    <section className="relative min-height-[90vh] flex items-center pt-32 pb-20 overflow-hidden">
      {/* Background Ambient Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[10%] right-[-5%] w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.05] border border-white/[0.1] mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-xs font-bold tracking-wider uppercase text-muted-foreground">
                Resolvit Care AI Elite System
              </span>
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-black tracking-tight mb-6 leading-[1.1]">
              Transforming <span className="text-gradient">Scattered Data</span> into Real-time Action
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed max-w-xl">
              AI-powered prioritization, volunteer orchestration, and predictive resource allocation for social impact at scale.
            </p>
            
            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="rounded-full px-8 gap-2 group">
                Request Demo <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button size="lg" variant="outline" className="rounded-full px-8 bg-white/[0.02] border-white/[0.1] backdrop-blur-sm">
                Explore Dashboard
              </Button>
            </div>
            
            <div className="mt-12 flex items-center gap-8 border-t border-white/[0.06] pt-8">
              <div>
                <div className="text-2xl font-black">1.2k+</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider font-bold">Active Cases</div>
              </div>
              <div className="w-px h-8 bg-white/[0.06]" />
              <div>
                <div className="text-2xl font-black">94%</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider font-bold">Res. Rate</div>
              </div>
              <div className="w-px h-8 bg-white/[0.06]" />
              <div>
                <div className="text-2xl font-black">300+</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider font-bold">NGO Partners</div>
              </div>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="relative"
          >
            {/* Main Preview Card */}
            <GlassCard className="p-0 overflow-hidden relative z-10 border-primary/20 bg-background/40">
              <div className="bg-white/[0.03] p-4 border-b border-white/[0.06] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500/20" />
                    <div className="w-3 h-3 rounded-full bg-amber-500/20" />
                    <div className="w-3 h-3 rounded-full bg-green-500/20" />
                  </div>
                  <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest ml-4">
                    NGO Command Center v2.0
                  </span>
                </div>
                <div className="flex items-center gap-4">
                   <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                </div>
              </div>
              
              <div className="p-8">
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-white/[0.03] p-4 rounded-xl border border-white/[0.06]">
                    <div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Impact Score</div>
                    <div className="text-2xl font-black tracking-tight text-gradient">84.2</div>
                  </div>
                  <div className="bg-white/[0.03] p-4 rounded-xl border border-white/[0.06]">
                    <div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Volunteers</div>
                    <div className="text-2xl font-black tracking-tight">342</div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="h-2 w-full bg-white/[0.05] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: "72%" }}
                      transition={{ duration: 1.5, delay: 0.5 }}
                      className="h-full bg-primary"
                    />
                  </div>
                  <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider">
                    <span className="text-muted-foreground">Global Resolution Progress</span>
                    <span className="text-primary">72%</span>
                  </div>
                </div>
                
                <div className="mt-8 pt-8 border-t border-white/[0.06] flex items-center justify-between">
                  <div className="flex -space-x-3">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="w-8 h-8 rounded-full border-2 border-background bg-secondary flex items-center justify-center text-[10px] font-bold">
                        U{i}
                      </div>
                    ))}
                    <div className="w-8 h-8 rounded-full border-2 border-background bg-primary/20 text-primary flex items-center justify-center text-[10px] font-bold">
                      +8
                    </div>
                  </div>
                  <span className="text-[11px] font-medium text-muted-foreground tracking-tight">
                    Coordination Team Active
                  </span>
                </div>
              </div>
            </GlassCard>
            
            {/* Floating Elements */}
            <motion.div
              animate={{ y: [0, -15, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -top-10 -right-6 z-20"
            >
              <GlassCard className="p-3 bg-primary/10 border-primary/20 backdrop-blur-md">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="text-[10px] font-bold uppercase text-primary">Emergency</div>
                    <div className="text-xs font-bold">Alert Detected</div>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
            
            <motion.div
              animate={{ y: [0, 15, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
              className="absolute -bottom-8 -left-8 z-20"
            >
              <GlassCard className="p-3 bg-cyan-500/10 border-cyan-500/20 backdrop-blur-md">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-cyan-500 flex items-center justify-center">
                    <BarChart3 className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="text-[10px] font-bold uppercase text-cyan-400">Analysis</div>
                    <div className="text-xs font-bold">Hotspot Map Live</div>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
