/**
 * api.js - Universal Fetch Wrapper & DAA Telemetry Controller
 * Exclusive Owner: Developer 2 (Anshu Kala)
 */

let telemetryCount = 0;

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
        addTelemetryRow(record);
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

    const now = new Date().toLocaleTimeString();
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><strong>#${telemetryCount}</strong></td>
        <td><strong>${escapeHtml(record.algorithm)}</strong></td>
        <td><span class="telemetry-badge-unit">${escapeHtml(record.unit || 'Unit I–IV')}</span></td>
        <td>${record.input_size ?? 'N/A'}</td>
        <td><code>${record.time_ms ?? '0.00'} ms</code></td>
        <td><span class="telemetry-complexity">${escapeHtml(record.complexity || 'O(1)')}</span></td>
        <td><small class="text-muted">${now}</small></td>
    `;

    if (tableBody) {
        tableBody.insertBefore(tr, tableBody.firstChild);
    }
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
