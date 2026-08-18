import axios from "axios";

// Read API URL from Vite environment variable with safe fallback
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("mra_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if session expired
      localStorage.removeItem("mra_token");
      if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export const auth = {
  register: (email, password) => api.post("/auth/register", { email, password }),
  login: (email, password) => api.post("/auth/login", { email, password }),
  me: () => api.get("/auth/me"),
};

export const reports = {
  upload: (file, onProgress) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/reports/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: onProgress,
    });
  },
  status: (reportId) => api.get(`/reports/${reportId}/status`),
  get: (reportId) => api.get(`/reports/${reportId}`),
  findings: (reportId) => api.get(`/reports/${reportId}/findings`),
  summary: (reportId) => api.get(`/reports/${reportId}/summary`),
  pages: (reportId) => api.get(`/reports/${reportId}/pages`),
  ask: (reportId, question) => api.post(`/reports/${reportId}/ask`, { question }),
  history: () => api.get("/reports/history"),
  list: () => api.get("/reports"),
  comparison: (reportId) => api.get(`/reports/${reportId}/comparison`),
  remove: (reportId) => api.delete(`/reports/${reportId}`),
};

export const system = {
  health: () => api.get("/health"),
  ready: () => api.get("/ready"),
};

export default api;
