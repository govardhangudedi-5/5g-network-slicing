# 5G Network Slicing for Smart Services with Dynamic Resource Allocation

> **Academic Capstone Project in Computer Networks & 5G Telecommunications**  
> **Notice:** This project is a **software-based simulation**. It models 5G logical slicing and dynamic radio resource management in software. No real 5G hardware, base stations (gNodeB), physical radio towers, or cellular modems are involved.

---

## 1. Project Introduction

In modern Fifth Generation (5G) cellular networks, diverse applications with conflicting communication requirements must share the same underlying radio access and core network infrastructure. A single network must concurrently support:
- Mission-critical **Emergency Telemedicine & Ambulances** requiring Ultra-Reliable Low-Latency Communication (URLLC).
- High-density **Smart City IoT Sensors** generating periodic telemetry under Massive Machine-Type Communication (mMTC).
- Bandwidth-intensive **4K CCTV Feeds & Video Streaming** demanding Enhanced Mobile Broadband (eMBB).

This project implements a complete, professional, interactive web-based 5G Network Operations Center (NOC) simulator called **“5G Network Slicing for Smart Services with Dynamic Resource Allocation.”** It logically divides a fixed **100 Mbps physical carrier** into three independent virtual slices, dynamically allocating bandwidth based on traffic demand surges and priority preemption while continuously enforcing Quality of Service (QoS) guarantees.

---

## 2. Problem Statement

Traditional legacy cellular architectures (3G/4G LTE) allocate physical resources statically or on a best-effort basis across all subscribers. When a surge in casual video streaming occurs, critical emergency services or city traffic sensors can suffer from packet drops, high jitter, and bufferbloat latency.

Conversely, statically partitioning physical bandwidth leads to resource inefficiency: bandwidth reserved for ambulances sits idle during quiet periods while video streams buffer unnecessarily.

**Key Challenges Addressed:**
1. **Capacity Invariant:** Ensuring total carrier bandwidth is strictly bounded at **100 Mbps** without over-allocation or negative allocations.
2. **Priority-Aware Scheduling:** Guaranteeing that mission-critical emergency traffic always receives immediate preemption and highest priority during load surges.
3. **Starvation Prevention:** Guaranteeing minimum baseline reservations for secondary slices (IoT: 10 Mbps, Video: 5 Mbps) even during extreme emergency surges.
4. **QoS Telemetry:** Monitoring real-time latency (ms), jitter (ms), and packet loss (%) against configurable Service Level Agreement (SLA) thresholds.
5. **Congestion & Fault Recovery:** Providing operational controls to simulate carrier overload and radio link degradation with root-cause analysis and corrective recommendations.

---

## 3. Project Objectives

1. **Logical 5G Slicing:** Model three independent virtual network slices (Emergency, Smart IoT, Video) on top of a shared 100 Mbps virtual carrier.
2. **Priority Dynamic Resource Allocation Algorithm:** Implement a deterministic, priority-aware algorithm that automatically adapts bandwidth grants to fluctuating traffic demands.
3. **Interactive 5G Network Topology:** Provide a real-time responsive visual diagram tracing traffic flows from the 5G Core (AMF/SMF/UPF) through virtual slice routers to endpoint devices.
4. **QoS Telemetry & SLA Tracking:** Compute simulated latency, jitter, and packet loss, grading slice performance as **PASS**, **WARNING**, or **FAIL** against configurable thresholds.
5. **Scenario & Fault Simulator:** Provide operational simulation buttons for normal operations, emergency surges, IoT bursts, video surges, congestion overload, RF degradation, network recovery, and reset.
6. **Advanced Visual Analytics:** Display Chart.js visualizations for bandwidth distribution, traffic demand vs. allocated bandwidth, carrier utilization timeline, latency comparison, and before/after comparisons.
7. **Simulation History & CSV Export:** Maintain a full in-memory audit log of all simulation runs with a one-click working CSV export feature.

---

## 4. System Architecture

The application adopts a modular, lightweight full-stack architecture adhering to modern web and networking standards:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                            │
│  HTML5 + CSS3 (Dark Glassmorphic NOC Theme) + Vanilla JavaScript (ES6) │
│                                                                        │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐ │
│  │  Home / Overview   │ │  NOC Dashboard     │ │ Analytics & Results│ │
│  │   (index.html)     │ │  (dashboard.html)  │ │   (results.html)   │ │
│  └────────────────────┘ └────────────────────┘ └────────────────────┘ │
│            │                      │                      │            │
│            ▼                      ▼                      ▼            │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Interactive Topology · Chart.js (5 Charts) · CSV Report Exporter │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API (JSON via fetch)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                            │
│                         Python 3 + Flask API                           │
│                                                                        │
│  ┌──────────────────────┐ ┌──────────────────────┐ ┌────────────────┐  │
│  │  Dynamic Allocation  │ │    QoS Evaluation    │ │ Fault Injection│  │
│  │   Priority Engine    │ │     & Thresholds     │ │   & Recovery   │  │
│  └──────────────────────┘ └──────────────────────┘ └────────────────┘  │
│                                   │                                    │
│                                   ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ IN-MEMORY SIMULATION STATE (100 Mbps Invariant, History, Alerts) │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Components:
- **Flask REST Backend (`app.py`):** Acts as the 5G Network Slice Orchestrator, executing the deterministic allocation algorithm, managing QoS parameters, tracking historical snapshots, and enforcing capacity invariants.
- **Client Engine (`dashboard.js`):** Polls simulation state, updates DOM elements with animated transitions, controls scenario triggers, and updates the interactive topology flow.
- **Analytics Visualizer (`results.js`):** Drives 5 interactive Chart.js charts, maintains the simulation history table, and renders CSV export files.
- **Design System (`style.css`):** Custom high-contrast dark NOC styling with cybernetic glows, glassmorphism cards, and responsive layouts.

---

## 5. Technologies Used

| Technology | Purpose | Notes |
|------------|---------|-------|
| **HTML5 & CSS3** | User Interface | Custom responsive dark-themed NOC layout with CSS variables and glassmorphism |
| **Vanilla JavaScript (ES6)** | Frontend Logic | Fetch API, reactive DOM updates, SVG topology animation, CSV generator |
| **Python 3 (3.8+)** | Backend Engine | In-memory orchestration logic, RESTful API endpoints |
| **Flask 3.0+** | Web Server & Routing | Serves HTML templates and JSON API endpoints (`/api/*`) |
| **Chart.js 4.4** | Data Visualization | 5 charts: Doughnut, Grouped Bar, Timeline Line, Latency Bar, Comparison |
| **Google Fonts** | Typography | *Outfit* (Modern UI) and *JetBrains Mono* (Telecom Metrics & Numbers) |

> **Constraints Satisfied:** No React/Angular/Vue, no machine learning dependencies, no paid external APIs, and no external databases required.

---

## 6. What is 5G Network Slicing?

**Network Slicing** is an architectural paradigm standardized by 3GPP and ITU-R for 5G standalone networks. It enables mobile network operators to divide a single physical radio access and core network into multiple virtual, end-to-end, logically isolated networks customized for specific business services.

Each network slice is allocated:
- A specific share of radio resources (bandwidth in Mbps).
- Differentiated scheduling priority (Quality of Service Class Identifier / 5QI).
- Dedicated latency, jitter, and packet error rate targets.
- Independent fault isolation: issues on a casual video slice do not degrade emergency communications.

---

## 7. The Three Independent Network Slices

| Parameter | 🚑 Emergency Slice | 🚦 Smart IoT Slice | 🎥 Video Streaming Slice |
|:---|:---|:---|:---|
| **3GPP Service Class** | **URLLC** (Ultra-Reliable Low-Latency) | **mMTC** (Massive Machine Type) | **eMBB** (Enhanced Mobile Broadband) |
| **Priority Level** | **HIGH** (Priority Weight: 3) | **MEDIUM** (Priority Weight: 2) | **NORMAL** (Priority Weight: 1) |
| **Baseline Bandwidth** | **20 Mbps** (20%) | **30 Mbps** (30%) | **50 Mbps** (50%) |
| **Minimum Reservation** | **15 Mbps** (Protected baseline) | **10 Mbps** (Protected baseline) | **5 Mbps** (Keepalive baseline) |
| **Simulated Endpoints** | Connected Ambulances, Hospital Telemetry | Smart Traffic Signals, Air Sensors | 4K Municipal CCTV, Media Streaming |
| **Baseline Latency** | 4.5 ms | 18.0 ms | 28.0 ms |
| **Baseline Packet Loss** | 0.01 % | 0.05 % | 0.10 % |
| **Baseline Jitter** | 1.0 ms | 3.0 ms | 5.0 ms |
| **Initial QoS Status** | **PASS** | **PASS** | **PASS** |

$$\text{Total Initial Allocation} = 20 + 30 + 50 = 100\text{ Mbps (Fixed Carrier Limit)}$$

---

## 8. Dynamic Resource Allocation Algorithm

The core orchestration engine in `app.py` follows a deterministic, priority-aware allocation algorithm.

### Mathematical Formulation & Rules:

Let the total network capacity be fixed:
$$C_{\text{total}} = 100\text{ Mbps}$$

Each slice $i \in \{\text{emergency}, \text{iot}, \text{video}\}$ has:
- A requested traffic demand: $D_i \ge 0$
- A guaranteed minimum reservation: $M_i$ where $M_{\text{em}}=15, M_{\text{iot}}=10, M_{\text{vid}}=5$
- A scheduling priority: $P_{\text{em}} > P_{\text{iot}} > P_{\text{vid}}$

$$\sum_{i} M_i = 15 + 10 + 5 = 30\text{ Mbps reserved pool}$$
$$\text{Remaining Free Pool} = C_{\text{total}} - \sum_{i} M_i = 100 - 30 = 70\text{ Mbps}$$

### Allocation Steps:
1. **Initialize Guaranteed Minimums:**
   $$\forall i, \quad A_i \leftarrow M_i$$
2. **Calculate Additional Unmet Demands:**
   $$\Delta D_i = \max(0, D_i - M_i)$$
3. **Priority Preemption Allocation:**
   - **Emergency First ($P=3$):**  
     $$G_{\text{em}} = \min(\text{Free Pool}, \Delta D_{\text{em}})$$  
     $$A_{\text{em}} \leftarrow A_{\text{em}} + G_{\text{em}}, \quad \text{Free Pool} \leftarrow \text{Free Pool} - G_{\text{em}}$$
   - **Smart IoT Next ($P=2$):**  
     $$G_{\text{iot}} = \min(\text{Free Pool}, \Delta D_{\text{iot}})$$  
     $$A_{\text{iot}} \leftarrow A_{\text{iot}} + G_{\text{iot}}, \quad \text{Free Pool} \leftarrow \text{Free Pool} - G_{\text{iot}}$$
   - **Video Last ($P=1$):**  
     $$G_{\text{vid}} = \min(\text{Free Pool}, \Delta D_{\text{vid}})$$  
     $$A_{\text{vid}} \leftarrow A_{\text{vid}} + G_{\text{vid}}, \quad \text{Free Pool} \leftarrow \text{Free Pool} - G_{\text{vid}}$$
4. **Spare Headroom Distribution:**  
   If $\text{Free Pool} > 0$ (when total demand $< 100$ Mbps), residual bandwidth is distributed proportionally to baseline weights (Video 50%, IoT 30%, Emergency 20%) to prevent idle spectrum waste.
5. **Invariant Constraint Check:**  
   $$\sum_{i} A_i \equiv 100\text{ Mbps}, \quad \forall i, A_i \ge 0$$
6. **Unmet Demand Reporting:**  
   $$\text{Total Unmet} = \max\left(0, \sum_i D_i - C_{\text{total}}\right)$$  
   $$\forall i, \quad U_i = \max(0, D_i - A_i)$$

---

## 9. Quality of Service (QoS) Telemetry & Thresholds

Each slice's communication quality is continuously evaluated based on its allocated bandwidth, traffic congestion ratio, and simulated channel impairments:

$$\text{Congestion Factor } \rho_i = \frac{D_i}{\max(1, A_i)}$$

### Metrics Simulated:
- **Latency ($L_i$ in ms):** Base latency modulated by traffic intensity and congestion factor:
  $$L_i = L_{\text{base}, i} \times T_{\text{mult}} \times \rho_i^{1.3} \times D_{\text{mult}}$$
- **Jitter ($J_i$ in ms):** Packet arrival variation computed from congestion and link status.
- **Packet Loss ($P_i$ in %):** Buffer drop rate calculated from buffer overflow when demand exceeds granted bandwidth:
  $$P_i = P_{\text{base}, i} \times T_{\text{mult}} + 12 \times \max\left(0, \frac{D_i - A_i}{D_i}\right)$$

### Configurable QoS Thresholds:
| Metric | PASS Condition | WARNING Condition | FAIL Condition |
|:---|:---|:---|:---|
| **Latency** | $< 40.0$ ms | $40.0\text{ ms} \le L < 80.0\text{ ms}$ | $\ge 80.0$ ms |
| **Jitter** | $< 15.0$ ms | $15.0\text{ ms} \le J < 35.0\text{ ms}$ | $\ge 35.0$ ms |
| **Packet Loss** | $< 1.0$ % | $1.0\% \le P < 4.0\%$ | $\ge 4.0$ % |

Thresholds can be adjusted dynamically via the **"Configure QoS Thresholds"** modal on the NOC dashboard.

---

## 10. Congestion & Fault Simulation Controls

The dashboard provides dedicated operational scenarios to test network resilience:
1. **Network Congestion:** Simulates simultaneous traffic surges across all three slices ($D_{\text{em}}=55, D_{\text{iot}}=50, D_{\text{vid}}=60 \implies 165$ Mbps total demand). The orchestrator throttles normal-priority Video down to 5 Mbps while keeping Emergency at 55 Mbps and IoT at 40 Mbps.
2. **Slice Degradation:** Simulates temporary radio link multipath interference and fading on the Video slice. Bandwidth remains allocated, but latency spikes to $> 80$ ms and packet loss exceeds $4\%$, triggering a **FAIL** QoS state.
3. **Network Recovery:** Operator triggers a recovery routine that clears radio impairments, resets QoS statuses back to **PASS**, and returns slices to balanced operation.
4. **Interactive Custom Demand Sliders:** Allows evaluators to drag custom demand sliders for each slice and observe dynamic allocation in real time.

---

## 11. Interactive 5G Network Topology

The **Interactive 5G Topology Visualizer** on the dashboard displays:
- **5G Core Network (5GC):** Central node representing AMF (Access and Mobility Management Function), SMF (Session Management Function), and UPF (User Plane Function).
- **Virtual Slice Channels:** Three visual lanes displaying live allocated bandwidth, QoS badges, and priority tags.
- **Animated Data Stream Packets:** Real-time CSS pulsing packets indicating active throughput.
- **Simulated Physical Endpoints:**
  - 🚑 Ambulances and Emergency Hospital Telemetry
  - 🚦 Smart City Traffic Signal Mesh and Environmental Sensors
  - 🎥 Municipal 4K CCTV and Video Streaming Feeds
- **Status Highlighting:** Turns pulsing amber during congestion, pulsing red during link degradation, and smooth emerald during healthy operation.

---

## 12. Advanced Analytics & Visualizations

The **Analytics & Results** page (`/results`) provides 5 interactive Chart.js visualizations:
1. **Bandwidth Allocation by Slice:** Doughnut chart displaying percentage share of the 100 Mbps carrier.
2. **Traffic Demand vs. Allocated Bandwidth:** Grouped bar chart comparing requested demand against granted bandwidth in Mbps.
3. **Carrier Utilization Timeline:** Real-time 20-point historical timeline line chart tracking overall network load.
4. **Latency Comparison Between Slices:** Bar chart comparing URLLC, mMTC, and eMBB latency against warning thresholds.
5. **Before vs. After Comparison:** Comparison chart illustrating dynamic shifts from the previous scenario.

### CSV Export & History Management:
- **One-Click CSV Export:** Generates and downloads a clean CSV file (`5g_network_slicing_history_*.csv`) containing timestamps, scenarios, allocations, unmet demands, and QoS parameters.
- **Clear History:** Resets the simulation audit log.

---

## 13. Installation & How to Run

### Prerequisites
- Python 3.8 or higher installed on your computer.

### Step 1: Open Terminal in the Project Directory
```powershell
cd "c:\Users\govar\5g network slicing"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Launch the Application
```bash
python app.py
```
*(On Windows systems where Python is registered as `py`, you may also run `py app.py`)*

### Step 4: Open in Web Browser
Navigate to the local server URL:
```
http://127.0.0.1:5000
```

---

## 14. Example Demonstration Scenarios

| Button / Scenario | Requested Demand | Granted Allocation | Unmet Demand | Utilization | Key Observation |
|:---|:---|:---|:---|:---|:---|
| **1. Normal Traffic** | Em: 20, IoT: 30, Vid: 50 | **Em: 20, IoT: 30, Vid: 50** | **0 Mbps** | **72%** | Standard baseline; all slices PASS QoS. |
| **2. Emergency Surge** | Em: 60, IoT: 20, Vid: 30 | **Em: 60, IoT: 20, Vid: 20** | **0 Mbps** | **100%** | Emergency receives full 60 Mbps; Video throttles to 20 Mbps. |
| **3. Smart IoT Surge** | Em: 20, IoT: 60, Vid: 30 | **Em: 20, IoT: 60, Vid: 20** | **0 Mbps** | **100%** | IoT surges to 60 Mbps; Emergency slice protected at 20 Mbps. |
| **4. Video Surge** | Em: 15, IoT: 20, Vid: 75 | **Em: 15, IoT: 20, Vid: 65** | **0 Mbps** | **100%** | Video expands to 65 Mbps using free capacity; minimums preserved. |
| **5. Network Congestion** | Em: 55, IoT: 50, Vid: 60 | **Em: 55, IoT: 40, Vid: 5** | **65 Mbps** | **100%** | Total demand 165 Mbps &gt; 100 Mbps. Video throttled to 5 Mbps keepalive. |
| **6. Slice Degradation** | Em: 20, IoT: 30, Vid: 50 | **Em: 20, IoT: 30, Vid: 50** | **0 Mbps** | **72%** | RF link impairment simulated on Video slice. Latency &gt; 80 ms, QoS FAIL. |
| **7. Recover Network** | Em: 20, IoT: 30, Vid: 50 | **Em: 20, IoT: 30, Vid: 50** | **0 Mbps** | **72%** | Radio impairments cleared; all slices restored to PASS QoS. |
| **8. Reset Simulation** | Baseline defaults | **Em: 20, IoT: 30, Vid: 50** | **0 Mbps** | **72%** | Restores initial state and clears transient alerts. |

---

## 15. REST API Documentation

| Endpoint | Method | Description | Sample Request / Response |
|:---|:---|:---|:---|
| `/` | `GET` | Home / Project Overview page | HTML response |
| `/dashboard` | `GET` | Main Operations Center (NOC) | HTML response |
| `/results` | `GET` | Analytics & Simulation Results page | HTML response |
| `/api/state` | `GET` | Retrieve full current network state, slice metrics, alerts, and timeline | `{"success": true, "state": {...}, "capacity": 100}` |
| `/api/simulate` | `POST` | Execute a traffic scenario or custom demand | Body: `{"scenario": "emergency"}` or `{"scenario": "custom", "demands": {"emergency": 50, "iot": 30, "video": 20}}` |
| `/api/reset` | `POST` | Restore network to initial baseline (20/30/50 Mbps) | `{"success": true, "message": "System reset..."}` |
| `/api/history` | `GET` | Retrieve full chronological history of simulation runs | `{"success": true, "history": [...], "count": 5}` |
| `/api/history/clear`| `POST`| Clear all stored simulation history entries | `{"success": true, "message": "History cleared"}` |
| `/api/thresholds` | `GET / POST` | Query or update configurable QoS thresholds | Body: `{"latency_warning": 45, "latency_fail": 90}` |

---

## 16. Automated Test Suite

The project includes an automated unit test suite in `test_app.py` covering:
- Route availability (`/`, `/dashboard`, `/results`)
- Invariant constraint verification ($\sum = 100$ Mbps across all scenarios)
- Non-negativity constraint verification ($A_i \ge 0$)
- Starvation prevention (minimum reservations preserved)
- Unmet demand reporting during congestion
- Slice degradation and recovery QoS state transitions
- Custom demand simulation
- Error handling for invalid scenario payloads (HTTP 400)
- Simulation history logging and clearing

To run the automated test suite:
```bash
python -m unittest test_app.py -v
```

---

## 17. Limitations & Future Enhancements

### Current Limitations:
1. **Simulation Scope:** Models traffic at the bandwidth and logical slice level; does not simulate physical RF wave propagation, beamforming, or OFDM subcarriers.
2. **In-Memory Storage:** Simulation history and state are held in memory; restarting the Flask server resets history.
3. **Single Carrier Model:** Fixed at one 100 Mbps carrier band.

### Future Enhancements:
1. **Machine Learning Predictive Slicing:** Incorporate LSTM/ARIMA models to forecast traffic surges and pre-allocate radio resource blocks proactively.
2. **Multi-Carrier & Carrier Aggregation:** Expand simulation to multi-carrier setups (e.g., Sub-6 GHz + mmWave 28 GHz).
3. **WebSocket Streaming:** Replace HTTP polling with WebSockets for sub-millisecond telemetry feeds.
4. **SLA Penalties Engine:** Model monetary SLA breach penalties based on QoS violation durations.
5. **OpenAPI / Swagger Documentation:** Add interactive Swagger UI for the REST API.

---

## 18. Project Summary & Academic Disclaimer

This project was developed as a comprehensive college capstone demonstration illustrating the principles of **Software-Defined Networking (SDN)** and **5G Network Slicing**. It bridges theoretical telecommunications concepts with full-stack software engineering.

*Developed with Python, Flask, HTML5, CSS3, Vanilla JavaScript, and Chart.js.*
