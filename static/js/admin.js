/**
 * admin.js - Administrator Algorithmic Suite Controller
 * Exclusive Owner: Developer 2 (Anshu Kala)
 */

async function triggerBipartiteMatch() {
    const btn = document.getElementById('runBipartiteBtn');
    const resultsBox = document.getElementById('bipartiteResults');
    const list = document.getElementById('bipartiteList');
    const countDisplay = document.getElementById('bipartiteCount');

    btn.disabled = true;
    btn.innerText = 'Computing Max Flow (Ford-Fulkerson)...';

    try {
        const res = await apiFetch('/admin/api/bipartite-match', { method: 'POST' });
        if (res.status === 'ok') {
            const pairs = res.data.pairs;
            countDisplay.innerText = res.data.max_matches;
            resultsBox.style.display = 'block';

            if (pairs.length === 0) {
                list.innerHTML = `
                    <div class="empty-state text-muted" style="padding: 1rem; text-align: center;">
                        No viable bipartite flow pairings found above threshold.
                    </div>
                `;
            } else {
                list.innerHTML = pairs.map((p, i) => `
                    <div class="pair-card" style="display: flex; align-items: center; justify-content: space-between; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; gap: 0.5rem;">
                        <div style="flex: 1;">
                            <span class="item-badge badge-lost" style="font-size: 0.7rem;">LOST #${p.lost_id}</span>
                            <div style="font-weight: 600; font-size: 0.9rem; margin-top: 0.2rem;">${escapeHtml(p.lost_title)}</div>
                            <small class="text-muted">${escapeHtml(p.category)}</small>
                        </div>

                        <div style="text-align: center; padding: 0 0.5rem;">
                            <span class="confidence-badge" style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                                ${Math.round(p.score * 100)}% Flow
                            </span>
                            <div style="color: #3b82f6; font-size: 1.1rem; line-height: 1;">➔</div>
                        </div>

                        <div style="flex: 1; text-align: right;">
                            <span class="item-badge badge-found" style="font-size: 0.7rem;">FOUND #${p.found_id}</span>
                            <div style="font-weight: 600; font-size: 0.9rem; margin-top: 0.2rem;">${escapeHtml(p.found_title)}</div>
                            <small class="text-success">Verified Match</small>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (err) {
        console.error("Bipartite matching error:", err);
        alert("Bipartite match failed. Check connection or console.");
    } finally {
        btn.disabled = false;
        btn.innerText = 'Execute Ford-Fulkerson Flow';
    }
}

async function triggerHandoverScheduling() {
    const btn = document.getElementById('runScheduleBtn');
    const resultsBox = document.getElementById('scheduleResults');
    const list = document.getElementById('scheduleList');
    const totalPriority = document.getElementById('scheduleTotalPriority');
    const chromaticNum = document.getElementById('scheduleChromaticNum');

    btn.disabled = true;
    btn.innerText = 'Solving Greedy Sequencing & Graph Colouring...';

    try {
        const res = await apiFetch('/admin/api/schedule-handovers', { method: 'POST' });
        if (res.status === 'ok') {
            const data = res.data;
            totalPriority.innerText = data.total_priority_saved;
            chromaticNum.innerText = data.chromatic_number;
            resultsBox.style.display = 'block';

            const scheduled = data.scheduled_claims;
            const assignments = data.slot_assignments || {};

            if (scheduled.length === 0) {
                list.innerHTML = `<div class="empty-state text-muted" style="padding: 1rem; text-align: center;">No claims require scheduling.</div>`;
            } else {
                list.innerHTML = `
                    <table class="benchmark-table" style="font-size: 0.85rem;">
                        <thead>
                            <tr>
                                <th>Assigned Slot</th>
                                <th>Claim Item</th>
                                <th>Deadline Urgency</th>
                                <th>Priority Value</th>
                                <th>Desk Allocation (Graph Colouring)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${scheduled.map(c => {
                                const deskInfo = assignments[`match_${c.claim_id}`] || { desk_number: 1, desk_label: "Desk #1 (Station A)" };
                                const deskBg = deskInfo.desk_number === 1 ? '#dbeafe' : (deskInfo.desk_number === 2 ? '#dcfce7' : '#fef3c7');
                                const deskColor = deskInfo.desk_number === 1 ? '#1d4ed8' : (deskInfo.desk_number === 2 ? '#15803d' : '#b45309');
                                return `
                                    <tr>
                                        <td><strong>${escapeHtml(c.slot)}</strong></td>
                                        <td>${escapeHtml(c.item_title)} (#${c.claim_id})</td>
                                        <td><span class="text-muted">${c.deadline}h</span></td>
                                        <td><span class="badge-count" style="background: #3b82f6;">+${c.priority}</span></td>
                                        <td>
                                            <span style="background: ${deskBg}; color: ${deskColor}; font-weight: 600; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">
                                                ${escapeHtml(deskInfo.desk_label)}
                                            </span>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                `;
            }
        }
    } catch (err) {
        console.error("Handover scheduling error:", err);
        alert("Scheduling failed. Check connection or console.");
    } finally {
        btn.disabled = false;
        btn.innerText = 'Generate Timetable & Desks';
    }
}

async function triggerVaultPacking() {
    const btn = document.getElementById('runVaultBtn');
    const capacityInput = document.getElementById('bagCapacity');
    const capacity = parseInt(capacityInput.value, 10) || 5;
    const resultsBox = document.getElementById('vaultResults');
    const list = document.getElementById('vaultList');
    const weightDisplay = document.getElementById('vaultWeightPacked');
    const capLimitDisplay = document.getElementById('vaultCapLimit');
    const maxValueDisplay = document.getElementById('vaultMaxValue');

    btn.disabled = true;
    btn.innerText = 'Computing 0/1 Knapsack DP...';

    try {
        const res = await apiFetch('/admin/api/vault-pack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ capacity })
        });

        if (res.status === 'ok') {
            const data = res.data;
            weightDisplay.innerText = data.total_weight;
            capLimitDisplay.innerText = data.capacity;
            maxValueDisplay.innerText = data.max_value;
            resultsBox.style.display = 'block';

            const packed = data.packed_items || [];
            if (packed.length === 0) {
                list.innerHTML = `<div class="empty-state text-muted" style="padding: 1rem; text-align: center;">No items fit inside the specified bag weight capacity.</div>`;
            } else {
                list.innerHTML = packed.map(item => `
                    <div class="vault-item-row" style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.5rem 0.85rem; margin-bottom: 0.4rem; font-size: 0.85rem;">
                        <div>
                            <strong>${escapeHtml(item.title)}</strong> (#${item.item_id})
                            <div style="font-size: 0.75rem; color: #64748b;">Category: ${escapeHtml(item.category || 'General')}</div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <span class="meta-code">${item.item_weight} kg</span>
                            <span class="badge-count" style="background: #10b981;">Priority: +${item.priority_value}</span>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (err) {
        console.error("Vault packing error:", err);
        alert("Knapsack computation failed.");
    } finally {
        btn.disabled = false;
        btn.innerText = 'Pack Bag (0/1 DP)';
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

window.triggerBipartiteMatch = triggerBipartiteMatch;
window.triggerHandoverScheduling = triggerHandoverScheduling;
window.triggerVaultPacking = triggerVaultPacking;
