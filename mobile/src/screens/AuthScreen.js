import React, { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { api } from "../api/client";

export default function AuthScreen({ onLoginSuccess }) {
  const [role, setRole] = useState("admin"); // 'admin' or 'employee'
  const [email, setEmail] = useState("admin@techpark.com");
  const [password, setPassword] = useState("admin123");
  const [loading, setLoading] = useState(false);

  const handleRoleSwitch = (selectedRole) => {
    setRole(selectedRole);
    if (selectedRole === "admin") {
      setEmail("admin@techpark.com");
      setPassword("admin123");
    } else {
      setEmail("employee@techpark.com");
      setPassword("emp123");
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    try {
      const user = await api.login(email, password);
      onLoginSuccess(user);
    } catch (err) {
      Alert.alert("Login Notice", err.message || "Failed to authenticate with backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.badge}>MCA Minor Project Prototype</Text>
        <Text style={styles.title}>ShuttleFlow</Text>
        <Text style={styles.subtitle}>Dynamic Employee Shuttle Routing System</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Sign In / Select Persona</Text>

        <View style={styles.roleTabs}>
          <TouchableOpacity
            style={[styles.roleTab, role === "admin" && styles.activeRoleTab]}
            onPress={() => handleRoleSwitch("admin")}
          >
            <Text style={[styles.roleTabText, role === "admin" && styles.activeRoleText]}>
              🛡️ Transport Admin
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.roleTab, role === "employee" && styles.activeRoleTab]}
            onPress={() => handleRoleSwitch("employee")}
          >
            <Text style={[styles.roleTabText, role === "employee" && styles.activeRoleText]}>
              👤 Employee Rider
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Corporate Email</Text>
        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
          placeholder="user@techpark.com"
          placeholderTextColor="#64748b"
        />

        <Text style={styles.label}>Password</Text>
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          placeholder="••••••••"
          placeholderTextColor="#64748b"
        />

        <TouchableOpacity style={styles.loginBtn} onPress={handleLogin} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#ffffff" />
          ) : (
            <Text style={styles.loginBtnText}>
              Launch as {role === "admin" ? "Administrator" : "Employee"}
            </Text>
          )}
        </TouchableOpacity>

        <Text style={styles.hintText}>
          ⚡ 1-Click quick login pre-configured for both roles.
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#090d16",
    justifyContent: "center",
    padding: 20,
  },
  header: {
    alignItems: "center",
    marginBottom: 28,
  },
  badge: {
    backgroundColor: "#1e293b",
    color: "#38bdf8",
    fontSize: 12,
    fontWeight: "bold",
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 20,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#334155",
  },
  title: {
    fontSize: 32,
    fontWeight: "800",
    color: "#f8fafc",
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 14,
    color: "#94a3b8",
    marginTop: 4,
    textAlign: "center",
  },
  card: {
    backgroundColor: "#111827",
    borderRadius: 16,
    padding: 22,
    borderWidth: 1,
    borderColor: "#1f2937",
    shadowColor: "#000",
    shadowOpacity: 0.4,
    shadowRadius: 10,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#f3f4f6",
    marginBottom: 16,
  },
  roleTabs: {
    flexDirection: "row",
    backgroundColor: "#1f2937",
    borderRadius: 8,
    padding: 4,
    marginBottom: 18,
  },
  roleTab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: "center",
    borderRadius: 6,
  },
  activeRoleTab: {
    backgroundColor: "#2563eb",
  },
  roleTabText: {
    color: "#9ca3af",
    fontSize: 13,
    fontWeight: "600",
  },
  activeRoleText: {
    color: "#ffffff",
  },
  label: {
    color: "#d1d5db",
    fontSize: 12,
    fontWeight: "600",
    marginBottom: 6,
    textTransform: "uppercase",
  },
  input: {
    backgroundColor: "#1f2937",
    borderRadius: 8,
    padding: 12,
    color: "#ffffff",
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#374151",
    fontSize: 14,
  },
  loginBtn: {
    backgroundColor: "#2563eb",
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 6,
  },
  loginBtnText: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "700",
  },
  hintText: {
    color: "#6b7280",
    fontSize: 12,
    textAlign: "center",
    marginTop: 14,
  },
});
