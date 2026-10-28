/**
 * 5G Network Slicing — Dashboard NOC Controller (dashboard.js)
 * Real-time monitoring, priority dynamic allocation, topology updates,
 * QoS calculation, fault simulation & alert management.
 */

'use strict';

// ── Application State ───────────────────────────────────────────────
let currentState = null;
let autoRefreshTimer = null;
let isAutoRefreshActive = true;
const REFRESH_INTERVAL_MS = 3000;

// ── Lifecycle Initialization ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    addActivityLog('System initialized — Connecting to 5G Slice Orchestrator...', 'system');
    await fetchState();
    addActivityLog('Orchestrator online — 100 Mbps Carrier divided into 3 logical slices (Emergency, Smart IoT, Video)', 'info');
    startAutoRefresh();
}

// ── State Fetching & Rendering ───────────────────────────────────────
async function fetchState() {
    try {
        const response = await fetch('/api/state');
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        const data = await response.json();

        if (data.success && data.state) {
            currentState = data.state;
            renderDashboard(data.state, data.before, data.after);
            setConnectionStatus(true);
        } else {
            setConnectionStatus(false);
        }
    } catch (err) {
        console.error('Failed to fetch simulation state:', err);
        setConnectionStatus(false);
    }
}

function setConnectionStatus(online) {
    const pulse = document.getElementById('global-pulse');
    const text = document.getElementById('conn-status-text');
    if (pulse && text) {
        if (online) {
            pulse.className = 'pulse-dot';
            text.textContent = 'Connected: 100 Mbps Carrier';
        } else {
            pulse.className = 'pulse-dot error';
            text.textContent = 'Connection Interrupted';
        }
    }
}

// ── Auto-Refresh Management ─────────────────────────────────────────
function startAutoRefresh() {
    if (autoRefreshTimer) clearInterval(autoRefreshTimer);
    autoRefreshTimer = setInterval(() => {
        if (isAutoRefreshActive) {
            fetchState();
        }
    }, REFRESH_INTERVAL_MS);
}

function toggleAutoRefresh() {
    isAutoRefreshActive = !isAutoRefreshActive;
    const btnText = document.getElementById('refresh-state-text');
    const btnIcon = document.getElementById('refresh-icon');

    if (isAutoRefreshActive) {
        if (btnText) btnText.textContent = 'ON (3s)';
        if (btnIcon) btnIcon.textContent = '⏱️';
        showToast('info', 'Auto-Refresh Active', 'Dashboard polling active every 3 seconds.');
    } else {
        if (btnText) btnText.textContent = 'PAUSED';
        if (btnIcon) btnIcon.textContent = '⏸️';
        showToast('warning', 'Auto-Refresh Paused', 'Real-time background polling paused.');
    }
}

// ── Master Render Function ──────────────────────────────────────────
function renderDashboard(state, before, after) {
    const slices = state.slices;

    // 1. Header Sync Time
    const lastSyncEl = document.getElementById('lastSyncTime');
    if (lastSyncEl) lastSyncEl.textContent = state.last_updated || new Date().toLocaleTimeString();

    // 2. KPI Summary Cards
    setElText('kpi-val-cap', `${state.total_bandwidth || 100} Mbps`);
    setElText('kpi-val-alloc', `${state.allocated_bandwidth || 100} Mbps`);
    setElText('kpi-val-avail', `${state.available_bandwidth || 0} Mbps`);
    setElText('kpi-val-demand', `${state.total_demand || 100} Mbps`);
    setElText('kpi-val-unmet', `${state.unmet_demand || 0} Mbps`);
    setElText('kpi-val-util', `${state.utilization || 72}%`);

    const unmetCard = document.getElementById('kpi-unmet');
    if (unmetCard) {
        if (state.unmet_demand > 0) {
            unmetCard.style.borderColor = 'rgba(239, 68, 68, 0.6)';
            unmetCard.style.boxShadow = '0 0 15px rgba(239, 68, 68, 0.25)';
        } else {
            unmetCard.style.borderColor = '';
            unmetCard.style.boxShadow = '';
        }
    }

    // 3. 100 Mbps Live Allocation Bar
    updateAllocationBar(slices.emergency.bandwidth, slices.iot.bandwidth, slices.video.bandwidth);

    // 4. Interactive 5G Network Topology
    updateTopologyView(state);

    // 5. Individual Slice Cards
    updateSliceCard('em', slices.emergency);
    updateSliceCard('iot', slices.iot);
    updateSliceCard('vid', slices.video);

    // 6. Active Alerts Panel
    renderAlerts(state.alerts || []);
}

// ── Allocation Bar Rendering ────────────────────────────────────────
function updateAllocationBar(emBw, iotBw, vidBw) {
    const segEm = document.getElementById('alloc-seg-em');
    const segIot = document.getElementById('alloc-seg-iot');
    const segVid = document.getElementById('alloc-seg-vid');

    const txtEm = document.getElementById('alloc-seg-em-text');
    const txtIot = document.getElementById('alloc-seg-iot-text');
    const txtVid = document.getElementById('alloc-seg-vid-text');

    if (segEm) segEm.style.width = `${emBw}%`;
    if (segIot) segIot.style.width = `${iotBw}%`;
    if (segVid) segVid.style.width = `${vidBw}%`;

    if (txtEm) txtEm.textContent = `Emergency: ${emBw} Mbps (${emBw}%)`;
    if (txtIot) txtIot.textContent = `Smart IoT: ${iotBw} Mbps (${iotBw}%)`;
    if (txtVid) txtVid.textContent = `Video: ${vidBw} Mbps (${vidBw}%)`;

    setElText('leg-em-val', `${emBw} Mbps`);
    setElText('leg-iot-val', `${iotBw} Mbps`);
    setElText('leg-vid-val', `${vidBw} Mbps`);
}

// ── Interactive 5G Topology Rendering (Feature E) ───────────────────
function updateTopologyView(state) {
    const slices = state.slices;

    // Topology overall badge
    const topoBadge = document.getElementById('topo-state-badge');
    if (topoBadge) {
        if (state.network_status === 'CONGESTED') {
            topoBadge.className = 'badge status-congested';
            topoBadge.textContent = 'CARRIER: CONGESTED';
        } else if (state.active_scenario === 'degradation') {
            topoBadge.className = 'badge status-degraded';
            topoBadge.textContent = 'LINK IMPAIRMENT DETECTED';
        } else {
            topoBadge.className = 'badge status-active';
            topoBadge.textContent = 'CARRIER: NORMAL ONLINE';
        }
    }

    // Emergency Lane
    setElText('topo-em-bw', `${slices.emergency.bandwidth} Mbps`);
    setQosBadge('topo-em-qos', slices.emergency.qos_status);
    updateLaneClass('topo-lane-em', slices.emergency.status);

    // Smart IoT Lane
    setElText('topo-iot-bw', `${slices.iot.bandwidth} Mbps`);
    setQosBadge('topo-iot-qos', slices.iot.qos_status);
    updateLaneClass('topo-lane-iot', slices.iot.status);

    // Video Lane
    setElText('topo-vid-bw', `${slices.video.bandwidth} Mbps`);
    setQosBadge('topo-vid-qos', slices.video.qos_status);
    updateLaneClass('topo-lane-vid', slices.video.status);
}

function updateLaneClass(laneId, status) {
    const el = document.getElementById(laneId);
    if (!el) return;
    el.classList.remove('status-congested', 'status-degraded');
    if (status === 'CONGESTED') el.classList.add('status-congested');
    if (status === 'DEGRADED') el.classList.add('status-degraded');
}

// ── Slice Card Rendering ────────────────────────────────────────────
function updateSliceCard(prefix, slice) {
    // Animated bandwidth value
    const bwValEl = document.getElementById(`${prefix}-bw-val`);
    if (bwValEl) {
        const currentBw = parseInt(bwValEl.textContent, 10);
        if (currentBw !== slice.bandwidth) {
            bwValEl.textContent = slice.bandwidth;
            bwValEl.classList.remove('bw-updated');
            void bwValEl.offsetWidth; // Force CSS reflow
            bwValEl.classList.add('bw-updated');
        }
    }

    // Badges
    const statusBadge = document.getElementById(`${prefix}-status-badge`);
    if (statusBadge) {
        statusBadge.className = `badge status-${slice.status.toLowerCase()}`;
        statusBadge.textContent = slice.status;
    }

    const qosBadge = document.getElementById(`${prefix}-qos-badge`);
    if (qosBadge) {
        setQosBadge(`${prefix}-qos-badge`, slice.qos_status);
    }

    const trafficBadge = document.getElementById(`${prefix}-traffic-badge`);
    if (trafficBadge) {
        trafficBadge.textContent = `TRAFFIC: ${slice.traffic}`;
    }

    // Meter Fill
    setElText(`${prefix}-demand-text`, `${slice.demand} Mbps`);
    const fillEl = document.getElementById(`${prefix}-meter-fill`);
    if (fillEl) {
        const fillPct = Math.min(100, Math.round((slice.bandwidth / 100) * 100));
        fillEl.style.width = `${fillPct}%`;
    }

    // QoS Numerical Metrics
    setElText(`${prefix}-lat-val`, `${slice.latency} ms`);
    setElText(`${prefix}-jit-val`, `${slice.jitter} ms`);
    setElText(`${prefix}-loss-val`, `${slice.packet_loss}%`);
    setElText(`${prefix}-unmet-val`, `${slice.unmet_demand} Mbps`);
}

function setQosBadge(elemId, status) {
    const el = document.getElementById(elemId);
    if (!el) return;
    el.className = `badge qos-${status.toLowerCase()}`;
    el.textContent = `QoS: ${status}`;
}

// ── Active Alerts Rendering (Feature H) ─────────────────────────────
function renderAlerts(alerts) {
    const container = document.getElementById('alertsContainer');
    const badge = document.getElementById('alert-count-badge');
    if (!container) return;

    if (badge) badge.textContent = `${alerts.length} Active`;

    if (!alerts || alerts.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: var(--text-muted); padding: 2rem 1rem;">
                <span style="font-size: 2rem;">✅</span>
                <p style="margin-top: 0.5rem; font-size: 0.85rem;">All slices operating within nominal parameters. No active faults.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = alerts.map(a => `
        <div class="alert-item severity-${a.severity}">
            <div class="alert-item-top">
                <span class="badge ${a.severity === 'CRITICAL' ? 'priority-high' : (a.severity === 'WARNING' ? 'priority-medium' : 'priority-normal')}">${a.severity}</span>
                <span class="alert-time">${a.timestamp}</span>
            </div>
            <div class="alert-title">${a.title || a.message}</div>
            <div class="alert-msg"><strong>Slice:</strong> ${a.slice} — ${a.message}</div>
            ${a.cause ? `<div class="alert-msg" style="font-size: 0.75rem; color: #94a3b8;"><strong>Root Cause:</strong> ${a.cause}</div>` : ''}
            ${a.recommendation ? `<div class="alert-rec">💡 <strong>Corrective Action:</strong> ${a.recommendation}</div>` : ''}
        </div>
    `).join('');
}

// ── Scenario Execution (Feature G & D) ──────────────────────────────
async function runScenario(scenarioKey) {
    highlightScenarioButton(scenarioKey);
    addActivityLog(`Triggered scenario '${scenarioKey}'...`, 'command');

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario: scenarioKey })
        });

        const data = await response.json();
        if (!response.ok || !data.success) {
            showToast('error', 'Simulation Failed', data.error || 'Backend rejected scenario');
            return;
        }

        currentState = data.state;
        renderDashboard(data.state, data.before, data.after);

        // Toast feedback
        showToastForScenario(scenarioKey, data);

        // Activity log changes
        if (data.changes && data.changes.length > 0) {
            data.changes.forEach(ch => {
                const diffStr = ch.diff > 0 ? `+${ch.diff} Mbps` : `${ch.diff} Mbps`;
                addActivityLog(`Dynamic re-allocation: ${ch.slice} changed from ${ch.from} Mbps → ${ch.to} Mbps (${diffStr})`, 'alloc');
            });
        } else {
            addActivityLog(`Scenario '${data.label}' executed — allocation unchanged.`, 'info');
        }

        if (data.unmet_demand > 0) {
            addActivityLog(`⚠️ Capacity constrained: ${data.unmet_demand} Mbps unmet demand detected.`, 'warning');
        }

    } catch (err) {
        console.error('Error executing scenario:', err);
        showToast('error', 'Simulation Error', 'Failed to communicate with simulation engine');
    }
}

async function resetSimulation() {
    addActivityLog('System reset initiated by operator...', 'command');
    try {
        const response = await fetch('/api/reset', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            currentState = data.state;
            renderDashboard(data.state, data.before, data.after);
            showToast('info', '🔁 System Reset Complete', 'All 3 slices restored to baseline: Emergency 20, Smart IoT 30, Video 50 Mbps.');
            addActivityLog('System reset: Baseline state restored (20 / 30 / 50 Mbps)', 'system');
            highlightScenarioButton('normal');
        }
    } catch (err) {
        console.error('Reset failed:', err);
        showToast('error', 'Reset Error', 'Could not reset simulation state');
    }
}

function highlightScenarioButton(key) {
    document.querySelectorAll('.scen-btn').forEach(btn => btn.classList.remove('active'));
    const target = document.getElementById(`btn-scen-${key}`);
    if (target) target.classList.add('active');
}

function showToastForScenario(key, data) {
    const titles = {
        normal: '📶 Normal Traffic Profile',
        emergency: '🚨 Emergency Surge — Priority Reallocated',
        iot: '🚦 Smart IoT Telemetry Spike',
        video: '🎥 Video Streaming Surge',
        congestion: '⚠️ Carrier Congestion Overload',
        degradation: '🔧 Simulated RF Link Degradation',
        recover: '✅ Network Recovered & Re-balanced',
    };

    const types = {
        normal: 'info',
        emergency: 'critical',
        iot: 'warning',
        video: 'info',
        congestion: 'critical',
        degradation: 'warning',
        recover: 'info',
    };

    const toastType = types[key] || 'info';
    const title = titles[key] || `Scenario: ${key}`;
    const desc = `Total requested: ${data.total_demand || 100} Mbps · Carrier limit: 100 Mbps · Unmet: ${data.unmet_demand || 0} Mbps`;

    showToast(toastType, title, desc);
}

// ── Custom Demand Sliders (Feature D & B) ───────────────────────────
function toggleCustomDrawer() {
    const drawer = document.getElementById('customDemandDrawer');
    if (drawer) {
        drawer.style.display = (drawer.style.display === 'none' || !drawer.style.display) ? 'block' : 'none';
    }
}

function updateCustomSliders() {
    const emVal = parseInt(document.getElementById('slider-em').value, 10);
    const iotVal = parseInt(document.getElementById('slider-iot').value, 10);
    const vidVal = parseInt(document.getElementById('slider-vid').value, 10);

    setElText('custom-em-val', `${emVal} Mbps`);
    setElText('custom-iot-val', `${iotVal} Mbps`);
    setElText('custom-vid-val', `${vidVal} Mbps`);

    const total = emVal + iotVal + vidVal;
    setElText('custom-total-demand', `${total} Mbps`);
}

async function applyCustomDemand() {
    const em = parseInt(document.getElementById('slider-em').value, 10);
    const iot = parseInt(document.getElementById('slider-iot').value, 10);
    const vid = parseInt(document.getElementById('slider-vid').value, 10);

    addActivityLog(`Submitting custom demand: Emergency ${em} Mbps, IoT ${iot} Mbps, Video ${vid} Mbps`, 'command');

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scenario: 'custom',
                demands: { emergency: em, iot: iot, video: vid }
            })
        });

        const data = await response.json();
        if (data.success) {
            currentState = data.state;
            renderDashboard(data.state, data.before, data.after);
            showToast('info', 'Custom Demand Applied', `Dynamic allocation computed for ${em + iot + vid} Mbps total demand.`);
            addActivityLog(`Custom dynamic allocation computed successfully.`, 'alloc');
        } else {
            showToast('error', 'Custom Allocation Error', data.error);
        }
    } catch (err) {
        showToast('error', 'Network Error', 'Failed to submit custom demand');
    }
}

// ── QoS Thresholds Modal (Feature C) ────────────────────────────────
function toggleThresholdsModal() {
    const modal = document.getElementById('thresholdsModal');
    if (modal) {
        modal.style.display = (modal.style.display === 'none' || !modal.style.display) ? 'flex' : 'none';
    }
}

async function saveThresholds() {
    const latWarn = parseFloat(document.getElementById('th-lat-warn').value);
    const latFail = parseFloat(document.getElementById('th-lat-fail').value);
    const lossWarn = parseFloat(document.getElementById('th-loss-warn').value);
    const lossFail = parseFloat(document.getElementById('th-loss-fail').value);

    try {
        const res = await fetch('/api/thresholds', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latency_warning: latWarn,
                latency_fail: latFail,
                packet_loss_warning: lossWarn,
                packet_loss_fail: lossFail,
            })
        });
        const data = await res.json();
        if (data.success) {
            showToast('info', 'QoS Thresholds Updated', 'Slice QoS statuses re-evaluated against new thresholds.');
            addActivityLog(`QoS thresholds updated: Latency warn ${latWarn}ms, fail ${latFail}ms`, 'system');
            toggleThresholdsModal();
            fetchState();
        }
    } catch (err) {
        showToast('error', 'Error', 'Failed to update QoS thresholds');
    }
}

function resetDefaultThresholds() {
    document.getElementById('th-lat-warn').value = 40;
    document.getElementById('th-lat-fail').value = 80;
    document.getElementById('th-loss-warn').value = 1.0;
    document.getElementById('th-loss-fail').value = 4.0;

    document.getElementById('th-lat-warn-val').textContent = '40 ms';
    document.getElementById('th-lat-fail-val').textContent = '80 ms';
    document.getElementById('th-loss-warn-val').textContent = '1.0 %';
    document.getElementById('th-loss-fail-val').textContent = '4.0 %';
}

// ── Activity Log (Audit Trail) ──────────────────────────────────────
function addActivityLog(message, type = 'info') {
    const container = document.getElementById('activityLogContainer');
    if (!container) return;

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    const row = document.createElement('div');
    row.className = 'log-item';

    const icons = {
        command: '⚡',
        alloc: '⚖️',
        warning: '⚠️',
        system: '⚙️',
        info: 'ℹ️'
    };
    const icon = icons[type] || 'ℹ️';

    row.innerHTML = `
        <span class="log-time">[${time}]</span>
        <span class="log-msg">${icon} ${message}</span>
    `;

    container.insertBefore(row, container.firstChild);

    // Limit log memory to last 50 items
    while (container.children.length > 50) {
        container.removeChild(container.lastChild);
    }
}

function clearActivityLog() {
    const container = document.getElementById('activityLogContainer');
    if (container) {
        container.innerHTML = '';
        addActivityLog('Activity log cleared by operator.', 'system');
    }
}

// ── Toast Notifications ─────────────────────────────────────────────
function showToast(type, title, message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast`;

    const borderColors = {
        critical: 'var(--danger)',
        warning: 'var(--warning)',
        info: 'var(--cyan-5g)',
        error: 'var(--danger)'
    };
    toast.style.borderLeft = `4px solid ${borderColors[type] || 'var(--cyan-5g)'}`;

    toast.innerHTML = `
        <div class="toast-header">
            <span>${title}</span>
            <span style="font-size: 0.72rem; color: var(--text-dim);">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="toast-body">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 350);
    }, 4500);
}

// ── Helper Utilities ────────────────────────────────────────────────
function setElText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}
