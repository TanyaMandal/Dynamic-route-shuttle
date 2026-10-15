import { API_BASE_URL } from "../config";

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "API request failed");
    }
    return data;
  } catch (err) {
    console.warn(`Request failed to ${url}:`, err.message);
    throw err;
  }
}

export const api = {
  // Auth
  login: (email, password) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  // Fleet
  getShuttles: () => request("/api/shuttles"),

  // Requests
  getRequests: (userId) => request(`/api/requests${userId ? `?user_id=${userId}` : ""}`),
  createRequest: (payload) =>
    request("/api/requests", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Routing & Plans
  generatePlan: () =>
    request("/api/plans/generate", {
      method: "POST",
    }),
  getLatestPlan: () => request("/api/plans/latest"),
  getPlanComparison: (planId) => request(`/api/plans/${planId}/compare`),

  // Disruptions
  getDisruptionPresets: () => request("/api/disruptions/presets"),
  getRoadSegments: () => request("/api/disruptions/road-segments"),
  simulateDisruption: (payload) =>
    request("/api/disruptions/simulate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Benchmark Demo Seeder
  seedBenchmark: () =>
    request("/api/demo/seed-50", {
      method: "POST",
    }),
  resetSystem: () =>
    request("/api/demo/reset", {
      method: "POST",
    }),
};
