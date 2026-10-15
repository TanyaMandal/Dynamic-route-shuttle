import React from "react";
import { View, StyleSheet, Platform, Text } from "react-native";

const ROUTE_COLORS = ["#2563EB", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4"];

export default function LeafletRouteMap({ routes = [], activeShuttleId = null }) {
  // Filter by active shuttle if selected
  const displayedRoutes = activeShuttleId
    ? routes.filter((r) => r.shuttle_id === activeShuttleId)
    : routes;

  const routesJson = JSON.stringify(displayedRoutes);
  const colorsJson = JSON.stringify(ROUTE_COLORS);

  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
          body, html, #map { margin: 0; padding: 0; width: 100%; height: 100%; background: #0f172a; }
          .custom-stop-marker {
            background-color: #ffffff;
            border: 2px solid #2563eb;
            color: #0f172a;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: bold;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
          }
          .custom-office-marker {
            background: #ef4444;
            color: white;
            border: 2px solid white;
            border-radius: 6px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: bold;
          }
          .leaflet-popup-content-wrapper {
            background: #1e293b;
            color: #f8fafc;
            border-radius: 8px;
            border: 1px solid #334155;
          }
          .leaflet-popup-tip {
            background: #1e293b;
          }
        </style>
      </head>
      <body>
        <div id="map"></div>
        <script>
          const map = L.map('map').setView([12.9450, 77.6350], 12);
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
          }).addTo(map);

          // Add Central Tech Park Office Marker
          const officeIcon = L.divIcon({
            className: 'custom-office-marker',
            html: '🏢 Tech Park (Office)',
            iconSize: [120, 24]
          });
          L.marker([12.9716, 77.5946], { icon: officeIcon })
            .addTo(map)
            .bindPopup("<b>Central Tech Park Campus</b><br>Final destination for all morning shuttles.");

          const routesData = ${routesJson};
          const colors = ${colorsJson};

          if (routesData && routesData.length > 0) {
            routesData.forEach((route, idx) => {
              const color = colors[idx % colors.length];

              // Draw Shuttle Route Polyline
              if (route.polyline && route.polyline.length > 0) {
                L.polyline(route.polyline, {
                  color: color,
                  weight: 5,
                  opacity: 0.85,
                  dashArray: idx % 2 === 1 ? '6, 6' : null
                }).addTo(map).bindPopup("<b>" + route.shuttle_name + "</b><br>Distance: " + route.total_distance_km + " km<br>Duration: " + route.total_duration_min + " min");
              }

              // Draw Sequenced Stops
              if (route.stops) {
                route.stops.forEach((stop) => {
                  const stopIcon = L.divIcon({
                    className: 'custom-stop-marker',
                    html: stop.sequence_num,
                    iconSize: [24, 24]
                  });

                  const passengersList = stop.passenger_names ? stop.passenger_names.join(', ') : 'None';
                  const popupContent = "<b>" + stop.stop_name + " (Stop #" + stop.sequence_num + ")</b><br>" +
                    "ETA: <b>" + stop.estimated_arrival_time + "</b><br>" +
                    "Assigned: <b>" + stop.passenger_count + " riders</b><br>" +
                    "<small style='color:#94a3b8;'>Passengers: " + passengersList + "</small>";

                  L.marker([stop.lat, stop.lng], { icon: stopIcon })
                    .addTo(map)
                    .bindPopup(popupContent);
                });
              }
            });
          }
        </script>
      </body>
    </html>
  `;

  if (Platform.OS === "web") {
    return (
      <View style={styles.container}>
        <iframe
          srcDoc={htmlContent}
          style={{ width: "100%", height: "100%", border: "none" }}
          title="Leaflet Map"
        />
      </View>
    );
  }

  // Mobile Webview Fallback or native view
  let WebViewComponent;
  try {
    WebViewComponent = require("react-native-webview").WebView;
  } catch (e) {
    WebViewComponent = null;
  }

  if (WebViewComponent) {
    return (
      <View style={styles.container}>
        <WebViewComponent
          originWhitelist={["*"]}
          source={{ html: htmlContent }}
          style={styles.map}
        />
      </View>
    );
  }

  return (
    <View style={[styles.container, styles.fallback]}>
      <Text style={styles.fallbackText}>🗺️ Interactive Route Map Active</Text>
      <Text style={styles.fallbackSub}>
        Viewing {displayedRoutes.length} optimized shuttle trajectories
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    minHeight: 380,
    borderRadius: 12,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "#334155",
    backgroundColor: "#0f172a",
  },
  map: {
    flex: 1,
  },
  fallback: {
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  fallbackText: {
    color: "#38bdf8",
    fontSize: 16,
    fontWeight: "bold",
  },
  fallbackSub: {
    color: "#94a3b8",
    fontSize: 13,
    marginTop: 6,
  },
});
