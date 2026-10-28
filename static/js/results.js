/**
 * 5G Network Slicing — Analytics & Results Controller (results.js)
 * Manages 5 interactive Chart.js visualizations, Before/After snapshots,
 * simulation history table, and CSV report export.
 */

'use strict';

// ── Chart Instances ─────────────────────────────────────────────────
let chartAlloc = null;
let chartDemandVsAlloc = null;
let chartUtilTimeline = null;
let chartLatency = null;
let chartBeforeAfter = null;

let currentHistory = [];

const CHART_THEME = {
    fontFamily: 'Outfit, sans-serif',
    textMuted: '#94a3b8',
    gridColor: 'rgba(255, 255, 255, 0.05)',
    emergencyColor: '#ef4444',
    iotColor: '#f59e0b',
    videoColor: '#3b82f6',
    cyanColor: '#38bdf8',
};

// ── Lifecycle Initialization ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadAllAnalytics();
});

// ── Load All Data ───────────────────────────────────────────────────
async function loadAllAnalytics() {
    try {
        const [stateRes, histRes] = await Promise.all([
            fetch('/api/state'),
            fetch('/api/history')
        ]);

        const stateData = await stateRes.json();
        const histData = await histRes.json();

        if (stateData.success) {
            renderKPIs(stateData.state, histData.count || 0);
            renderBeforeAfterSnapshot(stateData.before, stateData.after);

            // Render all 5 charts
            renderAllocDoughnut(stateData.state.slices);
            renderDemandVsAlloc(stateData.state.slices);
            renderUtilTimeline(stateData.util_timeline || []);
            renderLatencyComparison(stateData.state.slices);
            renderBeforeAfterChart(stateData.before, stateData.after);
        }

        if (histData.success) {
            currentHistory = histData.history || [];
            renderHistoryTable(currentHistory);
        }

        showToast('info', 'Analytics Refreshed', 'Visualizations updated from latest simulation state.');

    } catch (err) {
        console.error('Failed to load analytics data:', err);
        showToast('error', 'Error', 'Failed to refresh analytics from server');
    }
}

// ── Render Mini-KPIs ────────────────────────────────────────────────
function renderKPIs(state, historyCount) {
    const scenEl = document.getElementById('res-active-scenario');
    const demandEl = document.getElementById('res-total-demand');
    const unmetEl = document.getElementById('res-unmet-demand');
    const histEl = document.getElementById('res-history-count');

    if (scenEl) scenEl.textContent = state.active_scenario ? state.active_scenario.toUpperCase() : 'NORMAL';
    if (demandEl) demandEl.textContent = `${state.total_demand || 100} Mbps`;
    if (unmetEl) unmetEl.textContent = `${state.unmet_demand || 0} Mbps`;
    if (histEl) histEl.textContent = `${historyCount} Runs`;
}

// ── Render Before/After Snapshot Cards ──────────────────────────────
function renderBeforeAfterSnapshot(before, after) {
    if (before) {
        setElText('snap-before-em', `${before.emergency || 20} Mbps`);
        setElText('snap-before-iot', `${before.iot || 30} Mbps`);
        setElText('snap-before-vid', `${before.video || 50} Mbps`);
    }
    if (after) {
        setElText('snap-after-em', `${after.emergency || 20} Mbps`);
        setElText('snap-after-iot', `${after.iot || 30} Mbps`);
        setElText('snap-after-vid', `${after.video || 50} Mbps`);
    }
}

// ── Chart 1: Bandwidth Allocation Doughnut ──────────────────────────
function renderAllocDoughnut(slices) {
    const ctx = document.getElementById('chartAllocDoughnut');
    if (!ctx) return;

    if (chartAlloc) chartAlloc.destroy();

    const em = slices.emergency.bandwidth;
    const iot = slices.iot.bandwidth;
    const vid = slices.video.bandwidth;

    chartAlloc = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Emergency (URLLC)', 'Smart IoT (mMTC)', 'Video (eMBB)'],
            datasets: [{
                data: [em, iot, vid],
                backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6'],
                borderColor: '#081028',
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.label}: ${ctx.raw} Mbps (${ctx.raw}%)`
                    }
                }
            }
        }
    });
}

// ── Chart 2: Traffic Demand vs Allocated Bandwidth (Grouped Bar) ────
function renderDemandVsAlloc(slices) {
    const ctx = document.getElementById('chartDemandVsAlloc');
    if (!ctx) return;

    if (chartDemandVsAlloc) chartDemandVsAlloc.destroy();

    const labels = ['Emergency', 'Smart IoT', 'Video'];
    const demands = [slices.emergency.demand, slices.iot.demand, slices.video.demand];
    const allocations = [slices.emergency.bandwidth, slices.iot.bandwidth, slices.video.bandwidth];

    chartDemandVsAlloc = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Requested Demand (Mbps)',
                    data: demands,
                    backgroundColor: 'rgba(245, 158, 11, 0.75)',
                    borderColor: '#f59e0b',
                    borderWidth: 1.5,
                    borderRadius: 6,
                },
                {
                    label: 'Granted Allocation (Mbps)',
                    data: allocations,
                    backgroundColor: 'rgba(56, 189, 248, 0.85)',
                    borderColor: '#38bdf8',
                    borderWidth: 1.5,
                    borderRadius: 6,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: CHART_THEME.gridColor },
                    ticks: {
                        color: CHART_THEME.textMuted,
                        font: { family: CHART_THEME.fontFamily },
                        callback: v => `${v} Mbps`
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                }
            }
        }
    });
}

// ── Chart 3: Network Utilization Over Time (Timeline) ───────────────
function renderUtilTimeline(timeline) {
    const ctx = document.getElementById('chartUtilTimeline');
    if (!ctx) return;

    if (chartUtilTimeline) chartUtilTimeline.destroy();

    const labels = timeline.map((_, i) => `T-${timeline.length - 1 - i}`);

    chartUtilTimeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Carrier Utilization %',
                data: timeline,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.12)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.35,
                pointRadius: 3,
                pointBackgroundColor: '#38bdf8'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: CHART_THEME.gridColor },
                    ticks: {
                        color: CHART_THEME.textMuted,
                        font: { family: CHART_THEME.fontFamily },
                        callback: v => `${v}%`
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                }
            }
        }
    });
}

// ── Chart 4: Latency Comparison Between Slices ──────────────────────
function renderLatencyComparison(slices) {
    const ctx = document.getElementById('chartLatencyComparison');
    if (!ctx) return;

    if (chartLatency) chartLatency.destroy();

    const labels = ['Emergency (URLLC)', 'Smart IoT (mMTC)', 'Video (eMBB)'];
    const latencies = [slices.emergency.latency, slices.iot.latency, slices.video.latency];

    chartLatency = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Simulated Latency (ms)',
                data: latencies,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(59, 130, 246, 0.8)'
                ],
                borderColor: ['#ef4444', '#f59e0b', '#3b82f6'],
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: CHART_THEME.gridColor },
                    ticks: {
                        color: CHART_THEME.textMuted,
                        font: { family: CHART_THEME.fontFamily },
                        callback: v => `${v} ms`
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => ` Latency: ${ctx.raw} ms`
                    }
                }
            }
        }
    });
}

// ── Chart 5: Before vs After Allocation Comparison ──────────────────
function renderBeforeAfterChart(before, after) {
    const ctx = document.getElementById('chartBeforeAfter');
    if (!ctx) return;

    if (chartBeforeAfter) chartBeforeAfter.destroy();

    const b = before || { emergency: 20, iot: 30, video: 50 };
    const a = after || { emergency: 20, iot: 30, video: 50 };

    chartBeforeAfter = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Emergency', 'Smart IoT', 'Video'],
            datasets: [
                {
                    label: 'Before (Mbps)',
                    data: [b.emergency, b.iot, b.video],
                    backgroundColor: 'rgba(148, 163, 184, 0.5)',
                    borderColor: '#94a3b8',
                    borderWidth: 1.5,
                    borderRadius: 6
                },
                {
                    label: 'After (Mbps)',
                    data: [a.emergency, a.iot, a.video],
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10b981',
                    borderWidth: 1.5,
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: CHART_THEME.gridColor },
                    ticks: {
                        color: CHART_THEME.textMuted,
                        font: { family: CHART_THEME.fontFamily },
                        callback: v => `${v} Mbps`
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: CHART_THEME.textMuted, font: { family: CHART_THEME.fontFamily } }
                }
            }
        }
    });
}

// ── Simulation History Table Rendering (Feature F) ──────────────────
function renderHistoryTable(history) {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;

    if (!history || history.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; color: var(--text-dim); padding: 2rem;">
                    No simulation records logged yet. Run a scenario from the Dashboard to record history.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = history.map(entry => `
        <tr>
            <td class="mono" style="color: var(--text-dim);">${entry.timestamp}</td>
            <td><strong>${entry.scenario}</strong></td>
            <td class="mono" style="color: #fca5a5;">${entry.emergency_bw} Mbps</td>
            <td class="mono" style="color: #fcd34d;">${entry.iot_bw} Mbps</td>
            <td class="mono" style="color: #93c5fd;">${entry.video_bw} Mbps</td>
            <td class="mono">${entry.total_demand || (entry.emergency_bw + entry.iot_bw + entry.video_bw)} Mbps</td>
            <td class="mono" style="${entry.unmet_demand > 0 ? 'color: var(--danger); font-weight:700;' : ''}">
                ${entry.unmet_demand || 0} Mbps
            </td>
            <td class="mono">${entry.utilization}%</td>
            <td>
                <span class="badge ${entry.qos_emergency === 'FAIL' || entry.qos_video === 'FAIL' ? 'qos-fail' : (entry.qos_emergency === 'WARNING' || entry.qos_video === 'WARNING' ? 'qos-warning' : 'qos-pass')}">
                    EM: ${entry.qos_emergency || 'PASS'} · VID: ${entry.qos_video || 'PASS'}
                </span>
            </td>
        </tr>
    `).join('');
}

// ── CSV Export Functionality (Feature F) ─────────────────────────────
function exportHistoryCSV() {
    if (!currentHistory || currentHistory.length === 0) {
        showToast('warning', 'Export Warning', 'No simulation history records available to export.');
        return;
    }

    const headers = [
        'Timestamp',
        'Scenario',
        'Emergency_Mbps',
        'Smart_IoT_Mbps',
        'Video_Mbps',
        'Total_Demand_Mbps',
        'Unmet_Demand_Mbps',
        'Utilization_Percent',
        'Emergency_QoS',
        'IoT_QoS',
        'Video_QoS',
        'Emergency_Latency_ms',
        'IoT_Latency_ms',
        'Video_Latency_ms'
    ];

    const rows = currentHistory.map(h => [
        `"${h.timestamp}"`,
        `"${h.scenario}"`,
        h.emergency_bw,
        h.iot_bw,
        h.video_bw,
        h.total_demand || (h.emergency_bw + h.iot_bw + h.video_bw),
        h.unmet_demand || 0,
        h.utilization || 72,
        `"${h.qos_emergency || 'PASS'}"`,
        `"${h.qos_iot || 'PASS'}"`,
        `"${h.qos_video || 'PASS'}"`,
        h.emergency_lat || 4.5,
        h.iot_lat || 18.0,
        h.video_lat || 28.0
    ]);

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `5g_network_slicing_history_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('info', 'CSV Download Initiated', `Exported ${currentHistory.length} simulation records to CSV.`);
}

// ── Clear History ───────────────────────────────────────────────────
async function clearHistoryRecords() {
    try {
        const res = await fetch('/api/history/clear', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            currentHistory = [];
            renderHistoryTable([]);
            const histEl = document.getElementById('res-history-count');
            if (histEl) histEl.textContent = '0 Runs';
            showToast('info', 'History Cleared', 'Simulation history records have been reset.');
        }
    } catch (err) {
        showToast('error', 'Error', 'Failed to clear simulation history');
    }
}

// ── Toast Manager ───────────────────────────────────────────────────
function showToast(type, title, message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.borderLeft = `4px solid ${type === 'error' ? 'var(--danger)' : (type === 'warning' ? 'var(--warning)' : 'var(--cyan-5g)')}`;

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
    }, 4000);
}

function setElText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}
