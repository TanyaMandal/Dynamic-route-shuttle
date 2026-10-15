import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from "react-native";
import { api } from "../api/client";
import LeafletRouteMap from "../components/LeafletRouteMap";

export default function AdminMapScreen() {
  const [plan, setPlan] = useState(null);
  const [selectedShuttleId, setSelectedShuttleId] = useState(null);

  useEffect(() => {
    api.getLatestPlan()
      .then((p) => setPlan(p))
      .catch((e) => console.warn(e));
  }, []);

  const routes = plan?.routes || [];
  const activeRoute = selectedShuttleId
    ? routes.find((r) => r.shuttle_id === selectedShuttleId)
    : null;

  return (
    <View style={styles.container}>
      {/* Shuttle Filter Tabs */}
      <View style={styles.filterBar}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <TouchableOpacity
            style={[styles.filterChip, selectedShuttleId === null && styles.activeFilterChip]}
            onPress={() => setSelectedShuttleId(null)}
          >
            <Text
              style={[
                styles.filterChipText,
                selectedShuttleId === null && styles.activeFilterChipText,
              ]}
            >
              All Shuttles ({routes.length})
            </Text>
          </TouchableOpacity>

          {routes.map((r) => (
            <TouchableOpacity
              key={r.shuttle_id}
              style={[
                styles.filterChip,
                selectedShuttleId === r.shuttle_id && styles.activeFilterChip,
              ]}
              onPress={() => setSelectedShuttleId(r.shuttle_id)}
            >
              <Text
                style={[
                  styles.filterChipText,
                  selectedShuttleId === r.shuttle_id && styles.activeFilterChipText,
                ]}
              >
                {r.shuttle_name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Map View */}
      <View style={styles.mapContainer}>
        <LeafletRouteMap routes={routes} activeShuttleId={selectedShuttleId} />
      </View>

      {/* Manifest Drawer */}
      <View style={styles.manifestDrawer}>
        <Text style={styles.drawerTitle}>
          {activeRoute
            ? `${activeRoute.shuttle_name} Stop Sequence (${activeRoute.stops.length} Stops)`
            : "Select a shuttle above to view stop sequences & riders"}
        </Text>

        <ScrollView style={styles.stopsList}>
          {(activeRoute ? activeRoute.stops : []).map((st) => (
            <View key={st.sequence_num} style={styles.stopItem}>
              <View style={styles.stopNumCircle}>
                <Text style={styles.stopNum}>{st.sequence_num}</Text>
              </View>
              <View style={styles.stopDetails}>
                <Text style={styles.stopName}>{st.stop_name}</Text>
                <Text style={styles.stopMeta}>
                  ETA: <b>{st.estimated_arrival_time}</b> • 👥 {st.passenger_count} Riders
                </Text>
                <Text style={styles.passengerNames} numberOfLines={1}>
                  {st.passenger_names?.join(", ")}
                </Text>
              </View>
            </View>
          ))}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#090d16",
  },
  filterBar: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    backgroundColor: "#111827",
    borderBottomWidth: 1,
    borderBottomColor: "#1f2937",
  },
  filterChip: {
    backgroundColor: "#1f2937",
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: "#374151",
  },
  activeFilterChip: {
    backgroundColor: "#2563eb",
    borderColor: "#3b82f6",
  },
  filterChipText: {
    color: "#9ca3af",
    fontSize: 12,
    fontWeight: "600",
  },
  activeFilterChipText: {
    color: "#ffffff",
  },
  mapContainer: {
    flex: 1,
    padding: 10,
  },
  manifestDrawer: {
    height: 180,
    backgroundColor: "#111827",
    borderTopWidth: 1,
    borderTopColor: "#1f2937",
    padding: 12,
  },
  drawerTitle: {
    color: "#f8fafc",
    fontSize: 13,
    fontWeight: "700",
    marginBottom: 8,
  },
  stopsList: {
    flex: 1,
  },
  stopItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#1f2937",
    borderRadius: 8,
    padding: 8,
    marginBottom: 6,
  },
  stopNumCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#2563eb",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 10,
  },
  stopNum: {
    color: "#ffffff",
    fontSize: 11,
    fontWeight: "bold",
  },
  stopDetails: {
    flex: 1,
  },
  stopName: {
    color: "#f8fafc",
    fontSize: 13,
    fontWeight: "600",
  },
  stopMeta: {
    color: "#94a3b8",
    fontSize: 11,
    marginTop: 2,
  },
  passengerNames: {
    color: "#64748b",
    fontSize: 10,
    marginTop: 2,
  },
});
