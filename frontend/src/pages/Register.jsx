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
  CheckCircle,
} from "lucide-react";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await register(email.trim(), password);
      setDone(true);
      setTimeout(() => navigate("/dashboard"), 1200);
    } catch (err) {
      setError(err?.message || "Registration failed. Please try another email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans">
      {/* LEFT COLUMN: Xedlab-Inspired Futuristic Medical Hero Banner */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-slate-950 via-[#031533] to-[#04285e] p-12 flex-col justify-between border-r border-cyan-900/30">
        {/* Ambient Glows */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(6,182,212,0.15),transparent_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_80%,rgba(14,165,233,0.12),transparent_50%)]" />

        {/* Background Tech Image */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30 mix-blend-screen pointer-events-none"
          style={{ backgroundImage: "url('/medical-hero.jpg')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent" />

        {/* Header */}
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

        {/* Center Graphic */}
        <div className="relative z-10 my-auto py-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-semibold mb-6 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            Create Your Research & Clinical Workspace
          </div>

          <h2 className="text-3xl xl:text-4xl font-extrabold text-white tracking-tight leading-tight mb-4">
            AI-Assisted Diagnostic <br />
            <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-400 bg-clip-text text-transparent">
              Laboratory Intelligence
            </span>
          </h2>

          <p className="text-sm text-slate-300/90 leading-relaxed max-w-lg mb-8 font-light">
            Upload PDFs, scans, and laboratory printouts. Instantly cross-reference numerical findings with verified ranges, medical entities, and grounded RAG citations.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md">
              <HeartPulse className="w-5 h-5 text-rose-400 mb-2" />
              <div className="text-xs font-bold text-slate-200">Cardiology</div>
              <div className="text-[10px] text-slate-400">Lipid Panels</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md">
              <TestTube2 className="w-5 h-5 text-cyan-400 mb-2" />
              <div className="text-xs font-bold text-slate-200">Hematology</div>
              <div className="text-[10px] text-slate-400">CBC & WBC</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md">
              <Dna className="w-5 h-5 text-teal-400 mb-2" />
              <div className="text-xs font-bold text-slate-200">Biochemistry</div>
              <div className="text-[10px] text-slate-400">LFT & KFT</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md">
              <Pill className="w-5 h-5 text-amber-400 mb-2" />
              <div className="text-xs font-bold text-slate-200">Pharmacology</div>
              <div className="text-[10px] text-slate-400">Entities</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="relative z-10 pt-6 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Encrypted HIPAA/GDPR Architecture</span>
          </div>
          <span className="text-slate-500">100% Deterministic Bounds</span>
        </div>
      </div>

      {/* RIGHT COLUMN: Modern Glassmorphism Registration Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(6,182,212,0.06),transparent_70%)]" />

        <div className="w-full max-w-md relative z-10">
          <div className="bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 sm:p-10 shadow-2xl shadow-cyan-950/40">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 text-white flex items-center justify-center mx-auto mb-3 shadow-lg shadow-cyan-500/25">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Create Account
              </h1>
              <p className="text-xs text-slate-400 mt-1.5">
                Start analyzing medical reports with grounded AI support
              </p>
            </div>

            {done ? (
              <div className="flex flex-col items-center gap-3 py-8 text-center">
                <div className="w-16 h-16 rounded-full bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/20 animate-bounce">
                  <CheckCircle className="w-8 h-8" />
                </div>
                <h3 className="text-base font-bold text-white mt-2">Account Created!</h3>
                <p className="text-xs text-slate-400">Redirecting to your clinical dashboard...</p>
              </div>
            ) : (
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
                    Password <span className="font-normal text-slate-500">(minimum 8 characters)</span>
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

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      required
                      placeholder="••••••••"
                      value={confirm}
                      onChange={(e) => setConfirm(e.target.value)}
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
                  {loading ? "Creating Account..." : "Create Account & Get Started"}
                  {!loading && <ArrowRight className="w-4 h-4 text-slate-950" />}
                </button>
              </form>
            )}

            {!done && (
              <div className="mt-6 pt-6 border-t border-slate-800 text-center">
                <p className="text-xs text-slate-400">
                  Already have an account?{" "}
                  <Link
                    to="/login"
                    className="font-bold text-cyan-400 hover:text-cyan-300 hover:underline"
                  >
                    Sign in here
                  </Link>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
