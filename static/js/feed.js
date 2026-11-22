/**
 * feed.js - Feed Search, Sorting Toggle & Filter Controller
 * Exclusive Owner: Developer 2 (Anshu Kala)
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchModeSelect = document.getElementById('searchModeSelect');
    const sortMethodSelect = document.getElementById('sortMethodSelect');
    const executeSearchBtn = document.getElementById('executeSearchBtn');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const filterPills = document.querySelectorAll('.filter-pills-row .pill');

    let activeFilter = 'all';

    // Search button click
    if (executeSearchBtn) {
        executeSearchBtn.addEventListener('click', () => triggerFeedSearch());
    }

    // Enter key triggers search
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                triggerFeedSearch();
            }
        });

        searchInput.addEventListener('input', () => {
            if (clearSearchBtn) {
                clearSearchBtn.style.display = searchInput.value ? 'block' : 'none';
            }
        });
    }

    // Clear search
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearSearchBtn.style.display = 'none';
            triggerFeedSearch();
        });
    }

    // Filter pills
    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            activeFilter = pill.dataset.filter;
            applyClientSideCategoryFilter(activeFilter);
        });
    });

    // Auto search on mode/sort switch
    if (sortMethodSelect) {
        sortMethodSelect.addEventListener('change', () => triggerFeedSearch());
    }
    if (searchModeSelect) {
        searchModeSelect.addEventListener('change', () => {
            if (searchInput.value.trim()) {
                triggerFeedSearch();
            }
        });
    }
});

/**
 * Executes algorithmic search and sorting via /api/items/search
 */
async function triggerFeedSearch() {
    const q = document.getElementById('searchInput')?.value.trim() || '';
    const mode = document.getElementById('searchModeSelect')?.value || 'kmp';
    const sort = document.getElementById('sortMethodSelect')?.value || 'merge';

    const badge = document.getElementById('activeAlgoBadge');
    if (badge) {
        const modeLabel = mode === 'binary' ? 'Binary Search' : 'KMP Match';
        const sortLabel = sort === 'quick' ? 'Quick Sort' : (sort === 'bitonic' ? 'Bitonic Sort' : 'Merge Sort');
        badge.innerText = `⚡ ${modeLabel} + ${sortLabel}`;
    }

    const url = `/api/items/search?q=${encodeURIComponent(q)}&mode=${encodeURIComponent(mode)}&sort=${encodeURIComponent(sort)}`;

    try {
        const res = await apiFetch(url);
        if (res.status === 'ok') {
            renderItems(res.data);
        }
    } catch (err) {
        console.error("Feed search failed:", err);
    }
}

/**
 * Renders item cards into itemsGrid
 */
function renderItems(items) {
    const grid = document.getElementById('itemsGrid');
    const noResults = document.getElementById('noResultsAlert');
    const countDisplay = document.getElementById('itemCountDisplay');

    if (!grid) return;

    if (countDisplay) {
        countDisplay.innerText = items.length;
    }

    if (items.length === 0) {
        grid.innerHTML = '';
        if (noResults) noResults.style.display = 'block';
        return;
    }

    if (noResults) noResults.style.display = 'none';

    grid.innerHTML = items.map(item => `
        <div class="item-card" data-id="${item.item_id}" data-type="${item.type}" data-category="${item.category}">
            <div class="item-card-header">
                <span class="item-badge badge-${item.type.toLowerCase()}">${item.type}</span>
                <span class="item-category">${escapeHtml(item.category)}</span>
                <span class="item-id">#${item.item_id}</span>
            </div>
            
            <h4 class="item-title">${escapeHtml(item.title)}</h4>
            <p class="item-description">${escapeHtml(item.description)}</p>

            <div class="item-meta">
                <div class="meta-row">
                    <span class="meta-label">📍 Location:</span>
                    <span class="meta-value">${escapeHtml(item.location_name || 'Campus Area')}</span>
                </div>
                ${item.serial_tag ? `
                <div class="meta-row">
                    <span class="meta-label">🏷️ Tag / S/N:</span>
                    <code class="meta-code">${escapeHtml(item.serial_tag)}</code>
                </div>` : ''}
                <div class="meta-row">
                    <span class="meta-label">⏱️ Deadline:</span>
                    <span class="meta-value">${item.deadline_hours}h (Priority: ${item.priority_value})</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">📅 Reported:</span>
                    <span class="meta-value text-muted">${item.created_at || 'Recent'}</span>
                </div>
            </div>

            <div class="item-card-footer">
                <button class="btn btn-outline btn-sm" onclick="openMatchModal(${item.item_id}, '${item.type}', '${escapeHtml(item.title)}')">
                    Match Candidates
                </button>
                <span class="status-pill status-${(item.status || 'open').toLowerCase()}">${item.status || 'OPEN'}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Filter visible cards by type or category
 */
function applyClientSideCategoryFilter(filter) {
    const cards = document.querySelectorAll('.items-grid .item-card');
    let visibleCount = 0;

    cards.forEach(card => {
        const type = card.dataset.type;
        const cat = card.dataset.category;

        if (filter === 'all' || type === filter || cat === filter) {
            card.style.display = 'flex';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    const countDisplay = document.getElementById('itemCountDisplay');
    if (countDisplay) countDisplay.innerText = visibleCount;
}

/**
 * Match Candidates Modal Controls
 */
async function openMatchModal(itemId, itemType, itemTitle) {
    const modal = document.getElementById('matchModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');

    if (!modal) return;
    title.innerText = `LCS & Distance Pairing for: "${itemTitle}" (#${itemId})`;
    body.innerHTML = `
        <div style="padding: 1.5rem; text-align: center;">
            <p><strong>Querying DAA Engine:</strong> Running Longest Common Subsequence ($O(m \\cdot n)$) and Floyd-Warshall ($O(V^3)$)...</p>
        </div>
    `;
    modal.style.display = 'flex';

    try {
        const res = await apiFetch(`/api/items/${itemId}/candidates`);
        if (res.status === 'ok') {
            const candidates = res.data.candidates || [];
            if (candidates.length === 0) {
                body.innerHTML = `
                    <div style="padding: 1.5rem; text-align: center; color: #64748b;">
                        <p>No active counter-matches found in the same category.</p>
                        <small>Opposite report category: ${itemType === 'LOST' ? 'FOUND' : 'LOST'}</small>
                    </div>
                `;
            } else {
                body.innerHTML = `
                    <div style="padding: 1rem 0; display: flex; flex-direction: column; gap: 0.75rem;">
                        <p style="font-size: 0.9rem; color: #475569;">
                            Found <strong>${candidates.length}</strong> potential counter-match${candidates.length === 1 ? '' : 'es'} ranked by composite confidence ($0.65 \\times \\text{LCS} + 0.35 \\times \\text{Proximity}$):
                        </p>
                        ${candidates.map(c => `
                            <div style="background: #f8fafc; padding: 1rem; border-radius: 6px; border: 1px solid #e2e8f0;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">
                                    <span><strong>#${c.item.item_id} — ${escapeHtml(c.item.title)}</strong></span>
                                    <span class="confidence-badge">${Math.round(c.confidence_score * 100)}% Match</span>
                                </div>
                                <p style="font-size: 0.85rem; color: #475569; margin-bottom: 0.5rem;">${escapeHtml(c.item.description)}</p>
                                <div style="font-size: 0.8rem; display: flex; gap: 1rem; color: #64748b;">
                                    <span>📍 Location: <strong>${escapeHtml(c.item.location_name || 'Campus')}</strong></span>
                                    <span>LCS Ratio: <code>${c.lcs_score}</code></span>
                                    <span>Distance: <code>${c.spatial_distance_meters}m</code></span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        } else {
            body.innerHTML = `<div style="padding: 1rem; color: #dc2626;">Failed to load candidate pairings: ${res.message || 'Error'}</div>`;
        }
    } catch (err) {
        console.error("Match candidates error:", err);
        body.innerHTML = `<div style="padding: 1rem; color: #dc2626;">Failed to communicate with DAA matching service.</div>`;
    }
}

function closeMatchModal() {
    const modal = document.getElementById('matchModal');
    if (modal) modal.style.display = 'none';
}

window.openMatchModal = openMatchModal;
window.closeMatchModal = closeMatchModal;
