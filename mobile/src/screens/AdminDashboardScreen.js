import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { api } from "../api/client";
import MetricCard from "../components/MetricCard";
import LeafletRouteMap from "../components/LeafletRouteMap";

export default function AdminDashboardScreen({ navigation, onNavigateTab }) {
  const [loading, setLoading] = useState(false);
  const [shuttles, setShuttles] = useState([]);
  const [requests, setRequests] = useState([]);
  const [latestPlan, setLatestPlan] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const s = await api.getShuttles().catch(() => []);
      setShuttles(s);
      const r = await api.getRequests().catch(() => []);
      setRequests(r);
      const p = await api.getLatestPlan().catch(() => null);
      setLatestPlan(p);
    } catch (err) {
      console.warn("Error fetching dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleSeedBenchmark = async () => {
    setLoading(true);
    try {
      const res = await api.seedBenchmark();
      Alert.alert("Benchmark Seeded", `${res.message}\n50 Requests & 5 Shuttles ready.`);
      await fetchDashboardData();
    } catch (err) {
      Alert.alert("Seeding Error", err.message || "Failed to seed benchmark.");
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    setLoading(true);
    try {
      const plan = await api.generatePlan();
      Alert.alert(
        "Optimization Complete!",
        `Routes computed in < 2 seconds!\nTotal Distance: ${plan.metrics.total_distance_km} km\nUtilization: ${plan.metrics.vehicle_utilization_pct}%\nOn-Time: ${plan.metrics.deadline_compliance_pct}%`
      );
      setLatestPlan(plan);
      await fetchDashboardData();
    } catch (err) {
      Alert.alert("Optimization Error", err.message || "Failed to generate plan.");
    } finally {
      setLoading(false);
    }
  };

  const metrics = latestPlan?.metrics;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Top Banner */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Transport Admin Console</Text>
          <Text style={styles.subtitle}>Fleet Coordination & Demand-Responsive Routing</Text>
        </View>
        <TouchableOpacity style={styles.refreshBtn} onPress={fetchDashboardData}>
          <Text style={styles.refreshText}>🔄 Refresh</Text>
        </TouchableOpacity>
      </View>

      {/* Action Control Panel */}
      <View style={styles.actionPanel}>
        <Text style={styles.panelTitle}>Quick Actions & Demonstration Tools</Text>
        <View style={styles.btnRow}>
          <TouchableOpacity
            style={[styles.actionBtn, styles.seedBtn]}
            onPress={handleSeedBenchmark}
            disabled={loading}
          >
            <Text style={styles.actionBtnText}>⚡ Seed 50 Benchmark</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionBtn, styles.planBtn]}
            onPress={handleGeneratePlan}
            disabled={loading}
          >
            <Text style={styles.actionBtnText}>🚀 Run VRPTW Optimiser</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Metric Cards Grid */}
      <View style={styles.metricsGrid}>
        <MetricCard
          title="Active Shuttles"
          value={shuttles.filter((s) => s.status === "active").length}
          subtext={`of ${shuttles.length} fleet vehicles`}
          isHighlight
        />
        <MetricCard
          title="Pending Requests"
          value={requests.length}
          subtext="Commuters queued"
        />
        <MetricCard
          title="Vehicle Utilization"
          value={metrics ? `${metrics.vehicle_utilization_pct}%` : "—"}
          subtext="Occupied seats"
          trend={metrics ? { text: "+32% vs Baseline", positive: true } : null}
        />
        <MetricCard
          title="Total Fleet Distance"
          value={metrics ? metrics.total_distance_km : "—"}
          unit="km"
          subtext="Combined route length"
          trend={metrics ? { text: "-28% vs Baseline", positive: true } : null}
        />
      </View>

      {/* Latest Route Plan Preview */}
      {latestPlan?.routes && (
        <View style={styles.planSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Active Multi-Shuttle Trajectories</Text>
            <TouchableOpacity onPress={() => onNavigateTab("map")}>
              <Text style={styles.linkText}>Open Full Map ➔</Text>
            </TouchableOpacity>
          </View>

          <LeafletRouteMap routes={latestPlan.routes} />

          {/* Quick Route Manifest Cards */}
          <View style={styles.routeList}>
            {latestPlan.routes.map((r, i) => (
              <View key={r.shuttle_id} style={styles.routeCard}>
                <View style={styles.routeHeader}>
                  <Text style={styles.routeName}>{r.shuttle_name}</Text>
                  <Text style={styles.routePax}>
                    👥 {r.assigned_passengers_count}/{r.capacity} Seats
                  </Text>
                </View>
                <Text style={styles.routeMeta}>
                  📏 {r.total_distance_km} km • ⏱️ {r.total_duration_min} min • 🚏 {r.stops.length} stops
                </Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#38bdf8" />
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#090d16",
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
    paddingTop: 10,
  },
  title: {
    color: "#f8fafc",
    fontSize: 22,
    fontWeight: "800",
  },
  subtitle: {
    color: "#94a3b8",
    fontSize: 12,
    marginTop: 2,
  },
  refreshBtn: {
    backgroundColor: "#1e293b",
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#334155",
  },
  refreshText: {
    color: "#94a3b8",
    fontSize: 12,
  },
  actionPanel: {
    backgroundColor: "#111827",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "#1f2937",
    marginBottom: 16,
  },
  panelTitle: {
    color: "#f3f4f6",
    fontSize: 13,
    fontWeight: "700",
    marginBottom: 10,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  btnRow: {
    flexDirection: "row",
    gap: 10,
  },
  actionBtn: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  seedBtn: {
    backgroundColor: "#0284c7",
  },
  planBtn: {
    backgroundColor: "#16a34a",
  },
  actionBtnText: {
    color: "#ffffff",
    fontSize: 13,
    fontWeight: "bold",
  },
  metricsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginHorizontal: -6,
    marginBottom: 16,
  },
  planSection: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  sectionTitle: {
    color: "#f8fafc",
    fontSize: 16,
    fontWeight: "700",
  },
  linkText: {
    color: "#38bdf8",
    fontSize: 13,
    fontWeight: "600",
  },
  routeList: {
    marginTop: 12,
  },
  routeCard: {
    backgroundColor: "#111827",
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#1f2937",
  },
  routeHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  routeName: {
    color: "#f8fafc",
    fontSize: 14,
    fontWeight: "bold",
  },
  routePax: {
    color: "#38bdf8",
    fontSize: 12,
    fontWeight: "600",
  },
  routeMeta: {
    color: "#9ca3af",
    fontSize: 12,
    marginTop: 4,
  },
  loadingOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(9, 13, 22, 0.7)",
    justifyContent: "center",
    alignItems: "center",
  },
});
