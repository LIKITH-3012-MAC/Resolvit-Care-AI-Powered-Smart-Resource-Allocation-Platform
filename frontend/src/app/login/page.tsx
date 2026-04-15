"use client";

import React, { useState } from "react";
import { ShieldCheck, Lock, Mail, Loader2, ArrowRight } from "lucide-react";
import { authApi } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const form = new FormData();
      form.append("username", formData.email);
      form.append("password", formData.password);

      const response = await authApi.login(form);
      localStorage.setItem("token", response.data.access_token);
      
      // Redirect to dashboard
      router.push("/dashboard");
    } catch (err: any) {
      console.error("Login failed:", err);
      setError(err.response?.data?.detail || "Invalid credentials or backend offline.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6 text-foreground relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-[-20%] right-[-10%] w-[60%] h-[60%] bg-primary/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px]" />

      <div className="max-w-md w-full space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
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
          <h2 className="text-3xl font-black tracking-tighter uppercase">Mission Entry</h2>
          <p className="text-muted-foreground text-sm uppercase tracking-widest mt-2">Secure node authentication</p>
        </div>

        <form onSubmit={handleLogin} className="glass-card p-10 rounded-3xl border border-white/[0.06] bg-white/[0.02] space-y-6">
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs font-bold uppercase tracking-wider flex items-center gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground ml-1">Email Terminal</label>
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

          <button 
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-primary text-white font-black tracking-widest uppercase rounded-xl shadow-[0_10px_30px_rgba(255,0,102,0.3)] hover:shadow-[0_15px_40px_rgba(255,0,102,0.5)] active:scale-[0.98] transition-all disabled:opacity-50 flex items-center justify-center gap-2 group"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                Initiate Link
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>

          <p className="text-center text-xs text-muted-foreground uppercase tracking-widest font-bold">
            New operative? <Link href="/signup" className="text-primary hover:underline underline-offset-4">Register here</Link>
          </p>
        </form>

        <div className="text-center text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-medium opacity-50">
          Unauthorized access is logged and traced. Resolvit Care v2.0.4
        </div>
      </div>
    </div>
  );
}
