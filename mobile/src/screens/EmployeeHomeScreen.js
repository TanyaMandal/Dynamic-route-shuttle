import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
} from "react-native";
import { api } from "../api/client";
import LeafletRouteMap from "../components/LeafletRouteMap";

const SAMPLE_SECTORS = [
  { name: "HSR Layout Sector 1", lat: 12.9121, lng: 77.6446 },
  { name: "BTM Layout 2nd Stage", lat: 12.914, lng: 77.61 },
  { name: "Koramangala 4th Block", lat: 12.9345, lng: 77.6265 },
  { name: "Indiranagar 100ft Road", lat: 12.9719, lng: 77.6412 },
  { name: "Kadubeesanahalli Circle", lat: 12.937, lng: 77.693 },
];

export default function EmployeeHomeScreen({ user, onLogout }) {
  const [loading, setLoading] = useState(false);
  const [activePlan, setActivePlan] = useState(null);
  const [myRequests, setMyRequests] = useState([]);
  const [selectedSector, setSelectedSector] = useState(SAMPLE_SECTORS[0]);
  const [deadline, setDeadline] = useState("09:00:00");
  const [empName, setEmpName] = useState(user?.full_name || "Aarav Sharma");

  const loadData = async () => {
    setLoading(true);
    try {
      const plan = await api.getLatestPlan().catch(() => null);
      setActivePlan(plan);
      const reqs = await api.getRequests().catch(() => []);
      setMyRequests(reqs.filter((r) => r.employee_name === empName));
    } catch (e) {
      console.warn("Could not load employee view:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateRequest = async () => {
    try {
      await api.createRequest({
        employee_name: empName,
        pickup_lat: selectedSector.lat,
        pickup_lng: selectedSector.lng,
        pickup_location_name: selectedSector.name,
        destination: "Central Tech Park Campus",
        arrival_deadline: deadline,
      });
      Alert.alert("Success", "Pickup request submitted for next route plan!");
      loadData();
    } catch (e) {
      Alert.alert("Request Failed", e.message || "Failed to submit request.");
    }
  };

  // Find if employee is assigned in active plan
  let assignedShuttle = null;
  let assignedStop = null;
  if (activePlan?.routes) {
    for (const r of activePlan.routes) {
      for (const st of r.stops || []) {
        if (st.passenger_names && st.passenger_names.some((name) => name.includes(empName.split(" ")[0]))) {
          assignedShuttle = r;
          assignedStop = st;
          break;
        }
      }
      if (assignedShuttle) break;
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Top Header */}
      <View style={styles.topBar}>
        <View>
          <Text style={styles.greeting}>Welcome back,</Text>
          <Text style={styles.userName}>{empName}</Text>
        </View>
        <TouchableOpacity style={styles.logoutBtn} onPress={onLogout}>
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>
      </View>

      {/* Assignment Card */}
      {assignedShuttle && assignedStop ? (
        <View style={styles.assignmentCard}>
          <View style={styles.badgeRow}>
            <View style={styles.statusBadge}>
              <Text style={styles.statusBadgeText}>✅ SHUTTLE CONFIRMED</Text>
            </View>
            <Text style={styles.etaText}>Pickup ETA: {assignedStop.estimated_arrival_time}</Text>
          </View>

          <Text style={styles.shuttleTitle}>{assignedShuttle.shuttle_name}</Text>
          <Text style={styles.destinationText}>Destination: Central Tech Park (Arrive ~08:50 AM)</Text>

          <View style={styles.pickupBox}>
            <Text style={styles.pickupLabel}>RECOMMENDED SHARED PICKUP POINT</Text>
            <Text style={styles.stopName}>{assignedStop.stop_name}</Text>
            <Text style={styles.walkMeta}>
              🚶 Walking distance: ~180 meters • Stop #{assignedStop.sequence_num}
            </Text>
          </View>
        </View>
      ) : (
        <View style={styles.pendingCard}>
          <Text style={styles.pendingTitle}>Commute Status: Pending Plan Optimization</Text>
          <Text style={styles.pendingSub}>
            Your transport coordinator is generating the dynamic shuttle plan. You will be notified as soon as stop sequencing is locked.
          </Text>
        </View>
      )}

      {/* Route Map Preview */}
      {activePlan?.routes && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Transit Corridor & Route</Text>
          <LeafletRouteMap
            routes={assignedShuttle ? [assignedShuttle] : activePlan.routes.slice(0, 2)}
          />
        </View>
      )}

      {/* Submit Commute Request Form */}
      <View style={styles.formCard}>
        <Text style={styles.formTitle}>Book Morning Commute</Text>
        <Text style={styles.formSub}>
          Select your residential sector and target arrival deadline:
        </Text>

        <Text style={styles.label}>Select Neighborhood Sector</Text>
        <View style={styles.sectorChips}>
          {SAMPLE_SECTORS.map((sec) => (
            <TouchableOpacity
              key={sec.name}
              style={[
                styles.sectorChip,
                selectedSector.name === sec.name && styles.activeSectorChip,
              ]}
              onPress={() => setSelectedSector(sec)}
            >
              <Text
                style={[
                  styles.sectorChipText,
                  selectedSector.name === sec.name && styles.activeSectorChipText,
                ]}
              >
                {sec.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Work Arrival Deadline</Text>
        <TextInput
          style={styles.input}
          value={deadline}
          onChangeText={setDeadline}
          placeholder="09:00:00"
          placeholderTextColor="#64748b"
        />

        <TouchableOpacity style={styles.submitBtn} onPress={handleCreateRequest}>
          <Text style={styles.submitBtnText}>Submit Commute Request</Text>
        </TouchableOpacity>
      </View>
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
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 18,
    paddingTop: 10,
  },
  greeting: {
    color: "#94a3b8",
    fontSize: 13,
  },
  userName: {
    color: "#f8fafc",
    fontSize: 20,
    fontWeight: "bold",
  },
  logoutBtn: {
    backgroundColor: "#1e293b",
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#334155",
  },
  logoutText: {
    color: "#f87171",
    fontSize: 12,
    fontWeight: "600",
  },
  assignmentCard: {
    backgroundColor: "#111827",
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: "#10b981",
    marginBottom: 20,
  },
  badgeRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  statusBadge: {
    backgroundColor: "rgba(16, 185, 129, 0.15)",
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 6,
  },
  statusBadgeText: {
    color: "#10b981",
    fontSize: 11,
    fontWeight: "bold",
  },
  etaText: {
    color: "#38bdf8",
    fontSize: 13,
    fontWeight: "bold",
  },
  shuttleTitle: {
    color: "#ffffff",
    fontSize: 22,
    fontWeight: "800",
  },
  destinationText: {
    color: "#94a3b8",
    fontSize: 13,
    marginTop: 2,
  },
  pickupBox: {
    backgroundColor: "#1f2937",
    borderRadius: 10,
    padding: 12,
    marginTop: 14,
    borderLeftWidth: 4,
    borderLeftColor: "#38bdf8",
  },
  pickupLabel: {
    color: "#38bdf8",
    fontSize: 10,
    fontWeight: "bold",
    letterSpacing: 0.5,
  },
  stopName: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "700",
    marginTop: 4,
  },
  walkMeta: {
    color: "#9ca3af",
    fontSize: 12,
    marginTop: 4,
  },
  pendingCard: {
    backgroundColor: "#1e293b",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "#334155",
    marginBottom: 20,
  },
  pendingTitle: {
    color: "#f59e0b",
    fontSize: 15,
    fontWeight: "bold",
  },
  pendingSub: {
    color: "#94a3b8",
    fontSize: 12,
    marginTop: 4,
    lineHeight: 18,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    color: "#f8fafc",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 10,
  },
  formCard: {
    backgroundColor: "#111827",
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: "#1f2937",
  },
  formTitle: {
    color: "#f8fafc",
    fontSize: 17,
    fontWeight: "bold",
  },
  formSub: {
    color: "#94a3b8",
    fontSize: 12,
    marginTop: 2,
    marginBottom: 14,
  },
  label: {
    color: "#d1d5db",
    fontSize: 12,
    fontWeight: "600",
    marginBottom: 8,
    textTransform: "uppercase",
  },
  sectorChips: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginBottom: 14,
  },
  sectorChip: {
    backgroundColor: "#1f2937",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#374151",
  },
  activeSectorChip: {
    backgroundColor: "#2563eb",
    borderColor: "#3b82f6",
  },
  sectorChipText: {
    color: "#9ca3af",
    fontSize: 12,
    fontWeight: "500",
  },
  activeSectorChipText: {
    color: "#ffffff",
    fontWeight: "bold",
  },
  input: {
    backgroundColor: "#1f2937",
    borderRadius: 8,
    padding: 12,
    color: "#ffffff",
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#374151",
    fontSize: 14,
  },
  submitBtn: {
    backgroundColor: "#2563eb",
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: "center",
  },
  submitBtnText: {
    color: "#ffffff",
    fontSize: 14,
    fontWeight: "bold",
  },
});
