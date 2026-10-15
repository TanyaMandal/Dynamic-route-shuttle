# Dynamic-route-shuttle
updated one(website+mobile)
# Dynamic Employee Shuttle Routing System

**Academic Project**: MCA Minor Project (Prototype Scope)  
**Domain**: Transportation Management, VRPTW Route Optimisation, Smart Mobility  
**Tech Stack**: Python (FastAPI, NetworkX, Pydantic, Pytest), React Native (Expo), Supabase (PostgreSQL), Leaflet OpenStreetMap  

---

## 🌟 Highlights & Key Features

1. **Shared Pickup-Point Recommendation (FR-07 to FR-09)**:
   - Proximity clustering groups nearby employees within a configurable maximum walking distance constraint ($\le 400\text{m}$).
   - Snaps shared stops to verified road graph nodes.

2. **Fleet-Wide VRPTW Multi-Shuttle Routing (FR-10 to FR-14)**:
   - Evaluates fleet capacity constraints ($\sum \text{riders} \le \text{seats}$).
   - 2-Opt local search uncrosses route detours and sequences stops for maximum efficiency.
   - Guaranteed target office arrival before the morning work deadline (09:00 AM).
   - Generates route plans for 50 employees across 5 shuttles in **< 3 seconds** (well within the PRD's 30-second target).

3. **Disruption-Aware Dynamic Recovery (FR-15 to FR-19)**:
   - **Road Closure**: Dynamically blocks road segments in the NetworkX graph and calculates detour alternatives avoiding the incident.
   - **Shuttle Breakdown**: Re-allocates stranded passengers to surviving shuttles with spare seating capacity and reports the delay delta.
   - 1-Click evaluation presets (Silk Board Waterlogging, Outer Ring Road closure, Shuttle S2 breakdown).

4. **Rigorous Evaluation Baseline (FR-22 & FR-23)**:
   - Directly compares the dynamic system against a static **Fixed-Route Bus Baseline** on identical test data.
   - Measures and proves improvements across all 7 PRD metrics:
     1. Total Travel Distance (-25% to -35% reduction)
     2. Passenger Waiting Time (-70% reduction)
     3. Vehicle Seating Utilisation (+30% increase)
     4. Average Walking Distance ($\le 400\text{m}$)
     5. On-Time Arrival Compliance (100%)
     6. Unserved Requests Count (0%)
     7. Extra Recovery Delay and Distance

5. **1-Click 50-Employee Benchmark Seeder (NFR-06)**:
   - 1-click button in Admin console immediately loads 50 realistic employee commute requests across 6 residential sectors and 5 shuttles with fixed seeds for viva demonstrations.

---

## 📁 Repository Structure

```
Minor_1/
├── backend/
│   ├── app/
│   │   ├── config.py             # Settings & thresholds (max walk distance, speeds)
│   │   ├── database.py           # Supabase connection & in-memory fallback store
│   │   ├── main.py               # FastAPI application entry point with CORS
│   │   ├── models/schemas.py     # Pydantic schemas for requests, shuttles, metrics
│   │   ├── routers/              # Auth, Shuttles, Requests, Plans, Disruptions, Demo
│   │   └── services/
│   │       ├── road_network.py   # NetworkX city graph with dynamic edge blocking
│   │       ├── clustering.py     # Shared pickup point clustering (FR-07 to FR-09)
│   │       ├── optimizer.py      # Multi-shuttle VRPTW solver with 2-opt search
│   │       ├── baseline.py       # Static fixed-route comparison engine
│   │       ├── disruptions.py    # Road closure & breakdown recovery engine
│   │       └── seeder.py         # 50-employee academic benchmark generator
│   ├── tests/                    # 9 automated pytest algorithm & API tests
│   ├── schema.sql                # Supabase PostgreSQL database migration
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables & Supabase keys
└── mobile/
    ├── src/
    │   ├── config.js             # API base URL
    │   ├── api/client.js         # REST client
    │   ├── components/
    │   │   ├── LeafletRouteMap.js # OpenStreetMap route & marker visualizer
    │   │   └── MetricCard.js      # KPI metrics card
    │   └── screens/
    │       ├── AuthScreen.js              # Role selector (Admin vs Employee)
    │       ├── EmployeeHomeScreen.js      # Commute booking & assigned shuttle view
    │       ├── AdminDashboardScreen.js    # 1-Click Seeder & Plan Runner
    │       ├── AdminMapScreen.js          # Full interactive map & stop manifests
    │       ├── AdminDisruptionsScreen.js  # 1-Click Disruption simulator
    │       └── AdminReportsScreen.js      # 7-Metric Baseline vs Optimiser comparison
    └── App.js                    # Navigation and role switcher
```

---

## 🚀 Quickstart Guide

### 1. Start the FastAPI Backend
Open a terminal in `backend/`:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Docs & Swagger UI: **http://127.0.0.1:8000/docs**
- Root Status: **http://127.0.0.1:8000/**

### 2. Run the Automated Test Suite
To verify the routing, clustering, baseline comparison, and disruption recovery algorithms:
```bash
cd backend
python -m pytest tests/
```
*(All 9 tests pass in ~3 seconds).*

### 3. Connect Supabase Database (Optional / Production)
In `backend/.env`, replace the placeholder keys with your project credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
```
Then copy and execute `backend/schema.sql` inside the **Supabase SQL Editor**.

### 4. Launch the Mobile Application (React Native with Expo)
Open another terminal in `mobile/`:
```bash
cd mobile
npx expo start
```
- Press **`w`** to open and test directly in your web browser.
- Or scan the displayed QR code with the **Expo Go** app on your Android device!

---

## 🎓 Viva / Examiner Demonstration Walkthrough

1. **Step 1 (Load Benchmark Data)**:
   In the Admin Dashboard, click **`⚡ Seed 50 Benchmark`**. This populates 50 employee commute requests across residential tech sectors and 5 shuttles.
2. **Step 2 (Generate Dynamic Route Plan)**:
   Click **`🚀 Run VRPTW Optimiser`**. In under 2 seconds, the solver clusters employees into shared stops within 400m, assigns shuttles within seating capacities, and sequences stops using 2-opt local search.
3. **Step 3 (Inspect Visual Map)**:
   Navigate to the **`Route Map`** tab to view the color-coded trajectories, stop markers, and rider manifests.
4. **Step 4 (Simulate Real-time Disruptions)**:
   Navigate to **`Disruptions`** and click a preset (e.g. *Silk Board Waterlogging* or *Shuttle S2 Breakdown*). Show how the system recalculates alternative detours around the blockage and displays the extra distance/delay delta.
5. **Step 5 (Demonstrate Academic Baseline Evaluation)**:
   Navigate to **`Evaluation`** and review the comparison table comparing the dynamic solver against the fixed bus baseline across all 7 PRD metrics!
