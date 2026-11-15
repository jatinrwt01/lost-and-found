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
    let debounceTimer = null;

    // Search button click
    if (executeSearchBtn) {
        executeSearchBtn.addEventListener('click', () => triggerFeedSearch());
    }

    // Debounced real-time search on input
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(debounceTimer);
                triggerFeedSearch();
            }
        });

        searchInput.addEventListener('input', () => {
            if (clearSearchBtn) {
                clearSearchBtn.style.display = searchInput.value ? 'block' : 'none';
            }
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                triggerFeedSearch();
            }, 300);
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
            triggerFeedSearch();
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
            const activePill = document.querySelector('.filter-pills-row .pill.active');
            if (activePill && activePill.dataset.filter !== 'all') {
                applyClientSideCategoryFilter(activePill.dataset.filter);
            }
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
    title.innerText = `LCS & Distance Pairing: "${itemTitle}" (#${itemId})`;
    body.innerHTML = `
        <div style="padding: 1.5rem 0; text-align: center;">
            <p><strong>Querying DAA Engine...</strong></p>
            <p class="text-muted" style="font-size: 0.85rem; margin-top: 0.25rem;">Computing Floyd-Warshall distance matrix ($O(V^3)$) and Longest Common Subsequence ($O(m \\cdot n)$)...</p>
        </div>
    `;
    modal.style.display = 'flex';

    try {
        const res = await apiFetch(`/api/items/candidates/${itemId}`);
        if (res.status === 'ok') {
            const candidates = res.data.candidates;
            if (candidates.length === 0) {
                body.innerHTML = `
                    <div class="empty-matches-placeholder">
                        <span class="icon">🔍</span>
                        <p>No counter-candidates found in the opposite category yet.</p>
                    </div>
                `;
                return;
            }

            body.innerHTML = `
                <div style="margin-bottom: 0.75rem; font-size: 0.88rem; color: #475569;">
                    Found <strong>${candidates.length}</strong> potential counter-match${candidates.length === 1 ? '' : 'es'} ranked by composite text & spatial score:
                </div>
                <div class="candidates-modal-list">
                    ${candidates.map((c, idx) => `
                        <div class="candidate-item-box" style="margin-bottom: 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.85rem; background: #ffffff;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <strong>#${idx + 1}: ${escapeHtml(c.item.title)} (#${c.item.item_id})</strong>
                                <span class="confidence-badge" style="background: ${c.confidence_score >= 0.7 ? '#dcfce7' : '#fef3c7'}; color: ${c.confidence_score >= 0.7 ? '#15803d' : '#b45309'}; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">
                                    ${Math.round(c.confidence_score * 100)}% Match
                                </span>
                            </div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;">${escapeHtml(c.item.description)}</p>
                            <div style="font-size: 0.78rem; display: flex; flex-wrap: wrap; gap: 1rem; color: #475569; background: #f8fafc; padding: 0.4rem 0.6rem; border-radius: 4px;">
                                <span>📍 <strong>Location:</strong> ${escapeHtml(c.item.location_name || 'Campus')}</span>
                                <span>🔤 <strong>LCS Ratio:</strong> <code>${c.lcs_score}</code></span>
                                <span>📏 <strong>Campus Dist:</strong> <code>${c.spatial_dist_meters}m</code></span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            body.innerHTML = `<p class="text-danger">Failed to retrieve candidate matches: ${res.message || 'Unknown error'}</p>`;
        }
    } catch (e) {
        console.error("Match candidate fetch error:", e);
        body.innerHTML = `<p class="text-danger">Network error fetching candidates. Check connection.</p>`;
    }
}

function closeMatchModal() {
    const modal = document.getElementById('matchModal');
    if (modal) modal.style.display = 'none';
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

window.openMatchModal = openMatchModal;
window.closeMatchModal = closeMatchModal;
