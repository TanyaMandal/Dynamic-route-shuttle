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
import LeafletRouteMap from "../components/LeafletRouteMap";

export default function AdminDisruptionsScreen() {
  const [loading, setLoading] = useState(false);
  const [presets, setPresets] = useState([]);
  const [roadSegments, setRoadSegments] = useState([]);
  const [shuttles, setShuttles] = useState([]);
  const [latestPlan, setLatestPlan] = useState(null);
  const [recoveryResult, setRecoveryResult] = useState(null);

  useEffect(() => {
    api.getDisruptionPresets().then(setPresets).catch(console.warn);
    api.getRoadSegments().then(setRoadSegments).catch(console.warn);
    api.getShuttles().then(setShuttles).catch(console.warn);
    api.getLatestPlan().then(setLatestPlan).catch(console.warn);
  }, []);

  const handleSimulate = async (type, entityId, desc) => {
    if (!latestPlan) {
      Alert.alert("Plan Required", "Please generate a route plan on the Dashboard first!");
      return;
    }

    setLoading(true);
    setRecoveryResult(null);
    try {
      const res = await api.simulateDisruption({
        disruption_type: type,
        plan_id: latestPlan.id,
        affected_entity_id: entityId,
        description: desc,
      });
      setRecoveryResult(res);
      Alert.alert(
        "Disruption Handled",
        `Rerouting calculated!\nExtra Delay: +${res.extra_delay_min} mins\nExtra Distance: +${res.extra_distance_km} km`
      );
    } catch (err) {
      Alert.alert("Simulation Error", err.message || "Failed to simulate disruption.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Disruption Simulator & Auto-Recovery</Text>
      <Text style={styles.subtitle}>
        Simulate unexpected road closures or vehicle breakdowns and evaluate real-time dynamic rerouting.
      </Text>

      {/* Preset Scenarios */}
      <Text style={styles.sectionHeader}>⚡ 1-Click Evaluation Presets</Text>
      <View style={styles.presetList}>
        {presets.map((p) => (
          <TouchableOpacity
            key={p.id}
            style={styles.presetCard}
            onPress={() => handleSimulate(p.type, p.affected_entity, p.title)}
            disabled={loading}
          >
            <View style={styles.presetTop}>
              <Text style={styles.presetBadge}>
                {p.type === "road_closure" ? "🚧 ROAD CLOSURE" : "⚠️ SHUTTLE BREAKDOWN"}
              </Text>
              <Text style={styles.simText}>Tap to Simulate ➔</Text>
            </View>
            <Text style={styles.presetTitle}>{p.title}</Text>
            <Text style={styles.presetDesc}>{p.description}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Recovery Result Feedback Banner */}
      {recoveryResult && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>Dynamic Recovery Plan Generated</Text>
          <Text style={styles.resultMsg}>{recoveryResult.message}</Text>

          <View style={styles.metricRow}>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>EXTRA DISTANCE</Text>
              <Text style={styles.metricVal}>+{recoveryResult.extra_distance_km} km</Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>ADDED DELAY</Text>
              <Text style={styles.metricVal}>+{recoveryResult.extra_delay_min} min</Text>
            </View>
            <View style={styles.metricBox}>
              <Text style={styles.metricLabel}>REASSIGNED</Text>
              <Text style={styles.metricVal}>{recoveryResult.passengers_reassigned} riders</Text>
            </View>
          </View>

          {/* Revised Map Display */}
          <View style={styles.mapWrap}>
            <Text style={styles.mapLabel}>Revised Dynamic Routing Trajectories:</Text>
            <LeafletRouteMap routes={recoveryResult.revised_routes} />
          </View>
        </View>
      )}

      {loading && (
        <View style={styles.loadingWrap}>
          <ActivityIndicator size="large" color="#38bdf8" />
          <Text style={styles.loadingText}>Computing optimal detours on road graph...</Text>
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
  title: {
    color: "#f8fafc",
    fontSize: 22,
    fontWeight: "800",
  },
  subtitle: {
    color: "#94a3b8",
    fontSize: 13,
    marginTop: 4,
    marginBottom: 20,
    lineHeight: 18,
  },
  sectionHeader: {
    color: "#e2e8f0",
    fontSize: 14,
    fontWeight: "700",
    textTransform: "uppercase",
    marginBottom: 10,
    letterSpacing: 0.5,
  },
  presetList: {
    marginBottom: 20,
  },
  presetCard: {
    backgroundColor: "#111827",
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#1f2937",
  },
  presetTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  presetBadge: {
    backgroundColor: "rgba(239, 68, 68, 0.15)",
    color: "#f87171",
    fontSize: 10,
    fontWeight: "bold",
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: 4,
  },
  simText: {
    color: "#38bdf8",
    fontSize: 12,
    fontWeight: "bold",
  },
  presetTitle: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "bold",
  },
  presetDesc: {
    color: "#94a3b8",
    fontSize: 12,
    marginTop: 4,
    lineHeight: 16,
  },
  resultCard: {
    backgroundColor: "#064e3b",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "#10b981",
    marginTop: 10,
  },
  resultTitle: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "bold",
  },
  resultMsg: {
    color: "#a7f3d0",
    fontSize: 12,
    marginTop: 4,
  },
  metricRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 14,
  },
  metricBox: {
    backgroundColor: "rgba(0, 0, 0, 0.3)",
    padding: 8,
    borderRadius: 8,
    alignItems: "center",
    flex: 1,
    marginHorizontal: 3,
  },
  metricLabel: {
    color: "#a7f3d0",
    fontSize: 9,
    fontWeight: "bold",
  },
  metricVal: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "bold",
    marginTop: 2,
  },
  mapWrap: {
    marginTop: 10,
  },
  mapLabel: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "600",
    marginBottom: 6,
  },
  loadingWrap: {
    padding: 20,
    alignItems: "center",
  },
  loadingText: {
    color: "#38bdf8",
    fontSize: 12,
    marginTop: 8,
  },
});
