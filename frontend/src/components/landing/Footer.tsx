"use client";

import React from "react";
import { ShieldCheck, Mail, Globe, Activity } from "lucide-react";
import Link from "next/link";

export const Footer = () => {
  return (
    <footer className="bg-background border-t border-white/[0.06] pt-20 pb-10">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
          <div className="col-span-1 lg:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-black tracking-tighter uppercase leading-none">
                Resolvit <span className="text-primary">Care</span>
              </span>
            </Link>
            <p className="text-muted-foreground text-sm leading-relaxed mb-6">
              Empowering NGOs and relief organizations with AI-driven resource orchestration and civic intelligence.
            </p>
            <div className="flex gap-4">
              <Link href="#" className="p-2 rounded-lg bg-white/[0.03] text-muted-foreground hover:text-primary hover:bg-white/[0.06] transition-all">
                <Globe className="w-4 h-4" />
              </Link>
              <Link href="#" className="p-2 rounded-lg bg-white/[0.03] text-muted-foreground hover:text-primary hover:bg-white/[0.06] transition-all">
                <Activity className="w-4 h-4" />
              </Link>
              <Link href="#" className="p-2 rounded-lg bg-white/[0.03] text-muted-foreground hover:text-primary hover:bg-white/[0.06] transition-all">
                <ShieldCheck className="w-4 h-4" />
              </Link>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest mb-6">Platform</h4>
            <ul className="space-y-4">
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">NGO Dashboard</Link></li>
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">Volunteer Portal</Link></li>
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">Impact Analytics</Link></li>
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">Crisis Heatmap</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest mb-6">Company</h4>
            <ul className="space-y-4">
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">About Mission</Link></li>
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">Our Network</Link></li>
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">Global Impact</Link></li>
              <li><Link href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">Case Studies</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-bold uppercase tracking-widest mb-6">System Status</h4>
            <div className="bg-white/[0.03] p-4 rounded-xl border border-white/[0.06]">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs font-bold uppercase tracking-wider text-green-500">All Systems Operational</span>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Platform uptime: 99.98% over the last 30 days. High reliability for critical missions.
              </p>
            </div>
          </div>
        </div>
        
        <div className="pt-10 border-t border-white/[0.06] flex flex-col md:flex-row justify-between items-center gap-6">
          <p className="text-xs text-muted-foreground">
            © 2026 Resolvit Care AI Systems. Developed by <span className="text-primary font-bold">Likith Naidu Anumakonda</span>.
          </p>
          <div className="flex gap-8">
            <Link href="#" className="text-xs text-muted-foreground hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="#" className="text-xs text-muted-foreground hover:text-white transition-colors">Terms of Service</Link>
            <Link href="#" className="text-xs text-muted-foreground hover:text-white transition-colors">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
