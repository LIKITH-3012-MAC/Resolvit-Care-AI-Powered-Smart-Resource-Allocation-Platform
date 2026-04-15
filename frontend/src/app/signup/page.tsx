"use client";

import React, { useState } from "react";
import { ShieldCheck, User, Mail, Lock, UserCircle, Briefcase, Heart, ArrowRight, Loader2, CheckCircle2 } from "lucide-react";
import { authApi } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function SignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
    role: "citizen",
  });

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await authApi.signup({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: formData.role
      });
      setSuccess(true);
      setTimeout(() => router.push("/login"), 2000);
    } catch (err: any) {
      console.error("Signup failed:", err);
      setError(err.response?.data?.detail || "Registration failed. Trace connection.");
    } finally {
      setLoading(false);
    }
  };

  const roles = [
    { id: "citizen", label: "Citizen", icon: UserCircle, desc: "Report local issues & track relief" },
    { id: "ngo_admin", label: "NGO Admin", icon: Briefcase, desc: "Orchestrate resource & volunteer ops" },
    { id: "volunteer", label: "Volunteer", icon: Heart, desc: "Support field missions & save lives" },
  ];

  if (success) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="text-center space-y-6 max-w-md w-full glass-card p-12 rounded-3xl border border-primary/20 bg-primary/5">
          <div className="w-20 h-20 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-8 animate-bounce">
            <CheckCircle2 className="w-12 h-12 text-primary" />
          </div>
          <h1 className="text-3xl font-black tracking-tighter uppercase">Identity Verified</h1>
          <p className="text-muted-foreground leading-relaxed">
            Operative account created successfully. You are now being rerouted to the authentication terminal.
          </p>
          <div className="pt-4 text-xs font-bold tracking-widest text-primary uppercase animate-pulse">
            Establishing secure connection...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6 text-foreground relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-primary/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px]" />

      <div className="max-w-2xl w-full space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
        <div className="text-center">
          <Link href="/" className="inline-flex items-center gap-2 mb-8 group">
            <div className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center group-hover:rotate-12 transition-transform shadow-[0_0_30px_rgba(255,0,102,0.3)]">
              <ShieldCheck className="w-7 h-7 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-black tracking-tighter uppercase leading-none">Resolvit</h1>
              <span className="text-[10px] font-bold tracking-[0.3em] text-primary uppercase">Intelligence</span>
            </div>
          </Link>
          <h2 className="text-3xl font-black tracking-tighter uppercase">New Operative</h2>
          <p className="text-muted-foreground text-sm uppercase tracking-widest mt-2">Create your mission identity</p>
        </div>

        <form onSubmit={handleSignup} className="glass-card p-10 rounded-3xl border border-white/[0.06] bg-white/[0.02] space-y-8">
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs font-bold uppercase tracking-wider flex items-center gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground ml-1">Full Operative Name</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input 
                    type="text" 
                    required
                    placeholder="Likith Naidu"
                    className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl pl-12 pr-4 py-4 text-sm focus:outline-none focus:border-primary/50 focus:bg-white/[0.05] transition-all"
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground ml-1">Secure Email</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input 
                    type="email" 
                    required
                    placeholder="name@organization.gov"
                    className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl pl-12 pr-4 py-4 text-sm focus:outline-none focus:border-primary/50 focus:bg-white/[0.05] transition-all"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground ml-1">Access Cipher</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input 
                    type="password" 
                    required
                    placeholder="••••••••"
                    className="w-full bg-white/[0.03] border border-white/[0.06] rounded-xl pl-12 pr-4 py-4 text-sm focus:outline-none focus:border-primary/50 focus:bg-white/[0.05] transition-all"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground ml-1">Select Active Role</label>
              <div className="space-y-3">
                {roles.map((role) => {
                  const Icon = role.icon;
                  return (
                    <button
                      key={role.id}
                      type="button"
                      onClick={() => setFormData({...formData, role: role.id})}
                      className={`w-full p-4 rounded-2xl border text-left transition-all ${
                        formData.role === role.id 
                        ? 'bg-primary/10 border-primary shadow-[0_0_20px_rgba(255,0,102,0.1)]' 
                        : 'bg-white/[0.02] border-white/[0.06] hover:bg-white/[0.04]'
                      }`}
                    >
                      <div className="flex gap-4">
                        <div className={`p-2 rounded-lg ${formData.role === role.id ? 'bg-primary text-white' : 'bg-white/5 text-muted-foreground'}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div>
                          <p className={`text-xs font-bold uppercase tracking-wider ${formData.role === role.id ? 'text-primary' : ''}`}>{role.label}</p>
                          <p className="text-[10px] text-muted-foreground mt-1 leading-tight">{role.desc}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <button 
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-primary text-white font-black tracking-widest uppercase rounded-xl shadow-[0_10px_30px_rgba(255,0,102,0.3)] hover:shadow-[0_15px_40px_rgba(255,0,102,0.5)] active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center gap-2 group"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                Register Operative
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>

          <p className="text-center text-xs text-muted-foreground uppercase tracking-widest font-bold">
            Already registered? <Link href="/login" className="text-primary hover:underline underline-offset-4">Initiate login</Link>
          </p>
        </form>

        <div className="text-center text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-medium opacity-50">
          Global impact registry. Verified data exclusively.
        </div>
      </div>
    </div>
  );
}
