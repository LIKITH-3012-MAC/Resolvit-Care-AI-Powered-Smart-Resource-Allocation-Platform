"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  FileText, 
  Map as MapIcon, 
  Users, 
  Package, 
  BarChart3, 
  Settings, 
  LogOut,
  ShieldCheck,
  Bell
} from "lucide-react";
import { cn } from "@/lib/utils";

const menuItems = [
  { icon: LayoutDashboard, label: "Command Center", href: "/dashboard" },
  { icon: FileText, label: "Incident Reports", href: "/dashboard/reports" },
  { icon: MapIcon, label: "Mission Map", href: "/dashboard/map" },
  { icon: Users, label: "Volunteer Force", href: "/dashboard/volunteers" },
  { icon: Package, label: "Resource Hub", href: "/dashboard/resources" },
  { icon: BarChart3, label: "Impact Analytics", href: "/dashboard/analytics" },
];

export const DashboardSidebar = () => {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-background/40 backdrop-blur-xl border-r border-white/[0.08] flex flex-col z-50">
      <div className="p-6">
        <Link href="/" className="flex items-center gap-2 mb-8 group">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center group-hover:rotate-12 transition-transform">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <span className="text-sm font-black tracking-tighter uppercase">
            Resolvit <span className="text-primary">Care</span>
          </span>
        </Link>
        
        <nav className="space-y-1">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group",
                pathname === item.href
                  ? "bg-primary text-white shadow-[0_0_20px_rgba(139,92,246,0.3)]"
                  : "text-muted-foreground hover:bg-white/[0.05] hover:text-white"
              )}
            >
              <item.icon className={cn("w-4 h-4", pathname === item.href ? "text-white" : "group-hover:text-primary")} />
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="mt-auto p-6 space-y-1 border-t border-white/[0.06]">
        <Link
          href="/dashboard/settings"
          className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-muted-foreground hover:bg-white/[0.05] hover:text-white transition-all group"
        >
          <Settings className="w-4 h-4 group-hover:text-primary" />
          Settings
        </Link>
        <button
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:bg-red-400/10 transition-all group"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};
