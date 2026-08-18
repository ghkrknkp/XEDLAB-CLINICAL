import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { auth as authApi } from "./api";

const AuthContext = createContext(null);

const TOKEN_KEY = "mra_token";
const EMAIL_KEY = "mra_email";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [email, setEmail] = useState(() => localStorage.getItem(EMAIL_KEY));
  const [loading, setLoading] = useState(true);

  // Sync token across state & localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedEmail = localStorage.getItem(EMAIL_KEY);
    if (storedToken) setToken(storedToken);
    if (storedEmail) setEmail(storedEmail);
    setLoading(false);
  }, []);

  const register = useCallback(async (emailInput, password) => {
    const key = emailInput.trim().toLowerCase();

    try {
      // 1. Call real backend register endpoint
      await authApi.register(key, password);

      // 2. Automatically log in to get JWT token
      const loginRes = await authApi.login(key, password);
      const accessToken = loginRes.data?.access_token;

      if (!accessToken) {
        throw new Error("Authentication failed: No access token returned.");
      }

      localStorage.setItem(TOKEN_KEY, accessToken);
      localStorage.setItem(EMAIL_KEY, key);
      setToken(accessToken);
      setEmail(key);
    } catch (err) {
      console.error("Registration error:", err);
      const errorMsg =
        err.response?.data?.detail ||
        err.message ||
        "Registration failed. Please check your connection and try again.";
      throw new Error(errorMsg);
    }
  }, []);

  const login = useCallback(async (emailInput, password) => {
    const key = emailInput.trim().toLowerCase();

    try {
      const loginRes = await authApi.login(key, password);
      const accessToken = loginRes.data?.access_token;

      if (!accessToken) {
        throw new Error("Authentication failed: No access token returned.");
      }

      localStorage.setItem(TOKEN_KEY, accessToken);
      localStorage.setItem(EMAIL_KEY, key);
      setToken(accessToken);
      setEmail(key);
    } catch (err) {
      console.error("Login error:", err);
      const errorMsg =
        err.response?.data?.detail ||
        err.message ||
        "Invalid email or password. Please try again.";
      throw new Error(errorMsg);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EMAIL_KEY);
    setToken(null);
    setEmail(null);
  }, []);

  if (loading) {
    return null;
  }

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
