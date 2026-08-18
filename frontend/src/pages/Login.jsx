import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../services/AuthContext";
import {
  Activity,
  Lock,
  Mail,
  ArrowRight,
  ShieldCheck,
  Dna,
  HeartPulse,
  Pill,
  TestTube2,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate("/dashboard");
    } catch (err) {
      setError(err?.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = () => {
    setEmail("doctor.demo@example.com");
    setPassword("MedicalDemo123!");
  };

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans">
      {/* LEFT COLUMN: Xedlab-Inspired Futuristic Medical Hero Banner */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-slate-950 via-[#031533] to-[#04285e] p-12 flex-col justify-between border-r border-cyan-900/30">
        {/* Background Ambient Glows & Hero Image Overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(6,182,212,0.15),transparent_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_80%,rgba(14,165,233,0.12),transparent_50%)]" />
        
        {/* Background Tech Image with Opacity & Gradient Mask */}
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-30 mix-blend-screen pointer-events-none"
          style={{ backgroundImage: "url('/medical-hero.jpg')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent" />

        {/* Top Header & Branding */}
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-0.5 shadow-lg shadow-cyan-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <Activity className="w-6 h-6 text-cyan-400" />
              </div>
            </div>
            <div>
              <span className="text-lg font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-200 bg-clip-text text-transparent">
                XEDLAB <span className="text-cyan-400 font-light">CLINICAL AI</span>
              </span>
              <p className="text-[11px] font-medium text-cyan-400/80 uppercase tracking-widest">
                Medical Report Intelligence Platform
              </p>
            </div>
          </div>
        </div>

        {/* Center Graphic & Hexagonal Medical Feature Cards */}
        <div className="relative z-10 my-auto py-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-semibold mb-6 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            Next-Gen Medical Laboratory Intelligence
          </div>

          <h2 className="text-3xl xl:text-4xl font-extrabold text-white tracking-tight leading-tight mb-4">
            Deterministic Precision for <br />
            <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-400 bg-clip-text text-transparent">
              Clinical Document Analysis
            </span>
          </h2>

          <p className="text-sm text-slate-300/90 leading-relaxed max-w-lg mb-8 font-light">
            Instantly ingest, extract, and deterministically validate laboratory values against printed reference ranges with zero hallucination.
          </p>

          {/* Hexagonal Medical Module Icons */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md hover:border-cyan-400/50 transition-all group">
              <HeartPulse className="w-5 h-5 text-rose-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-bold text-slate-200">Cardiology</div>
              <div className="text-[10px] text-slate-400">Lipid & Enzymes</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md hover:border-cyan-400/50 transition-all group">
              <TestTube2 className="w-5 h-5 text-cyan-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-bold text-slate-200">Hematology</div>
              <div className="text-[10px] text-slate-400">CBC & Platelets</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md hover:border-cyan-400/50 transition-all group">
              <Dna className="w-5 h-5 text-teal-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-bold text-slate-200">Biochemistry</div>
              <div className="text-[10px] text-slate-400">LFT & KFT Panels</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md hover:border-cyan-400/50 transition-all group">
              <Pill className="w-5 h-5 text-amber-400 mb-2 group-hover:scale-110 transition-transform" />
              <div className="text-xs font-bold text-slate-200">Pharmacology</div>
              <div className="text-[10px] text-slate-400">Entities & Dosage</div>
            </div>
          </div>
        </div>

        {/* Bottom Trust & Compliance Footer */}
        <div className="relative z-10 pt-6 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Strict Non-Diagnostic Safety Guardrails</span>
          </div>
          <span className="text-slate-500">ISO 27001 / HIPAA Compatible</span>
        </div>
      </div>

      {/* RIGHT COLUMN: Modern Glassmorphism Clinical Sign In Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(6,182,212,0.06),transparent_70%)]" />

        <div className="w-full max-w-md relative z-10">
          {/* Card Container */}
          <div className="bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 sm:p-10 shadow-2xl shadow-cyan-950/40">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 text-white flex items-center justify-center mx-auto mb-3 shadow-lg shadow-cyan-500/25">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Sign In to Portal
              </h1>
              <p className="text-xs text-slate-400 mt-1.5">
                Access your medical reports, verified findings & clinical Q&A
              </p>
            </div>

            {/* Form */}
            <form onSubmit={onSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    placeholder="doctor@hospital.org"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 text-xs rounded-xl border border-slate-700 bg-slate-950/70 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 text-xs rounded-xl border border-slate-700 bg-slate-950/70 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500 transition-all"
                  />
                </div>
              </div>

              {error && (
                <div className="p-3.5 bg-rose-950/40 border border-rose-800/80 rounded-xl text-rose-300 text-xs flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-4 bg-gradient-to-r from-cyan-500 hover:from-cyan-400 to-blue-600 hover:to-blue-500 text-slate-950 font-bold text-xs rounded-xl shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-2"
              >
                {loading ? "Authenticating..." : "Sign In to Workspace"}
                {!loading && <ArrowRight className="w-4 h-4 text-slate-950" />}
              </button>
            </form>

            {/* Quick Demo Pre-fill */}
            <div className="mt-6 p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 text-center">
              <p className="text-[11px] text-slate-400 mb-1.5">First time testing the clinical analyzer?</p>
              <button
                type="button"
                onClick={handleFillDemo}
                className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 hover:underline inline-flex items-center gap-1"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> Auto-fill Demo Credentials
              </button>
            </div>

            {/* Register Footer */}
            <div className="mt-6 pt-6 border-t border-slate-800 text-center">
              <p className="text-xs text-slate-400">
                Don't have an account?{" "}
                <Link
                  to="/register"
                  className="font-bold text-cyan-400 hover:text-cyan-300 hover:underline"
                >
                  Create an account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
