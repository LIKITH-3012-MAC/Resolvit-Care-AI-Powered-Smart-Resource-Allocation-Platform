"use client";

import React, { useState } from "react";
import { ShieldCheck, MapPin, AlertCircle, CheckCircle2, Loader2, Navigation, Send } from "lucide-react";
import dynamic from "next/dynamic";
import { reportsApi } from "@/lib/api-client";
import { useRouter } from "next/navigation";

// Dynamically import EliteMap to avoid SSR issues
const EliteMap = dynamic(() => import("@/components/dashboard/EliteMap"), {
  ssr: false,
  loading: () => <div className="w-full h-[400px] bg-white/[0.03] animate-pulse rounded-2xl border border-white/[0.06]" />,
});

export default function ReportPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState({
    title: "",
    raw_text: "",
    category: "General",
    affected_count: 1,
    location_name: "",
    latitude: 17.3850,
    longitude: 78.4867,
  });

  const handleLocationSelect = (lat: number, lng: number) => {
    setFormData(prev => ({ ...prev, latitude: lat, longitude: lng }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Note: Real production logic would use the reporter_id from auth token
      await reportsApi.create({
        ...formData,
        category_id: 1, // Default for now
        status: "reported"
      });
      setSuccess(true);
      setTimeout(() => router.push("/dashboard"), 3000);
    } catch (error) {
      console.error("Failed to submit report:", error);
      alert("Submission failed. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="text-center space-y-6 max-w-md w-full glass-card p-12 rounded-3xl border border-primary/20 bg-primary/5">
          <div className="w-20 h-20 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-8 animate-bounce">
            <CheckCircle2 className="w-12 h-12 text-primary" />
          </div>
          <h1 className="text-3xl font-black tracking-tighter uppercase">Intelligence Logged</h1>
          <p className="text-muted-foreground leading-relaxed">
            Your report has been successfully ingested. The AI prioritization engine is now calculating urgency scores and routing to the nearest relief teams.
          </p>
          <div className="pt-4 text-xs font-bold tracking-widest text-primary uppercase animate-pulse">
            Redirecting to Mission Control...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground pt-32 pb-20 overflow-x-hidden">
      {/* Background Orbs */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/10 rounded-full blur-[120px]" />
      </div>

      <div className="container mx-auto px-4 max-w-4xl">
        <div className="flex items-center gap-4 mb-12">
          <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30">
            <Navigation className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tighter uppercase leading-none">Citizen Intelligence</h1>
            <p className="text-muted-foreground text-sm uppercase tracking-[0.2em] font-medium mt-1">Field Report Ingestion v2.0</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Left: Form */}
          <div className="lg:col-span-12 space-y-8">
            <div className="p-8 rounded-3xl glass-card border border-white/[0.06] bg-white/[0.02]">
              <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/[0.06]">
                <div className="flex gap-4">
                  {[1, 2, 3].map((s) => (
                    <div 
                      key={s} 
                      className={`h-1.5 w-12 rounded-full transition-all duration-500 ${step >= s ? 'bg-primary' : 'bg-white/[0.06]'}`} 
                    />
                  ))}
                </div>
                <span className="text-xs font-bold tracking-widest uppercase text-muted-foreground">Step {step} of 3</span>
              </div>

              {step === 1 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="space-y-3">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">Report Title</label>
                    <input 
                      type="text" 
                      placeholder="e.g., Road Blockage in District 5"
                      className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-all"
                      value={formData.title}
                      onChange={(e) => setFormData({...formData, title: e.target.value})}
                    />
                  </div>
                  <div className="space-y-3">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">Description</label>
                    <textarea 
                      rows={6}
                      placeholder="Describe the situation in detail. Our AI will automatically extract key entities and urgency indicators."
                      className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-all resize-none"
                      value={formData.raw_text}
                      onChange={(e) => setFormData({...formData, raw_text: e.target.value})}
                    />
                  </div>
                  <button 
                    onClick={() => setStep(2)}
                    disabled={!formData.raw_text}
                    className="w-full py-4 bg-primary text-white font-black tracking-widest uppercase rounded-xl hover:shadow-[0_0_30px_rgba(255,0,102,0.4)] transition-all disabled:opacity-50"
                  >
                    Analyze Situation
                  </button>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">Primary Need Category</label>
                      <select 
                        className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-all appearance-none"
                        value={formData.category}
                        onChange={(e) => setFormData({...formData, category: e.target.value})}
                      >
                        <option>Medical Emergency</option>
                        <option>Food & Water</option>
                        <option>Infrastructure Repair</option>
                        <option>Evacuation Support</option>
                        <option>General Support</option>
                      </select>
                    </div>
                    <div className="space-y-3">
                      <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">Affected Individuals (Est.)</label>
                      <input 
                        type="number" 
                        min="1"
                        className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-all"
                        value={formData.affected_count}
                        onChange={(e) => setFormData({...formData, affected_count: parseInt(e.target.value)})}
                      />
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <button 
                      onClick={() => setStep(1)}
                      className="flex-1 py-4 border border-white/[0.1] text-white font-black tracking-widest uppercase rounded-xl hover:bg-white/[0.05] transition-all"
                    >
                      Back
                    </button>
                    <button 
                      onClick={() => setStep(3)}
                      className="flex-[2] py-4 bg-primary text-white font-black tracking-widest uppercase rounded-xl hover:shadow-[0_0_30px_rgba(255,0,102,0.4)] transition-all"
                    >
                      Geotag Report
                    </button>
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
                  <div className="space-y-3">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground ml-1">Select Precise Location</label>
                    <div className="h-[400px] w-full rounded-2xl border border-white/[0.1] overflow-hidden">
                      <EliteMap onLocationSelect={handleLocationSelect} />
                    </div>
                    <div className="flex items-center gap-2 mt-2 ml-1">
                      <MapPin className="w-3 h-3 text-primary" />
                      <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground">
                        Coords: {formData.latitude.toFixed(6)}, {formData.longitude.toFixed(6)}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <button 
                      onClick={() => setStep(2)}
                      className="flex-1 py-4 border border-white/[0.1] text-white font-black tracking-widest uppercase rounded-xl hover:bg-white/[0.05] transition-all"
                    >
                      Back
                    </button>
                    <button 
                      onClick={handleSubmit}
                      disabled={loading}
                      className="flex-[2] py-4 bg-primary text-white font-black tracking-widest uppercase rounded-xl hover:shadow-[0_0_30px_rgba(255,0,102,0.4)] transition-all flex items-center justify-center gap-2"
                    >
                      {loading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <>
                          <Send className="w-5 h-5" />
                          Ingest Core Data
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex items-start gap-4 p-6 rounded-2xl bg-primary/5 border border-primary/10">
              <AlertCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed text-muted-foreground uppercase tracking-wider font-medium">
                <span className="text-white font-bold">Important:</span> This platform is monitored by humanitarian intelligence officers. False reports may delay critical response for others. Ensure all data is accurate to the best of your knowledge.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
