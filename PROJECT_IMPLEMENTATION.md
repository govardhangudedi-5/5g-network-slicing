# Project Implementation Document
## 5G Network Slicing for Smart Services with Dynamic Resource Allocation

---

### Project Metadata
- **Project Title:** 5G Network Slicing for Smart Services with Dynamic Resource Allocation
- **Domain:** Computer Networks, Next-Generation Telecommunications, Software-Defined Networking (SDN)
- **Technology Stack:** Python 3, Flask, HTML5, CSS3, Vanilla JavaScript (ES6), Chart.js
- **Network Scope:** 100 Mbps Fixed Physical Carrier Simulation (In-Memory State Machine)
- **Repository:** `https://github.com/govardhangudedi-5/5g-network-slicing`
- **Notice:** Software-based academic simulation; no physical 5G base stations or radio hardware required.

---

## 1. Executive Summary & Abstract

With the advent of Fifth Generation (5G) cellular networks, physical network infrastructure must support heterogeneous applications with drastically divergent requirements. A single physical carrier must concurrently serve:
1. **Ultra-Reliable Low-Latency Communication (URLLC):** Mission-critical emergency telemedicine and ambulance telemetry requiring near-zero latency and zero packet loss.
2. **Massive Machine-Type Communication (mMTC):** High-density smart city sensors and traffic grids with periodic, small-payload transmission.
3. **Enhanced Mobile Broadband (eMBB):** Bandwidth-hungry 4K municipal CCTV feeds and video streaming requiring high throughput.

This project implements an interactive, full-stack **5G Network Operations Center (NOC)** simulator. It logically partitions a **100 Mbps virtual carrier** into three isolated slices, dynamically reallocating bandwidth in real time using a deterministic, priority-aware algorithm while continuously monitoring Quality of Service (QoS) telemetry against configurable Service Level Agreement (SLA) thresholds.

---

## 2. Problem Statement & Project Objectives

### 2.1 The Problem
In legacy 3G/4G systems, radio resource blocks are assigned statically or on a best-effort basis. During high data traffic spikes, best-effort video streaming can saturate the carrier, causing packet drops and latency spikes for emergency response communications. Conversely, hard-partitioning spectrum leaves bandwidth idle during off-peak emergency hours.

### 2.2 Core Objectives
- **Logical Carrier Slicing:** Partition a 100 Mbps carrier into Emergency, Smart IoT, and Video slices.
- **Dynamic Priority Allocation:** Automatically shift bandwidth to high-priority demanding slices during traffic surges.
- **Starvation Prevention:** Guarantee minimum reservations (15 Mbps Emergency, 10 Mbps IoT, 5 Mbps Video) so no service is completely starved.
- **Total Capacity Invariant:** Guarantee that total allocated bandwidth strictly equals exactly 100 Mbps at all times:
  $$\sum_{i} \text{Allocated}_i \equiv 100\text{ Mbps}, \quad \forall i, \text{Allocated}_i \ge 0$$
- **Real-Time QoS Telemetry:** Compute and display simulated Latency (ms), Jitter (ms), and Packet Loss (%) graded as **PASS**, **WARNING**, or **FAIL**.
- **Interactive 5G Topology:** Visualize data packets flowing from the 5G Core Network (AMF/SMF/UPF) to physical service endpoints.
- **Scenario Simulator:** Provide 8 operational triggers (Normal, Emergency, IoT, Video, Congestion, Degradation, Recovery, Reset).
- **Advanced Analytics & CSV Export:** 5 interactive Chart.js visualizations with a downloadable simulation history CSV report.

---

## 3. System Architecture

The application adopts a three-tier decoupled client-server architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER (UI)                         │
│   Dark Glassmorphic NOC Dashboard · HTML5 + CSS3 + Vanilla JS (ES6)    │
│                                                                        │
│   ├── templates/index.html      (Architecture & Slice Overview)        │
│   ├── templates/dashboard.html  (Live NOC Operations Center)           │
│   ├── templates/results.html    (Analytics & Simulation History)       │
│   ├── static/css/style.css      (Theme, CSS Grid/Flex, Animations)     │
│   ├── static/js/dashboard.js    (Topology, State Polling, Scenarios)   │
│   └── static/js/results.js      (5 Chart.js Charts, CSV Exporter)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST API (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER (Flask)                       │
│                         Python 3 Backend Engine                        │
│                                                                        │
│   ├── app.py: Dynamic Resource Allocation Engine (Priority-Aware)      │
│   ├── app.py: QoS Telemetry Calculator (Congestion Ratio & Jitter)     │
│   ├── app.py: Fault Injection & Network Recovery Manager               │
│   └── app.py: REST Controllers (/api/state, /api/simulate, etc.)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ In-Memory State & History
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           DATA STORAGE LAYER                           │
│   In-memory data structures: DEFAULT_STATE, simulation_history,        │
│   util_timeline, before_snapshot, after_snapshot (Zero DB dependency)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Module Implementation Breakdown

### 4.1 Backend Engine (`app.py`)
- **Capacity Definition:** Constant `TOTAL_CAPACITY = 100` Mbps.
- **Slice Definitions:**
  - **Emergency:** URLLC, Priority 3 (HIGH), Baseline: 20 Mbps, Guaranteed Min: 15 Mbps.
  - **Smart IoT:** mMTC, Priority 2 (MEDIUM), Baseline: 30 Mbps, Guaranteed Min: 10 Mbps.
  - **Video:** eMBB, Priority 1 (NORMAL), Baseline: 50 Mbps, Guaranteed Min: 5 Mbps.
- **REST API Endpoints:**
  - `GET /` — Serves landing overview page.
  - `GET /dashboard` — Serves NOC operations center.
  - `GET /results` — Serves analytics and history page.
  - `GET /api/state` — Returns full live network state, current allocations, QoS, and thresholds.
  - `POST /api/simulate` — Executes a scenario (`normal`, `emergency`, `iot`, `video`, `congestion`, `degradation`, `recover`, `custom`).
  - `POST /api/reset` — Restores baseline initial state (20 / 30 / 50 Mbps).
  - `GET /api/history` — Returns chronological simulation runs list.
  - `POST /api/history/clear` — Clears stored simulation history.
  - `GET/POST /api/thresholds` — Queries or updates configurable QoS thresholds.

### 4.2 Frontend NOC Dashboard (`templates/dashboard.html` & `static/js/dashboard.js`)
- **KPI Row:** Live counters for Carrier Capacity, Allocated Bandwidth, Available Headroom, Total Traffic Demand, Unmet Demand, and Utilization %.
- **100 Mbps Multi-Segment Bar:** Real-time percentage width animation representing exact bandwidth slices.
- **Interactive 5G Topology:** Visual flow from 5G Core (AMF/SMF/UPF) through 3 virtual slice lanes with glowing status badges to physical endpoint cards (Ambulances 🚑, Traffic Sensors 🚦, CCTV Cameras 🎥).
- **Slice Cards:** Large animated bandwidth digits, demand meters, and 4-quadrant QoS metrics (Latency, Jitter, Packet Loss, Unmet Demand).
- **Scenario Simulator:** 8 interactive triggers plus custom demand sliders drawer.
- **Alerts & Audit Log:** Severity-graded alerts (CRITICAL, WARNING, INFO) with root causes and corrective recommendations.

### 4.3 Analytics & Reporting Module (`templates/results.html` & `static/js/results.js`)
- **Chart 1:** Bandwidth Allocation by Slice (Doughnut).
- **Chart 2:** Traffic Demand vs. Allocated Bandwidth (Grouped Bar).
- **Chart 3:** Network Utilization Timeline (20-point historical line chart).
- **Chart 4:** Latency QoS Comparison between slices against SLA thresholds (Bar).
- **Chart 5:** Before vs. After Allocation Shift (Grouped Bar).
- **History Table & CSV Exporter:** Browser-generated CSV download (`5g_network_slicing_history_*.csv`).

---

## 5. Algorithmic Formulation

### 5.1 Deterministic Dynamic Allocation Algorithm
The algorithm guarantees strict adherence to the 100 Mbps carrier limit while preventing slice starvation and prioritizing mission-critical communication.

#### Mathematical Steps:
1. **Inputs:** Requested demands $D_{\text{em}}, D_{\text{iot}}, D_{\text{vid}} \ge 0$.
2. **Guaranteed Minimum Phase:**
   $$A_{\text{em}} \leftarrow 15, \quad A_{\text{iot}} \leftarrow 10, \quad A_{\text{vid}} \leftarrow 5$$
   $$\text{FreePool} \leftarrow 100 - (15 + 10 + 5) = 70\text{ Mbps}$$
3. **Excess Demand Calculation:**
   $$\Delta D_i = \max(0, D_i - A_i), \quad \forall i \in \{\text{em}, \text{iot}, \text{vid}\}$$
4. **Priority-Driven Preemption Phase:**
   - **Emergency (Rank 3 - Highest):**
     $$G_{\text{em}} = \min(\text{FreePool}, \Delta D_{\text{em}})$$
     $$A_{\text{em}} \leftarrow A_{\text{em}} + G_{\text{em}}, \quad \text{FreePool} \leftarrow \text{FreePool} - G_{\text{em}}$$
   - **Smart IoT (Rank 2 - Medium):**
     $$G_{\text{iot}} = \min(\text{FreePool}, \Delta D_{\text{iot}})$$
     $$A_{\text{iot}} \leftarrow A_{\text{iot}} + G_{\text{iot}}, \quad \text{FreePool} \leftarrow \text{FreePool} - G_{\text{iot}}$$
   - **Video (Rank 1 - Normal):**
     $$G_{\text{vid}} = \min(\text{FreePool}, \Delta D_{\text{vid}})$$
     $$A_{\text{vid}} \leftarrow A_{\text{vid}} + G_{\text{vid}}, \quad \text{FreePool} \leftarrow \text{FreePool} - G_{\text{vid}}$$
5. **Headroom Distribution Phase:**
   If $\text{FreePool} > 0$ (total demand $< 100$ Mbps), the remaining capacity is assigned proportionally (50% Video, 30% IoT, 20% Emergency) to prevent spectrum waste.
6. **Constraint Validation:**
   $$\sum_{i} A_i \equiv 100, \quad A_i \ge 0$$
   $$\text{Unmet Demand} = \max\left(0, \sum_i D_i - 100\right)$$

---

## 6. Quality of Service (QoS) Telemetry Model

Slice QoS metrics are modeled based on baseline physical transmission bounds, congestion ratios ($\rho_i = D_i / A_i$), and simulated channel impairments:

1. **Latency ($L_i$ in ms):**
   $$L_i = L_{\text{base}, i} \times T_{\text{mult}} \times \left(\max(1.0, \rho_i)\right)^{1.3} \times \delta_{\text{deg}}$$
2. **Jitter ($J_i$ in ms):**
   $$J_i = J_{\text{base}, i} \times T_{\text{mult}} \times \max(1.0, \rho_i) \times \delta_{\text{deg}}$$
3. **Packet Loss ($P_i$ in %):**
   $$P_i = \left(P_{\text{base}, i} \times T_{\text{mult}} \times \delta_{\text{deg}}\right) + 12.0 \times \max\left(0, \frac{D_i - A_i}{D_i}\right)$$

### Threshold Classification:
- **PASS:** Latency $< 40$ ms, Jitter $< 15$ ms, Packet Loss $< 1.0\%$.
- **WARNING:** $40 \le \text{Latency} < 80$ ms, $15 \le \text{Jitter} < 35$ ms, $1.0\% \le \text{Loss} < 4.0\%$.
- **FAIL:** Latency $\ge 80$ ms or Jitter $\ge 35$ ms or Packet Loss $\ge 4.0\%$.

---

## 7. Simulation Scenarios & Expected Outcomes

| Scenario Name | Traffic Demands | Bandwidth Allocations | Total | Unmet | Status & QoS |
|:---|:---|:---|:---|:---|:---|
| **1. Normal** | Em: 20, IoT: 30, Vid: 50 | **Em: 20, IoT: 30, Vid: 50** | 100 | 0 Mbps | Balanced state. All slices PASS. |
| **2. Emergency Surge** | Em: 60, IoT: 20, Vid: 30 | **Em: 60, IoT: 20, Vid: 20** | 100 | 0 Mbps | Emergency prioritized to 60 Mbps; Video throttles to 20 Mbps. |
| **3. Smart IoT Surge** | Em: 20, IoT: 60, Vid: 30 | **Em: 20, IoT: 60, Vid: 20** | 100 | 0 Mbps | IoT expanded to 60 Mbps; Emergency protected at 20 Mbps. |
| **4. Video Surge** | Em: 15, IoT: 20, Vid: 75 | **Em: 15, IoT: 20, Vid: 65** | 100 | 0 Mbps | Video granted 65 Mbps; minimum reservations preserved. |
| **5. Congestion Overload** | Em: 55, IoT: 50, Vid: 60 | **Em: 55, IoT: 40, Vid: 5** | 100 | 65 Mbps | 165 Mbps demand. Video throttled to 5 Mbps keepalive. |
| **6. Slice Degradation** | Em: 20, IoT: 30, Vid: 50 | **Em: 20, IoT: 30, Vid: 50** | 100 | 0 Mbps | RF fading on Video slice. Latency $> 80$ ms, QoS FAIL. |
| **7. Recover Network** | Em: 20, IoT: 30, Vid: 50 | **Em: 20, IoT: 30, Vid: 50** | 100 | 0 Mbps | Link cleared. Normal allocations and PASS QoS restored. |
| **8. Reset Simulation** | Baseline defaults | **Em: 20, IoT: 30, Vid: 50** | 100 | 0 Mbps | In-memory state re-initialized to initial condition. |

---

## 8. Verification & Test Results

Automated unit tests implemented in `test_app.py` execute against the Flask test harness:

```text
test_all_scenarios_and_invariant_100mbps ... ok
test_api_state_initial ................... ok
test_congestion_and_unmet_demand ......... ok
test_custom_demand_allocation ............ ok
test_emergency_priority_preemption ....... ok
test_history_and_clear ................... ok
test_invalid_scenario_error_handling ..... ok
test_reset_endpoint ...................... ok
test_routes_status_codes ................. ok
test_slice_degradation_and_qos ........... ok
test_thresholds_endpoint ................. ok

Ran 11 tests in 0.086s — 100% SUCCESS (0 errors, 0 failures)
```

---

## 9. How to Run the Application

### 9.1 Quick Start (Single Click)
Double-click [`run_project.bat`](file:///c:/Users/govar/5g%20network%20slicing/run_project.bat) in the project directory. It automatically locates Python, installs missing packages, launches the server, and opens your default browser.

### 9.2 Command Line Execution
```powershell
cd "c:\Users\govar\5g network slicing"
pip install -r requirements.txt
python app.py
```

### 9.3 Application URLs
- **Landing Overview:** `http://127.0.0.1:5000`
- **NOC Dashboard:** `http://127.0.0.1:5000/dashboard`
- **Analytics & Results:** `http://127.0.0.1:5000/results`

---

## 10. Conclusion & Academic Value

This project provides an educational demonstration of 5G Software-Defined Radio Resource Management. It proves how priority preemption, slice isolation, and dynamic reallocation guarantee mission-critical connectivity without requiring dedicated physical spectrum for every service.
