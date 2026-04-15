"use client";

import React from "react";
import { Search, Bell, UserCircle, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/shared/GlassCard";

export const DashboardHeader = ({ title, subtitle }: { title: string; subtitle?: string }) => {
  return (
    <header className="flex items-center justify-between mb-8 sticky top-0 z-40 bg-background/20 backdrop-blur-sm py-4">
      <div>
        <h1 className="text-2xl font-black tracking-tight">{title}</h1>
        {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-6">
        <div className="hidden md:flex items-center bg-white/[0.05] border border-white/[0.08] px-4 py-2 rounded-xl w-64">
          <Search className="w-4 h-4 text-muted-foreground mr-2" />
          <input
            type="text"
            placeholder="Search reports or tasks..."
            className="bg-transparent border-none outline-none text-xs w-full"
          />
        </div>

        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="relative group">
            <Bell className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-background animate-pulse" />
          </Button>
          
          <div className="w-px h-6 bg-white/[0.06] mx-2" />
          
          <Button className="rounded-xl gap-2 h-10 px-4 bg-primary hover:bg-primary/90 hidden sm:flex">
            <Plus className="w-4 h-4" />
            New Report
          </Button>
          
          <div className="flex items-center gap-3 bg-white/[0.05] border border-white/[0.08] p-1.5 rounded-xl pl-3">
            <div className="hidden lg:block text-right">
              <div className="text-[10px] font-bold leading-none mb-1">Likith Naidu</div>
              <div className="text-[8px] text-muted-foreground uppercase tracking-widest leading-none">NGO Admin</div>
            </div>
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-bold text-xs uppercase">
              LN
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
