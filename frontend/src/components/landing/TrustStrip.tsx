"use client";

import React from "react";
import { motion } from "framer-motion";
import { Globe, Shield, Heart, Landmark, Anchor, Activity } from "lucide-react";

export const TrustStrip = () => {
  const partners = [
    { name: "UNICEF", icon: Heart },
    { name: "Red Cross", icon: Activity },
    { name: "ReliefWeb", icon: Globe },
    { name: "WFP", icon: Anchor },
    { name: "GovCare", icon: Landmark },
    { name: "SafeImpact", icon: Shield },
  ];

  return (
    <div className="py-12 border-y border-white/[0.06] bg-white/[0.01]">
      <div className="container mx-auto px-4">
        <p className="text-center text-[10px] font-bold tracking-[0.3em] text-muted-foreground uppercase mb-8">
          Trusted by humanitarian leaders worldwide
        </p>
        <div className="flex flex-wrap justify-center gap-x-12 gap-y-8 opacity-40 grayscale hover:grayscale-0 transition-all duration-500">
          {partners.map((partner, i) => (
            <div key={i} className="flex items-center gap-2 group cursor-pointer hover:opacity-100 transition-opacity">
              <partner.icon className="w-5 h-5 group-hover:text-primary transition-colors" />
              <span className="text-sm font-black tracking-tighter uppercase whitespace-nowrap">
                {partner.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
