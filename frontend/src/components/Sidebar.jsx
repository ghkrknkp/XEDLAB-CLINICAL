import React, { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Clock,
  LogOut,
  Activity,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useAuth } from "../services/AuthContext";
import { system } from "../services/api";

export default function Sidebar() {
  const { email, logout } = useAuth();
  const navigate = useNavigate();
  const [healthStatus, setHealthStatus] = useState("online");

  useEffect(() => {
    system
      .health()
      .then(() => setHealthStatus("healthy"))
      .catch(() => setHealthStatus("active (local)"));
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navLinkClass = ({ isActive }) =>
    `flex items-center gap-3 px-3.5 py-3 rounded-2xl text-xs font-bold transition-all ${
      isActive
        ? "bg-gradient-to-r from-teal-500 to-cyan-500 text-slate-950 shadow-md shadow-teal-500/20"
        : "text-slate-400 hover:bg-slate-900 hover:text-teal-300"
    }`;

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-950 flex flex-col justify-between p-4 h-screen sticky top-0 text-slate-100 font-sans">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2 py-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-teal-500 to-cyan-500 p-0.5 shadow-md shadow-teal-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <Activity className="w-5 h-5 text-teal-400" />
            </div>
          </div>
          <div>
            <h1 className="font-extrabold text-sm leading-tight text-white tracking-tight">
              XEDLAB <span className="text-teal-400 font-light">CLINICAL</span>
            </h1>
            <p className="text-[10px] font-medium text-slate-400 tracking-wider">
              Medical Report AI
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1.5">
          <NavLink to="/dashboard" className={navLinkClass} end>
            <LayoutDashboard className="w-4 h-4" />
            <span>Dashboard & Upload</span>
          </NavLink>
          <NavLink to="/history" className={navLinkClass}>
            <Clock className="w-4 h-4" />
            <span>Report History</span>
          </NavLink>
        </nav>

        {/* Safety Badge */}
        <div className="mt-8 mx-1 p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center gap-2 text-teal-400 mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span className="text-[11px] font-bold">Non-Diagnostic Safety</span>
          </div>
          <p className="text-[10px] text-slate-400 leading-relaxed font-light">
            Deterministic range verification & grounded patient synthesis.
          </p>
        </div>
      </div>

      {/* Footer / Account */}
      <div className="pt-4 border-t border-slate-800/80">
        <div className="flex items-center justify-between px-2 mb-2">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
            System Status
          </span>
          <span className="flex items-center gap-1.5 text-[10px] font-medium text-teal-400">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
            {healthStatus}
          </span>
        </div>

        <div className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 font-medium truncate mb-2 font-mono">
          {email || "doctor@hospital.org"}
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold text-rose-400 hover:bg-rose-950/40 border border-transparent hover:border-rose-900/40 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
