import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
} from "react-native";
import AuthScreen from "./src/screens/AuthScreen";
import EmployeeHomeScreen from "./src/screens/EmployeeHomeScreen";
import AdminDashboardScreen from "./src/screens/AdminDashboardScreen";
import AdminMapScreen from "./src/screens/AdminMapScreen";
import AdminDisruptionsScreen from "./src/screens/AdminDisruptionsScreen";
import AdminReportsScreen from "./src/screens/AdminReportsScreen";

export default function App() {
  const [currentUser, setCurrentUser] = useState({
    id: "ADMIN_001",
    email: "admin@techpark.com",
    full_name: "Transport Coordinator",
    role: "admin",
  });
  const [adminTab, setAdminTab] = useState("dashboard"); // 'dashboard', 'map', 'disruptions', 'reports'

  // If not logged in, show Auth Screen
  if (!currentUser) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="light-content" backgroundColor="#090d16" />
        <AuthScreen onLoginSuccess={setCurrentUser} />
      </SafeAreaView>
    );
  }

  // If logged in as Employee, show Employee Experience
  if (currentUser.role === "employee") {
    return (
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="light-content" backgroundColor="#090d16" />
        <View style={styles.roleHeaderBar}>
          <Text style={styles.roleIndicator}>👤 Commuter View</Text>
          <TouchableOpacity
            style={styles.switchRoleBtn}
            onPress={() =>
              setCurrentUser({
                id: "ADMIN_001",
                email: "admin@techpark.com",
                full_name: "Transport Coordinator",
                role: "admin",
              })
            }
          >
            <Text style={styles.switchRoleText}>Switch to Admin ➔</Text>
          </TouchableOpacity>
        </View>
        <EmployeeHomeScreen user={currentUser} onLogout={() => setCurrentUser(null)} />
      </SafeAreaView>
    );
  }

  // Admin Experience with Navigation Tabs
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#090d16" />

      {/* Role Switcher & Header Bar */}
      <View style={styles.roleHeaderBar}>
        <View style={styles.adminBadge}>
          <Text style={styles.adminBadgeText}>🛡️ TRANSPORT ADMIN</Text>
        </View>
        <TouchableOpacity
          style={styles.switchRoleBtn}
          onPress={() =>
            setCurrentUser({
              id: "EMP_001",
              email: "employee@techpark.com",
              full_name: "Aarav Sharma",
              role: "employee",
            })
          }
        >
          <Text style={styles.switchRoleText}>Switch to Employee ➔</Text>
        </TouchableOpacity>
      </View>

      {/* Screen Body */}
      <View style={styles.screenContainer}>
        {adminTab === "dashboard" && (
          <AdminDashboardScreen onNavigateTab={(tab) => setAdminTab(tab)} />
        )}
        {adminTab === "map" && <AdminMapScreen />}
        {adminTab === "disruptions" && <AdminDisruptionsScreen />}
        {adminTab === "reports" && <AdminReportsScreen />}
      </View>

      {/* Bottom Navigation Bar */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={[styles.navItem, adminTab === "dashboard" && styles.activeNavItem]}
          onPress={() => setAdminTab("dashboard")}
        >
          <Text style={styles.navIcon}>📊</Text>
          <Text style={[styles.navLabel, adminTab === "dashboard" && styles.activeNavLabel]}>
            Dashboard
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, adminTab === "map" && styles.activeNavItem]}
          onPress={() => setAdminTab("map")}
        >
          <Text style={styles.navIcon}>🗺️</Text>
          <Text style={[styles.navLabel, adminTab === "map" && styles.activeNavLabel]}>
            Route Map
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, adminTab === "disruptions" && styles.activeNavItem]}
          onPress={() => setAdminTab("disruptions")}
        >
          <Text style={styles.navIcon}>⚠️</Text>
          <Text style={[styles.navLabel, adminTab === "disruptions" && styles.activeNavLabel]}>
            Disruptions
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, adminTab === "reports" && styles.activeNavItem]}
          onPress={() => setAdminTab("reports")}
        >
          <Text style={styles.navIcon}>📈</Text>
          <Text style={[styles.navLabel, adminTab === "reports" && styles.activeNavLabel]}>
            Evaluation
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#090d16",
  },
  roleHeaderBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: "#111827",
    borderBottomWidth: 1,
    borderBottomColor: "#1f2937",
  },
  roleIndicator: {
    color: "#38bdf8",
    fontSize: 12,
    fontWeight: "bold",
  },
  adminBadge: {
    backgroundColor: "rgba(37, 99, 235, 0.2)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#2563eb",
  },
  adminBadgeText: {
    color: "#60a5fa",
    fontSize: 11,
    fontWeight: "bold",
  },
  switchRoleBtn: {
    paddingVertical: 4,
    paddingHorizontal: 10,
    backgroundColor: "#1f2937",
    borderRadius: 6,
  },
  switchRoleText: {
    color: "#9ca3af",
    fontSize: 12,
    fontWeight: "600",
  },
  screenContainer: {
    flex: 1,
  },
  bottomNav: {
    flexDirection: "row",
    backgroundColor: "#111827",
    borderTopWidth: 1,
    borderTopColor: "#1f2937",
    paddingVertical: 8,
    paddingBottom: 16,
  },
  navItem: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 4,
  },
  activeNavItem: {
    borderTopWidth: 2,
    borderTopColor: "#38bdf8",
  },
  navIcon: {
    fontSize: 18,
  },
  navLabel: {
    color: "#64748b",
    fontSize: 10,
    fontWeight: "600",
    marginTop: 2,
  },
  activeNavLabel: {
    color: "#38bdf8",
    fontWeight: "bold",
  },
});
