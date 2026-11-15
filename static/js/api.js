/**
 * api.js - Universal Fetch Wrapper & DAA Telemetry Controller
 * Exclusive Owner: Developer 2 (Anshu Kala)
 */

let telemetryCount = 0;
const telemetryHistory = [];
let currentUnitFilter = 'all';

/**
 * Universal API Fetch wrapper that automatically parses and updates
 * the collapsible DAA Telemetry Drawer with execution metrics.
 */
async function apiFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();

        if (data && data.telemetry) {
            handleTelemetryUpdates(data.telemetry);
        }

        return data;
    } catch (error) {
        console.error(`[apiFetch Error] Request to ${url} failed:`, error);
        throw error;
    }
}

/**
 * Parses single or array telemetry objects and renders them into the drawer.
 */
function handleTelemetryUpdates(telemetry) {
    if (!telemetry) return;

    const list = Array.isArray(telemetry) ? telemetry : [telemetry];
    list.forEach(record => {
        if (!record || !record.algorithm) return;
        telemetryCount++;
        const enrichedRecord = {
            id: telemetryCount,
            ...record,
            timestamp: new Date().toLocaleTimeString()
        };
        telemetryHistory.unshift(enrichedRecord);
        addTelemetryRow(enrichedRecord);
    });

    const countBadge = document.getElementById('telemetryCount');
    if (countBadge) {
        countBadge.innerText = `${telemetryCount} op${telemetryCount === 1 ? '' : 's'}`;
    }
}

/**
 * Inserts a new telemetry record row into the top of the telemetry table.
 */
function addTelemetryRow(record) {
    const tableBody = document.getElementById('telemetryLogs');
    const emptyRow = document.getElementById('emptyTelemetryRow');
    if (emptyRow) {
        emptyRow.remove();
    }

    const latestBox = document.getElementById('telemetryLatest');
    if (latestBox) {
        latestBox.innerHTML = `<strong>Last:</strong> ${escapeHtml(record.algorithm)} (${record.time_ms} ms | ${escapeHtml(record.complexity)})`;
    }

    const tr = document.createElement('tr');
    tr.dataset.unit = record.unit || '';
    tr.className = 'telemetry-log-row';

    if (currentUnitFilter !== 'all' && !record.unit?.includes(currentUnitFilter)) {
        tr.style.display = 'none';
    }

    tr.innerHTML = `
        <td><strong>#${record.id}</strong></td>
        <td><strong>${escapeHtml(record.algorithm)}</strong></td>
        <td><span class="telemetry-badge-unit">${escapeHtml(record.unit || 'Unit I–IV')}</span></td>
        <td>${record.input_size ?? 'N/A'}</td>
        <td><code>${record.time_ms ?? '0.00'} ms</code></td>
        <td><span class="telemetry-complexity">${escapeHtml(record.complexity || 'O(1)')}</span></td>
        <td><small class="text-muted">${record.timestamp}</small></td>
    `;

    if (tableBody) {
        tableBody.insertBefore(tr, tableBody.firstChild);
    }
}

/**
 * Filters the displayed telemetry table by DAA syllabus unit.
 */
function filterTelemetryUnit(unit, btn) {
    currentUnitFilter = unit;
    const tabs = document.querySelectorAll('.telemetry-filter-tabs .t-tab');
    tabs.forEach(t => t.classList.remove('active'));
    if (btn) btn.classList.add('active');

    const rows = document.querySelectorAll('.telemetry-log-row');
    rows.forEach(row => {
        const rowUnit = row.dataset.unit;
        if (unit === 'all' || rowUnit.includes(unit)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Copies the entire telemetry history log to clipboard as formatted JSON.
 */
async function copyTelemetryJSON() {
    if (telemetryHistory.length === 0) {
        alert("No telemetry records logged yet.");
        return;
    }
    const jsonStr = JSON.stringify(telemetryHistory, null, 2);
    try {
        await navigator.clipboard.writeText(jsonStr);
        alert(`Copied ${telemetryHistory.length} telemetry execution records to clipboard!`);
    } catch (e) {
        console.error("Clipboard copy failed:", e);
        prompt("Copy telemetry JSON below:", jsonStr);
    }
}

/**
 * Clears the telemetry log table and resets the session counter.
 */
function clearTelemetryLog() {
    telemetryHistory.length = 0;
    telemetryCount = 0;
    const tableBody = document.getElementById('telemetryLogs');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr id="emptyTelemetryRow">
                <td colspan="7" class="text-center text-muted">
                    Telemetry log cleared. Run an algorithmic action to record new metrics.
                </td>
            </tr>
        `;
    }
    const countBadge = document.getElementById('telemetryCount');
    if (countBadge) countBadge.innerText = '0 calls';

    const latestBox = document.getElementById('telemetryLatest');
    if (latestBox) latestBox.innerHTML = '<em>No algorithmic operations recorded yet.</em>';
}

/**
 * Toggles the collapsed/expanded state of the DAA Telemetry Drawer.
 */
function toggleTelemetry() {
    const drawer = document.getElementById('telemetryDrawer');
    const toggleBtn = document.getElementById('drawerToggleBtn');
    if (!drawer) return;

    if (drawer.classList.contains('collapsed')) {
        drawer.classList.remove('collapsed');
        if (toggleBtn) toggleBtn.innerText = '▼ Collapse';
    } else {
        drawer.classList.add('collapsed');
        if (toggleBtn) toggleBtn.innerText = '▲ Expand';
    }
}

function escapeHtml(str) {
    if (typeof str !== 'string') return str;
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

window.apiFetch = apiFetch;
window.toggleTelemetry = toggleTelemetry;
window.handleTelemetryUpdates = handleTelemetryUpdates;
window.filterTelemetryUnit = filterTelemetryUnit;
window.copyTelemetryJSON = copyTelemetryJSON;
window.clearTelemetryLog = clearTelemetryLog;
