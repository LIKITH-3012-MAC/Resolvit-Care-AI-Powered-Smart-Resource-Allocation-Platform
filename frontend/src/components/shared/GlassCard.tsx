import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  glow?: boolean;
}

export const GlassCard = ({ children, className, glow = false, ...props }: GlassCardProps) => {
  return (
    <div
      className={cn(
        "glass-card bg-white/[0.03] backdrop-blur-lg border border-white/[0.06] rounded-2xl p-6 transition-all duration-300",
        glow && "hover:shadow-[0_0_40px_rgba(139,92,246,0.15)] hover:border-primary/40",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
