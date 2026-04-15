import { cn } from "@/lib/utils";
import React from "react";

interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  container?: boolean;
}

export const Section = ({ children, className, container = true, ...props }: SectionProps) => {
  return (
    <section className={cn("py-16 md:py-24 relative overflow-hidden", className)} {...props}>
      {container ? (
        <div className="container mx-auto px-4 relative z-10">{children}</div>
      ) : (
        <div className="relative z-10">{children}</div>
      )}
    </section>
  );
};

export const SectionHeader = ({
  overline,
  title,
  description,
  align = "center",
  className,
}: {
  overline?: string;
  title: React.ReactNode;
  description?: string;
  align?: "left" | "center" | "right";
  className?: string;
}) => {
  const alignment = {
    left: "text-left items-start",
    center: "text-center items-center justify-center",
    right: "text-right items-end",
  };

  return (
    <div className={cn("flex flex-col mb-12", alignment[align], className)}>
      {overline && (
        <span className="text-primary font-bold text-xs tracking-widest uppercase mb-3">
          {overline}
        </span>
      )}
      <h2 className="text-3xl md:text-4xl lg:text-5xl font-black tracking-tight mb-4 leading-tight">
        {title}
      </h2>
      {description && (
        <p className="text-muted-foreground text-base md:text-lg max-w-2xl leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
};
