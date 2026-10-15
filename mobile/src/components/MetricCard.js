import React from "react";
import { View, Text, StyleSheet } from "react-native";

export default function MetricCard({ title, value, unit = "", subtext = "", isHighlight = false, trend = null }) {
  return (
    <View style={[styles.card, isHighlight && styles.highlightCard]}>
      <Text style={styles.title}>{title}</Text>
      <View style={styles.valueRow}>
        <Text style={[styles.value, isHighlight && styles.highlightValue]}>
          {value}
        </Text>
        {unit ? <Text style={styles.unit}>{unit}</Text> : null}
      </View>
      {subtext ? <Text style={styles.subtext}>{subtext}</Text> : null}
      {trend ? (
        <View style={[styles.trendBadge, trend.positive ? styles.positiveBadge : styles.neutralBadge]}>
          <Text style={[styles.trendText, trend.positive ? styles.positiveText : styles.neutralText]}>
            {trend.text}
          </Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: "#334155",
    flex: 1,
    minWidth: 140,
    margin: 6,
  },
  highlightCard: {
    borderColor: "#38bdf8",
    backgroundColor: "#0f233f",
  },
  title: {
    color: "#94a3b8",
    fontSize: 12,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  valueRow: {
    flexDirection: "row",
    alignItems: "baseline",
    marginTop: 6,
  },
  value: {
    color: "#f8fafc",
    fontSize: 22,
    fontWeight: "bold",
  },
  highlightValue: {
    color: "#38bdf8",
  },
  unit: {
    color: "#94a3b8",
    fontSize: 13,
    marginLeft: 4,
    fontWeight: "500",
  },
  subtext: {
    color: "#64748b",
    fontSize: 11,
    marginTop: 4,
  },
  trendBadge: {
    marginTop: 8,
    alignSelf: "flex-start",
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: 4,
  },
  positiveBadge: {
    backgroundColor: "rgba(16, 185, 129, 0.15)",
  },
  neutralBadge: {
    backgroundColor: "rgba(148, 163, 184, 0.15)",
  },
  trendText: {
    fontSize: 11,
    fontWeight: "bold",
  },
  positiveText: {
    color: "#10b981",
  },
  neutralText: {
    color: "#94a3b8",
  },
});
