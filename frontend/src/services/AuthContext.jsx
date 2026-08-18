/**
 * AuthContext — localStorage-based auth (no backend required).
 * Users are stored in localStorage so registration & login work instantly.
 * When the backend is available, API calls are attempted first.
 */
import React, { createContext, useContext, useState, useCallback } from "react";

const AuthContext = createContext(null);

const USERS_KEY = "mra_users";
const TOKEN_KEY = "mra_token";
const EMAIL_KEY = "mra_email";

// ─── helpers ────────────────────────────────────────────────────────────────

function getUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function makeToken(email) {
  // Simple base64 pseudo-token — good enough for local demo
  const payload = btoa(JSON.stringify({ email, exp: Date.now() + 86400000 }));
  return `local.${payload}`;
}

// ─── provider ───────────────────────────────────────────────────────────────

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [email, setEmail] = useState(() => localStorage.getItem(EMAIL_KEY));

  const register = useCallback(async (emailInput, password) => {
    const key = emailInput.trim().toLowerCase();

    // Try real backend first (silent fail)
    try {
      const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
      const resp = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: key, password }),
      });
      if (resp.ok) {
        // Backend registration succeeded — now login
        const loginResp = await fetch(`${API}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: key, password }),
        });
        if (loginResp.ok) {
          const data = await loginResp.json();
          localStorage.setItem(TOKEN_KEY, data.access_token);
          localStorage.setItem(EMAIL_KEY, key);
          setToken(data.access_token);
          setEmail(key);
          return;
        }
      }
      // If backend returns 400 "email already exists" — show that error
      if (resp.status === 400) {
        const err = await resp.json();
        throw new Error(err.detail || "Email already registered.");
      }
    } catch (e) {
      // If it's our explicit 400 error, re-throw it
      if (e.message && e.message.includes("already")) throw e;
      // Otherwise backend is down — fall through to localStorage
    }

    // ── localStorage fallback ──────────────────────────────────────────────
    const users = getUsers();
    if (users[key]) {
      throw new Error("An account with this email already exists. Please sign in.");
    }
    users[key] = { password }; // store password for local login (demo only)
    saveUsers(users);

    const tok = makeToken(key);
    localStorage.setItem(TOKEN_KEY, tok);
    localStorage.setItem(EMAIL_KEY, key);
    setToken(tok);
    setEmail(key);
  }, []);

  const login = useCallback(async (emailInput, password) => {
    const key = emailInput.trim().toLowerCase();

    // Try real backend first
    try {
      const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
      const resp = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: key, password }),
      });
      if (resp.ok) {
        const data = await resp.json();
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(EMAIL_KEY, key);
        setToken(data.access_token);
        setEmail(key);
        return;
      }
      if (resp.status === 401) {
        throw new Error("Invalid email or password.");
      }
    } catch (e) {
      if (e.message === "Invalid email or password.") throw e;
      // Backend unavailable — fall through to localStorage
    }

    // ── localStorage fallback ──────────────────────────────────────────────
    const users = getUsers();
    if (!users[key] || users[key].password !== password) {
      throw new Error("Invalid email or password.");
    }

    const tok = makeToken(key);
    localStorage.setItem(TOKEN_KEY, tok);
    localStorage.setItem(EMAIL_KEY, key);
    setToken(tok);
    setEmail(key);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EMAIL_KEY);
    setToken(null);
    setEmail(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ token, email, login, register, logout, isAuthenticated: !!token }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
