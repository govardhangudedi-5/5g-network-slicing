"""
5G Network Slicing Simulation — Flask Backend
Dynamic Resource Allocation Algorithm with QoS, History, Topology & Fault Simulation
======================================================================================
SOFTWARE SIMULATION ONLY — Academic demonstration of 5G logical slicing.
No real 5G hardware, radio towers, or physical cellular network involved.
"""

from flask import Flask, render_template, jsonify, request
import copy
import time
from datetime import datetime

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Network Capacity & Minimum Reservations (Mbps)
# ─────────────────────────────────────────────────────────────────────────────
TOTAL_CAPACITY = 100

# Guaranteed minimum allocations to prevent complete starvation
MIN_RESERVATIONS = {
    "emergency": 15,  # Mission-critical URLLC slice baseline
    "iot":       10,  # Massive IoT mMTC telemetry baseline
    "video":      5,  # Enhanced Mobile Broadband (eMBB) baseline
}

# Priority weights (higher number = higher scheduling priority)
PRIORITY_WEIGHTS = {
    "emergency": 3,   # HIGH priority (Ambulances, emergency response)
    "iot":       2,   # MEDIUM priority (Smart sensors, traffic signals)
    "video":     1,   # NORMAL priority (CCTV, 4K streaming, entertainment)
}

# ─────────────────────────────────────────────────────────────────────────────
# QoS Baseline Parameters (Simulated ideal values)
# ─────────────────────────────────────────────────────────────────────────────
QOS_BASE = {
    "emergency": {"latency": 4.5,   "jitter": 1.0,  "packet_loss": 0.01},  # URLLC target < 10ms
    "iot":       {"latency": 18.0,  "jitter": 3.0,  "packet_loss": 0.05},  # mMTC tolerant
    "video":     {"latency": 28.0,  "jitter": 5.0,  "packet_loss": 0.10},  # eMBB throughput-focused
}

# Configurable QoS Thresholds
QOS_THRESHOLDS = {
    "latency_warning":     40.0,   # ms
    "latency_fail":        80.0,   # ms
    "jitter_warning":      15.0,   # ms
    "jitter_fail":         35.0,   # ms
    "packet_loss_warning": 1.0,    # %
    "packet_loss_fail":    4.0,    # %
}

# ─────────────────────────────────────────────────────────────────────────────
# Default Initial State (Total = 100 Mbps)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_STATE = {
    "total_bandwidth": TOTAL_CAPACITY,
    "allocated_bandwidth": TOTAL_CAPACITY,
    "available_bandwidth": 0,
    "utilization": 72,
    "network_status": "ONLINE",
    "slicing_status": "ACTIVE",
    "allocation_mode": "DYNAMIC_PRIORITY",
    "active_scenario": "normal",
    "last_updated": time.strftime("%H:%M:%S"),
    "simulation_label": "SIMULATED METRICS ONLY",
    "total_demand": 100,
    "unmet_demand": 0,
    "slices": {
        "emergency": {
            "id": "emergency",
            "name": "Emergency Slice",
            "short_name": "Emergency",
            "type": "URLLC (Ultra-Reliable Low-Latency)",
            "icon": "🚑",
            "endpoints": "Ambulances & Emergency Services",
            "bandwidth": 20,
            "demand": 20,
            "min_guarantee": MIN_RESERVATIONS["emergency"],
            "unmet_demand": 0,
            "priority": "HIGH",
            "priority_weight": PRIORITY_WEIGHTS["emergency"],
            "traffic": "NORMAL",
            "status": "ACTIVE",
            "color": "#ef4444",
            "latency": 4.5,
            "jitter": 1.0,
            "packet_loss": 0.01,
            "qos_status": "PASS",
        },
        "iot": {
            "id": "iot",
            "name": "Smart IoT Slice",
            "short_name": "Smart IoT",
            "type": "mMTC (Massive Machine Type Comms)",
            "icon": "🚦",
            "endpoints": "Smart-City Sensors & Traffic Grid",
            "bandwidth": 30,
            "demand": 30,
            "min_guarantee": MIN_RESERVATIONS["iot"],
            "unmet_demand": 0,
            "priority": "MEDIUM",
            "priority_weight": PRIORITY_WEIGHTS["iot"],
            "traffic": "NORMAL",
            "status": "ACTIVE",
            "color": "#f59e0b",
            "latency": 18.0,
            "jitter": 3.0,
            "packet_loss": 0.05,
            "qos_status": "PASS",
        },
        "video": {
            "id": "video",
            "name": "Video Slice",
            "short_name": "Video",
            "type": "eMBB (Enhanced Mobile Broadband)",
            "icon": "🎥",
            "endpoints": "CCTV Feeds & Video Streaming",
            "bandwidth": 50,
            "demand": 50,
            "min_guarantee": MIN_RESERVATIONS["video"],
            "unmet_demand": 0,
            "priority": "NORMAL",
            "priority_weight": PRIORITY_WEIGHTS["video"],
            "traffic": "NORMAL",
            "status": "ACTIVE",
            "color": "#3b82f6",
            "latency": 28.0,
            "jitter": 5.0,
            "packet_loss": 0.10,
            "qos_status": "PASS",
        },
    },
    "alerts": [
        {
            "id": "init-1",
            "timestamp": time.strftime("%H:%M:%S"),
            "severity": "INFO",
            "slice": "All Slices",
            "title": "5G Slice Orchestrator Online",
            "message": "Initialized 3 logical slices over 100 Mbps shared virtual radio resource.",
            "cause": "System startup / initial state loaded.",
            "recommendation": "Network healthy. Ready to simulate traffic demand scenarios.",
        }
    ],
}

# Runtime In-Memory Simulation Storage
network_state = copy.deepcopy(DEFAULT_STATE)
before_snapshot = {"emergency": 20, "iot": 30, "video": 50}
after_snapshot = {"emergency": 20, "iot": 30, "video": 50}
simulation_history = []
util_timeline = [72] * 20

# ─────────────────────────────────────────────────────────────────────────────
# Predefined Simulation Scenario Catalog
# ─────────────────────────────────────────────────────────────────────────────
SCENARIO_DEFINITIONS = {
    "normal": {
        "label": "Normal Traffic",
        "demands": {"emergency": 20, "iot": 30, "video": 50},
        "traffic_levels": {"emergency": "NORMAL", "iot": "NORMAL", "video": "NORMAL"},
        "description": "Baseline traffic distribution across all services.",
        "degraded_slice": None,
    },
    "emergency": {
        "label": "Emergency Traffic Surge",
        "demands": {"emergency": 60, "iot": 20, "video": 30},
        "traffic_levels": {"emergency": "HIGH", "iot": "NORMAL", "video": "NORMAL"},
        "description": "Critical emergency broadcast / multiple ambulances dispatched.",
        "degraded_slice": None,
    },
    "iot": {
        "label": "Smart IoT Traffic Surge",
        "demands": {"emergency": 20, "iot": 60, "video": 30},
        "traffic_levels": {"emergency": "NORMAL", "iot": "HIGH", "video": "NORMAL"},
        "description": "Citywide smart sensor telemetry flood and traffic sync spike.",
        "degraded_slice": None,
    },
    "video": {
        "label": "Video Traffic Surge",
        "demands": {"emergency": 15, "iot": 20, "video": 75},
        "traffic_levels": {"emergency": "NORMAL", "iot": "NORMAL", "video": "HIGH"},
        "description": "Major stadium event or citywide 4K CCTV surveillance streaming.",
        "degraded_slice": None,
    },
    "congestion": {
        "label": "Network Congestion",
        "demands": {"emergency": 55, "iot": 50, "video": 60},
        "traffic_levels": {"emergency": "HIGH", "iot": "HIGH", "video": "HIGH"},
        "description": "Total network demand (165 Mbps) exceeds physical carrier capacity (100 Mbps).",
        "degraded_slice": None,
    },
    "degradation": {
        "label": "Slice Degradation",
        "demands": {"emergency": 20, "iot": 30, "video": 50},
        "traffic_levels": {"emergency": "NORMAL", "iot": "NORMAL", "video": "NORMAL"},
        "description": "Simulated RF link interference and packet impairment on Video slice.",
        "degraded_slice": "video",
    },
    "recover": {
        "label": "Network Recovery",
        "demands": {"emergency": 20, "iot": 30, "video": 50},
        "traffic_levels": {"emergency": "NORMAL", "iot": "NORMAL", "video": "NORMAL"},
        "description": "Fault cleared, RF link quality restored, and slices re-balanced.",
        "degraded_slice": None,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# QoS Calculation Engine
# ─────────────────────────────────────────────────────────────────────────────
def calculate_qos(slice_key, traffic_level, allocated_bw, demand_bw, degraded=False):
    """
    Computes simulated QoS metrics (latency, jitter, packet loss)
    based on congestion ratio = demand / allocated bandwidth,
    traffic multiplier, and degradation factors.
    """
    base = QOS_BASE[slice_key]
    traffic_multipliers = {"LOW": 0.7, "NORMAL": 1.0, "HIGH": 1.8}
    t_mult = traffic_multipliers.get(traffic_level, 1.0)

    # Congestion factor: if demand > allocated bandwidth, delay and drop rates escalate
    congestion_ratio = demand_bw / max(1, allocated_bw)
    cong_factor = max(1.0, congestion_ratio)

    deg_latency_mult = 3.2 if degraded else 1.0
    deg_jitter_mult = 2.5 if degraded else 1.0
    deg_loss_mult = 5.0 if degraded else 1.0

    # Calculate metrics
    latency = round(base["latency"] * t_mult * (cong_factor ** 1.3) * deg_latency_mult, 1)
    jitter = round(base["jitter"] * t_mult * cong_factor * deg_jitter_mult, 1)

    # Packet loss increases steeply when capacity is exceeded
    excess_ratio = max(0.0, (demand_bw - allocated_bw) / max(1, demand_bw))
    loss_congestion_add = excess_ratio * 12.0  # drop percentage from buffer overflow
    packet_loss = round((base["packet_loss"] * t_mult * deg_loss_mult) + loss_congestion_add, 2)

    # Evaluate against thresholds
    th = QOS_THRESHOLDS
    if (latency >= th["latency_fail"] or
        jitter >= th["jitter_fail"] or
        packet_loss >= th["packet_loss_fail"]):
        qos_status = "FAIL"
    elif (latency >= th["latency_warning"] or
          jitter >= th["jitter_warning"] or
          packet_loss >= th["packet_loss_warning"]):
        qos_status = "WARNING"
    else:
        qos_status = "PASS"

    return {
        "latency": latency,
        "jitter": jitter,
        "packet_loss": packet_loss,
        "qos_status": qos_status,
        "congestion_ratio": round(congestion_ratio, 2),
    }

# ─────────────────────────────────────────────────────────────────────────────
# Priority-Aware Dynamic Allocation Algorithm
# ─────────────────────────────────────────────────────────────────────────────
def run_dynamic_allocation(demands, scenario_name, degraded_slice=None):
    """
    Deterministic Dynamic Resource Allocation Engine:
    --------------------------------------------------
    1. Capacity Constraint: SUM(allocations) == 100 Mbps strictly.
    2. Non-negativity: Every slice allocation >= 0.
    3. Starvation Prevention: Each slice preserves guaranteed minimum reservation
       (Emergency: 15 Mbps, Smart IoT: 10 Mbps, Video: 5 Mbps = 30 Mbps total min).
    4. Priority Execution:
       - Priority 3 (Emergency): Highest priority. Satisfies demand first.
       - Priority 2 (Smart IoT): Medium priority. Satisfies demand from remaining capacity.
       - Priority 1 (Video): Normal priority. Best-effort delivery.
    5. Unused capacity redistribution: Spare capacity distributed to support QoS.
    6. Unmet demand reporting when total demand > 100 Mbps.
    """
    global before_snapshot, after_snapshot, util_timeline

    # Record BEFORE snapshot
    before_snapshot = {k: network_state["slices"][k]["bandwidth"] for k in ["emergency", "iot", "video"]}

    # Clean demand values
    d_em = max(0, int(demands.get("emergency", 20)))
    d_iot = max(0, int(demands.get("iot", 30)))
    d_vid = max(0, int(demands.get("video", 50)))
    total_requested = d_em + d_iot + d_vid

    # Allocation containers
    alloc = {"emergency": 0, "iot": 0, "video": 0}

    # Step 1: Ensure minimum reservations
    alloc["emergency"] = MIN_RESERVATIONS["emergency"]
    alloc["iot"] = MIN_RESERVATIONS["iot"]
    alloc["video"] = MIN_RESERVATIONS["video"]
    remaining_pool = TOTAL_CAPACITY - sum(alloc.values())  # 100 - 30 = 70 Mbps

    # Step 2: Calculate additional demand above guaranteed minimums
    extra_demands = {
        "emergency": max(0, d_em - alloc["emergency"]),
        "iot":       max(0, d_iot - alloc["iot"]),
        "video":     max(0, d_vid - alloc["video"]),
    }

    # Step 3: Service additional demand by priority order:
    # Priority 1: Emergency
    grant_em = min(remaining_pool, extra_demands["emergency"])
    alloc["emergency"] += grant_em
    remaining_pool -= grant_em

    # Priority 2: Smart IoT
    grant_iot = min(remaining_pool, extra_demands["iot"])
    alloc["iot"] += grant_iot
    remaining_pool -= grant_iot

    # Priority 3: Video
    grant_vid = min(remaining_pool, extra_demands["video"])
    alloc["video"] += grant_vid
    remaining_pool -= grant_vid

    # Step 4: If any pool capacity remains (e.g. when total demand < 100 Mbps),
    # redistribute proportionally or to higher capacity consumers
    if remaining_pool > 0:
        # Distribute based on baseline weights: Video 50%, IoT 30%, Emergency 20%
        # or proportional to requests
        v_add = round(remaining_pool * 0.5)
        i_add = round(remaining_pool * 0.3)
        e_add = remaining_pool - (v_add + i_add)
        alloc["video"] += v_add
        alloc["iot"] += i_add
        alloc["emergency"] += e_add

    # Final sanity check: ensure total == 100 exactly
    total_alloc = sum(alloc.values())
    if total_alloc != TOTAL_CAPACITY:
        diff = TOTAL_CAPACITY - total_alloc
        alloc["video"] += diff

    # Ensure all >= 0
    for k in alloc:
        alloc[k] = max(0, alloc[k])
    assert sum(alloc.values()) == TOTAL_CAPACITY, f"Allocation sum violation: {sum(alloc.values())} != 100"

    # Step 5: Update state, slice metrics, and detect changes
    changes = []
    alerts = []
    current_time_str = time.strftime("%H:%M:%S")

    scen_info = SCENARIO_DEFINITIONS.get(scenario_name, {})
    traffic_map = scen_info.get("traffic_levels", {
        "emergency": "HIGH" if d_em > 30 else "NORMAL",
        "iot": "HIGH" if d_iot > 40 else "NORMAL",
        "video": "HIGH" if d_vid > 60 else "NORMAL",
    })

    for key in ["emergency", "iot", "video"]:
        s = network_state["slices"][key]
        old_bw = before_snapshot[key]
        new_bw = alloc[key]
        demand_bw = d_em if key == "emergency" else (d_iot if key == "iot" else d_vid)
        traffic_lvl = traffic_map.get(key, "NORMAL")

        unmet = max(0, demand_bw - new_bw)

        if old_bw != new_bw:
            changes.append({
                "slice": s["short_name"],
                "from": old_bw,
                "to": new_bw,
                "diff": new_bw - old_bw,
            })

        s["bandwidth"] = new_bw
        s["demand"] = demand_bw
        s["unmet_demand"] = unmet
        s["traffic"] = traffic_lvl

        # Slice Status determination
        is_this_degraded = (degraded_slice == key)
        if is_this_degraded:
            s["status"] = "DEGRADED"
        elif unmet > 0 or scenario_name == "congestion":
            s["status"] = "CONGESTED"
        else:
            s["status"] = "ACTIVE"

        # Compute QoS
        qos = calculate_qos(key, traffic_lvl, new_bw, demand_bw, degraded=is_this_degraded)
        s.update(qos)

        # Generate slice-level QoS alerts if WARNING or FAIL
        if qos["qos_status"] == "FAIL":
            alerts.append({
                "id": f"alert-{key}-{int(time.time()*1000)%10000}",
                "timestamp": current_time_str,
                "severity": "CRITICAL",
                "slice": s["short_name"],
                "title": f"{s['short_name']} QoS Violation (FAIL)",
                "message": f"Latency {qos['latency']}ms, Loss {qos['packet_loss']}%, Jitter {qos['jitter']}ms exceeded critical thresholds.",
                "cause": "Excessive demand or slice degradation exceeding carrier bounds.",
                "recommendation": "Allocate higher priority bandwidth or initiate slice fault recovery.",
            })
        elif qos["qos_status"] == "WARNING":
            alerts.append({
                "id": f"alert-{key}-{int(time.time()*1000)%10000}",
                "timestamp": current_time_str,
                "severity": "WARNING",
                "slice": s["short_name"],
                "title": f"{s['short_name']} Elevated Latency (WARNING)",
                "message": f"Latency at {qos['latency']}ms with {unmet} Mbps unmet demand.",
                "cause": "Traffic approaching slice allocation limits.",
                "recommendation": "Monitor queue buffers and throttle non-critical background traffic.",
            })

    # Step 6: System-wide alerts & Scenarios
    unmet_total = max(0, total_requested - TOTAL_CAPACITY)
    utilization = min(100, round((total_requested / TOTAL_CAPACITY) * 100)) if total_requested > 0 else 70

    if scenario_name == "emergency":
        alerts.insert(0, {
            "id": f"alert-scen-{int(time.time()*1000)%10000}",
            "timestamp": current_time_str,
            "severity": "CRITICAL",
            "slice": "Emergency Slice",
            "title": "🚨 Emergency Priority Preemption Activated",
            "message": "Emergency demand surged to 60 Mbps. Bandwidth immediately reallocated from Smart IoT and Video slices.",
            "cause": "URLLC mission-critical life-safety event triggered.",
            "recommendation": "Sustained Emergency slice priority until dispatch confirmation.",
        })
    elif scenario_name == "congestion":
        alerts.insert(0, {
            "id": f"alert-scen-{int(time.time()*1000)%10000}",
            "timestamp": current_time_str,
            "severity": "CRITICAL",
            "slice": "5G Network Core",
            "title": "⚠️ Carrier Congestion Overload",
            "message": f"Total demand ({total_requested} Mbps) exceeds physical 100 Mbps limit. Unmet demand: {unmet_total} Mbps.",
            "cause": "Simultaneous traffic spike across all 3 logical slices.",
            "recommendation": "Dynamic priority allocation enforced: Video slice throttled to preserve URLLC & IoT telemetry.",
        })
    elif scenario_name == "degradation":
        alerts.insert(0, {
            "id": f"alert-scen-{int(time.time()*1000)%10000}",
            "timestamp": current_time_str,
            "severity": "WARNING",
            "slice": "Video Slice",
            "title": "🔧 Simulated Radio Link Degradation",
            "message": "Video slice experiencing simulated RF multipath interference; packet loss and jitter elevated.",
            "cause": "Simulated channel degradation / cell-edge fading.",
            "recommendation": "Click 'Recover Network' to simulate RF optimization and clear link faults.",
        })
    elif scenario_name == "recover":
        alerts.insert(0, {
            "id": f"alert-scen-{int(time.time()*1000)%10000}",
            "timestamp": current_time_str,
            "severity": "INFO",
            "slice": "All Slices",
            "title": "✅ Network Slices Recovered & Re-Balanced",
            "message": "Radio impairments cleared. Standard dynamic allocation (20/30/50 Mbps) restored across slices.",
            "cause": "Operator triggered network recovery routine.",
            "recommendation": "All slices operating within target QoS thresholds.",
        })
    elif scenario_name == "iot":
        alerts.insert(0, {
            "id": f"alert-scen-{int(time.time()*1000)%10000}",
            "timestamp": current_time_str,
            "severity": "WARNING",
            "slice": "Smart IoT Slice",
            "title": "📡 Smart City IoT Telemetry Surge",
            "message": "IoT demand increased to 60 Mbps. Bandwidth dynamically expanded to 50 Mbps while protecting Emergency slice.",
            "cause": "Citywide traffic sensor synchronized reporting cycle.",
            "recommendation": "IoT slice assigned additional radio resource blocks.",
        })
    elif scenario_name == "video":
        alerts.insert(0, {
            "id": f"alert-scen-{int(time.time()*1000)%10000}",
            "timestamp": current_time_str,
            "severity": "INFO",
            "slice": "Video Slice",
            "title": "📹 Video Streaming Traffic Increase",
            "message": "eMBB demand increased to 75 Mbps. Video allocation expanded to 65 Mbps using available headroom.",
            "cause": "High-bandwidth media transmission / CCTV telemetry stream.",
            "recommendation": "Video slice expanded while preserving minimum reservations for Emergency & IoT.",
        })
    elif scenario_name == "normal":
        alerts.insert(0, {
            "id": f"alert-scen-{int(time.time()*1000)%10000}",
            "timestamp": current_time_str,
            "severity": "INFO",
            "slice": "All Slices",
            "title": "📶 Normal Traffic Profile Applied",
            "message": "Standard balanced allocations: Emergency 20 Mbps, Smart IoT 30 Mbps, Video 50 Mbps.",
            "cause": "Routine operations profile loaded.",
            "recommendation": "System stable. Total utilization within nominal parameters.",
        })

    # Update overall network state
    after_snapshot = {k: alloc[k] for k in ["emergency", "iot", "video"]}
    network_state["allocated_bandwidth"] = TOTAL_CAPACITY
    network_state["available_bandwidth"] = 0
    network_state["total_demand"] = total_requested
    network_state["unmet_demand"] = unmet_total
    network_state["utilization"] = min(100, utilization)
    network_state["active_scenario"] = scenario_name
    network_state["last_updated"] = current_time_str
    network_state["alerts"] = alerts[:8]  # Keep top 8 alerts
    network_state["network_status"] = "CONGESTED" if (scenario_name == "congestion" or unmet_total > 20) else "ONLINE"

    # Append to timeline
    util_timeline.append(min(100, utilization))
    if len(util_timeline) > 20:
        util_timeline.pop(0)

    # Append to Simulation History
    history_entry = {
        "timestamp": current_time_str,
        "scenario": SCENARIO_DEFINITIONS.get(scenario_name, {}).get("label", scenario_name.capitalize()),
        "scenario_key": scenario_name,
        "emergency_bw": alloc["emergency"],
        "iot_bw": alloc["iot"],
        "video_bw": alloc["video"],
        "total_demand": total_requested,
        "unmet_demand": unmet_total,
        "utilization": min(100, utilization),
        "qos_emergency": network_state["slices"]["emergency"]["qos_status"],
        "qos_iot": network_state["slices"]["iot"]["qos_status"],
        "qos_video": network_state["slices"]["video"]["qos_status"],
        "emergency_lat": network_state["slices"]["emergency"]["latency"],
        "iot_lat": network_state["slices"]["iot"]["latency"],
        "video_lat": network_state["slices"]["video"]["latency"],
    }
    simulation_history.insert(0, history_entry)
    if len(simulation_history) > 100:
        simulation_history.pop()

    return {
        "success": True,
        "scenario": scenario_name,
        "label": SCENARIO_DEFINITIONS.get(scenario_name, {}).get("label", scenario_name),
        "changes": changes,
        "alerts": alerts,
        "allocation": after_snapshot,
        "total_demand": total_requested,
        "unmet_demand": unmet_total,
        "utilization": min(100, utilization),
    }

# ─────────────────────────────────────────────────────────────────────────────
# Web Routes (Pages)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Home / Landing page explaining 5G Network Slicing & Architecture."""
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    """Main 5G Network Operations Center (NOC) Dashboard."""
    return render_template("dashboard.html")

@app.route("/results")
def results():
    """Advanced Analytics, Comparison Charts & Simulation History page."""
    return render_template("results.html")

# ─────────────────────────────────────────────────────────────────────────────
# REST API Endpoints
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/state")
def api_state():
    """Retrieve full live simulation state, snapshot, thresholds, and timeline."""
    return jsonify({
        "success": True,
        "state": network_state,
        "before": before_snapshot,
        "after": after_snapshot,
        "util_timeline": util_timeline,
        "thresholds": QOS_THRESHOLDS,
        "capacity": TOTAL_CAPACITY,
        "history_count": len(simulation_history),
    })

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    """
    Execute a traffic simulation scenario or custom demand.
    Accepts JSON:
      {"scenario": "emergency" | "iot" | "video" | "congestion" | "degradation" | "recover" | "normal" | "custom",
       "demands": {"emergency": int, "iot": int, "video": int} [optional],
       "degraded_slice": "video" | "iot" | "emergency" | null [optional]}
    """
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "normal")

    if scenario not in SCENARIO_DEFINITIONS and scenario != "custom":
        return jsonify({
            "success": False,
            "error": f"Invalid scenario '{scenario}'. Allowed: {list(SCENARIO_DEFINITIONS.keys()) + ['custom']}",
        }), 400

    try:
        if scenario == "custom":
            demands = data.get("demands", {"emergency": 20, "iot": 30, "video": 50})
            degraded_slice = data.get("degraded_slice", None)
            result = run_dynamic_allocation(demands, "custom", degraded_slice=degraded_slice)
        else:
            scen_cfg = SCENARIO_DEFINITIONS[scenario]
            result = run_dynamic_allocation(
                scen_cfg["demands"],
                scenario,
                degraded_slice=scen_cfg.get("degraded_slice")
            )

        result.update({
            "state": network_state,
            "before": before_snapshot,
            "after": after_snapshot,
            "util_timeline": util_timeline,
            "thresholds": QOS_THRESHOLDS,
        })
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Restore network to default initial state (20 / 30 / 50 Mbps)."""
    global network_state, before_snapshot, after_snapshot, util_timeline, simulation_history
    before_snapshot = {k: network_state["slices"][k]["bandwidth"] for k in ["emergency", "iot", "video"]}
    network_state = copy.deepcopy(DEFAULT_STATE)
    after_snapshot = {"emergency": 20, "iot": 30, "video": 50}
    util_timeline = [72] * 20
    # Keep simulation history or keep a reset marker
    reset_entry = {
        "timestamp": time.strftime("%H:%M:%S"),
        "scenario": "Reset Simulation",
        "scenario_key": "reset",
        "emergency_bw": 20,
        "iot_bw": 30,
        "video_bw": 50,
        "total_demand": 100,
        "unmet_demand": 0,
        "utilization": 72,
        "qos_emergency": "PASS",
        "qos_iot": "PASS",
        "qos_video": "PASS",
        "emergency_lat": 4.5,
        "iot_lat": 18.0,
        "video_lat": 28.0,
    }
    simulation_history.insert(0, reset_entry)
    return jsonify({
        "success": True,
        "message": "System reset to default baseline allocation (20/30/50 Mbps)",
        "state": network_state,
        "before": before_snapshot,
        "after": after_snapshot,
        "util_timeline": util_timeline,
    })

@app.route("/api/history")
def api_history():
    """Retrieve full chronological simulation history."""
    return jsonify({
        "success": True,
        "history": simulation_history,
        "count": len(simulation_history),
    })

@app.route("/api/history/clear", methods=["POST"])
def api_history_clear():
    """Clear all stored simulation history."""
    global simulation_history
    simulation_history = []
    return jsonify({"success": True, "message": "Simulation history cleared successfully."})

@app.route("/api/thresholds", methods=["GET", "POST"])
def api_thresholds():
    """Retrieve or update configurable QoS thresholds."""
    global QOS_THRESHOLDS
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        for key in ["latency_warning", "latency_fail", "jitter_warning", "jitter_fail", "packet_loss_warning", "packet_loss_fail"]:
            if key in data:
                try:
                    QOS_THRESHOLDS[key] = float(data[key])
                except (ValueError, TypeError):
                    pass
        # Re-evaluate current slices against updated thresholds
        for key in ["emergency", "iot", "video"]:
            s = network_state["slices"][key]
            qos = calculate_qos(key, s["traffic"], s["bandwidth"], s["demand"], degraded=(s["status"] == "DEGRADED"))
            s.update(qos)
        return jsonify({"success": True, "thresholds": QOS_THRESHOLDS, "state": network_state})

    return jsonify({"success": True, "thresholds": QOS_THRESHOLDS})

# ─────────────────────────────────────────────────────────────────────────────
# Main Application Launcher
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    print("=" * 65)
    print("  [5G] 5G Network Slicing for Smart Services")
    print("  [NOC] Dynamic Resource Allocation System")
    print("  [NOTE] ACADEMIC SOFTWARE SIMULATION ONLY -- No physical hardware")
    print("  [URL] Server running at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(debug=True, host="127.0.0.1", port=5000)
