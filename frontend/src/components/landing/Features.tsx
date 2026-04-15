"use client";

import React from "react";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/shared/GlassCard";
import { Section, SectionHeader } from "@/components/shared/Section";
import { 
  FileText, 
  BrainCircuit, 
  AlertCircle, 
  MapPin, 
  Users, 
  Package, 
  ListChecks, 
  LineChart 
} from "lucide-react";

export const Features = () => {
  const features = [
    {
      title: "Intelligent Need Reporting",
      description: "Aggregate community reports from multiple streams with AI-driven sanity checks.",
      icon: FileText,
      color: "text-blue-400",
    },
    {
      title: "NLP Classification",
      description: "Auto-categorize reports into 10+ social sectors for faster routing.",
      icon: BrainCircuit,
      color: "text-purple-400",
    },
    {
      title: "Multi-factor Urgency",
      description: "Prioritize cases using 8-factor AI scoring across severity and impact.",
      icon: AlertCircle,
      color: "text-red-400",
    },
    {
      title: "Geospatial Intelligence",
      description: "Identify crisis hotspots and visualize demand through predictive heatmaps.",
      icon: MapPin,
      color: "text-amber-400",
    },
    {
      title: "Smart Volunteer Matching",
      description: "Algorithmically assign top-tier volunteers based on skills and proximity.",
      icon: Users,
      color: "text-emerald-400",
    },
    {
      title: "Resource Orchestration",
      description: "Optimize inventory dispatch and resource movement between warehouses.",
      icon: Package,
      color: "text-cyan-400",
    },
    {
      title: "Task Lifecycle Tracking",
      description: "Monitor real-time status from report ingestion to final verification.",
      icon: ListChecks,
      color: "text-indigo-400",
    },
    {
      title: "Impact Analytics",
      description: "Visualize ROI on social impact and measure operational efficiency.",
      icon: LineChart,
      color: "text-pink-400",
    },
  ];

  return (
    <Section id="features">
      <SectionHeader
        overline="Elite Capabilities"
        title={
          <>
            Engineering <span className="text-gradient">Social Impact</span> at Scale
          </>
        }
        description="A comprehensive suite of AI operations tools designed for modern NGOs and disaster response teams."
      />
      
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
          >
            <GlassCard className="h-full group hover:border-primary/30" glow>
              <div className={`w-12 h-12 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center mb-6 transition-all duration-300 group-hover:scale-110 group-hover:shadow-[0_0_20px_rgba(255,255,255,0.05)]`}>
                <feature.icon className={`w-6 h-6 ${feature.color}`} />
              </div>
              <h3 className="text-xl font-bold mb-3 tracking-tight">{feature.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </GlassCard>
          </motion.div>
        ))}
      </div>
    </Section>
  );
};
