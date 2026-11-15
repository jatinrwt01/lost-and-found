/**
 * canvas_map.js - HTML5 Canvas Campus Graph Interactive Renderer
 * Exclusive Owner: Developer 2 (Anshu Kala)
 */

const CAMPUS_NODES = [
    { id: 1, name: "Main Gate", x: 100, y: 400 },
    { id: 2, name: "Central Library", x: 250, y: 220 },
    { id: 3, name: "Academic Block A", x: 420, y: 180 },
    { id: 4, name: "Canteen", x: 380, y: 360 },
    { id: 5, name: "Hostel Complex", x: 650, y: 380 },
    { id: 6, name: "Sports Ground", x: 700, y: 150 },
    { id: 7, name: "Admin Vault", x: 500, y: 260 },
];

const CAMPUS_EDGES = [
    { src: 1, dst: 2, weight: 150 },
    { src: 1, dst: 4, weight: 200 },
    { src: 2, dst: 3, weight: 110 },
    { src: 2, dst: 4, weight: 140 },
    { src: 3, dst: 6, weight: 220 },
    { src: 3, dst: 7, weight: 130 },
    { src: 4, dst: 5, weight: 180 },
    { src: 4, dst: 7, weight: 95 },
    { src: 5, dst: 7, weight: 160 },
    { src: 6, dst: 7, weight: 190 },
];

let canvas, ctx;
let activeHighlight = null; // { type: 'path'|'mst'|'tsp', ... }
let hoveredNode = null;
let selectedSrc = 1;
let selectedDst = 5;
let animationOffset = 0;
let animationTimer = null;

document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('campusCanvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    // Add canvas click listener for interactive node selection
    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('mousemove', handleCanvasMouseMove);
    canvas.addEventListener('mouseleave', () => {
        hoveredNode = null;
        drawMap();
    });

    drawMap();
});

/**
 * Main Canvas Render Loop
 */
function drawMap() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Draw base edges
    CAMPUS_EDGES.forEach(edge => {
        const u = CAMPUS_NODES.find(n => n.id === edge.src);
        const v = CAMPUS_NODES.find(n => n.id === edge.dst);
        if (u && v) {
            drawLine(u.x, u.y, v.x, v.y, '#cbd5e1', 2);
            // Edge weight badge
            const midX = (u.x + v.x) / 2;
            const midY = (u.y + v.y) / 2;
            ctx.fillStyle = '#64748b';
            ctx.font = 'bold 11px monospace';
            ctx.fillText(`${edge.weight}m`, midX - 10, midY - 6);
        }
    });

    // 2. Draw active algorithmic overlays
    if (activeHighlight) {
        if (activeHighlight.type === 'path') {
            drawPathOverlay(activeHighlight.path);
        } else if (activeHighlight.type === 'mst') {
            drawMSTOverlay(activeHighlight.edges);
        } else if (activeHighlight.type === 'tsp') {
            drawTSPOverlay(activeHighlight.tour);
        }
    }

    // 3. Draw nodes (vertices)
    CAMPUS_NODES.forEach(node => {
        const isHovered = hoveredNode && hoveredNode.id === node.id;
        const isSrc = selectedSrc === node.id;
        const isDst = selectedDst === node.id;

        // Node Glow for Selection / Hover
        if (isSrc || isDst || isHovered) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, 22, 0, 2 * Math.PI);
            ctx.fillStyle = isSrc ? 'rgba(16, 185, 129, 0.3)' : (isDst ? 'rgba(239, 68, 68, 0.3)' : 'rgba(59, 130, 246, 0.25)');
            ctx.fill();
        }

        // Inner circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, 16, 0, 2 * Math.PI);
        if (isSrc) {
            ctx.fillStyle = '#10b981';
        } else if (isDst) {
            ctx.fillStyle = '#ef4444';
        } else {
            ctx.fillStyle = '#2563eb';
        }
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();

        // Node ID inside
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node.id, node.x, node.y);

        // Node Name label below
        ctx.fillStyle = '#1e293b';
        ctx.font = '600 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.name, node.x, node.y + 26);

        // Selection Tag
        if (isSrc) {
            drawTag(node.x, node.y - 24, "SRC", "#10b981");
        } else if (isDst) {
            drawTag(node.x, node.y - 24, "DST", "#ef4444");
        }
    });
}

function drawTag(x, y, text, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x - 16, y - 8, 32, 14);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 9px sans-serif";
    ctx.fillText(text, x, y);
}

function drawLine(x1, y1, x2, y2, color, width, dashed = false) {
    ctx.beginPath();
    if (dashed) {
        ctx.setLineDash([8, 6]);
        ctx.lineDashOffset = -animationOffset;
    } else {
        ctx.setLineDash([]);
    }
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawPathOverlay(nodeIds) {
    for (let i = 0; i < nodeIds.length - 1; i++) {
        const u = CAMPUS_NODES.find(n => n.id === nodeIds[i]);
        const v = CAMPUS_NODES.find(n => n.id === nodeIds[i + 1]);
        if (u && v) {
            drawLine(u.x, u.y, v.x, v.y, '#10b981', 6);
        }
    }
}

function drawMSTOverlay(edges) {
    edges.forEach(edge => {
        const u = CAMPUS_NODES.find(n => n.id === edge.src);
        const v = CAMPUS_NODES.find(n => n.id === edge.dst);
        if (u && v) {
            drawLine(u.x, u.y, v.x, v.y, '#059669', 5);
        }
    });
}

function drawTSPOverlay(tour) {
    for (let i = 0; i < tour.length - 1; i++) {
        const u = CAMPUS_NODES.find(n => n.id === tour[i]);
        const v = CAMPUS_NODES.find(n => n.id === tour[i + 1]);
        if (u && v) {
            drawLine(u.x, u.y, v.x, v.y, '#f59e0b', 5, true);
        }
    }
}

/**
 * Interactive Canvas Clicks: Clicking nodes selects Source & Destination
 */
function handleCanvasClick(e) {
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    const clicked = CAMPUS_NODES.find(n => {
        const dx = n.x - clickX;
        const dy = n.y - clickY;
        return Math.sqrt(dx * dx + dy * dy) <= 22;
    });

    if (clicked) {
        if (selectedSrc === clicked.id) {
            // Already source, do nothing
            return;
        } else if (selectedDst === clicked.id) {
            selectedDst = selectedSrc;
            selectedSrc = clicked.id;
        } else {
            // Toggle next target
            selectedDst = clicked.id;
        }

        const srcSelect = document.getElementById('mapSrcSelect');
        const dstSelect = document.getElementById('mapDstSelect');
        if (srcSelect) srcSelect.value = selectedSrc;
        if (dstSelect) dstSelect.value = selectedDst;

        runDijkstra();
    }
}

function handleCanvasMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const found = CAMPUS_NODES.find(n => {
        const dx = n.x - mouseX;
        const dy = n.y - mouseY;
        return Math.sqrt(dx * dx + dy * dy) <= 22;
    });

    if (found !== hoveredNode) {
        hoveredNode = found;
        canvas.style.cursor = found ? 'pointer' : 'default';
        drawMap();
    }
}

/**
 * Triggers Dijkstra Shortest Path calculation
 */
async function runDijkstra() {
    stopAnimation();
    selectedSrc = parseInt(document.getElementById('mapSrcSelect').value, 10);
    selectedDst = parseInt(document.getElementById('mapDstSelect').value, 10);
    const infoBar = document.getElementById('routeInfoBar');

    infoBar.innerHTML = '<em>Running Dijkstra shortest path calculation...</em>';

    try {
        const res = await apiFetch(`/campus/api/route?src=${selectedSrc}&dst=${selectedDst}`);
        if (res.status === 'ok') {
            const path = res.data.path;
            const dist = res.data.total_meters;
            activeHighlight = { type: 'path', path };
            drawMap();

            const pathNames = path.map(id => CAMPUS_NODES.find(n => n.id === id)?.name || id);
            infoBar.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <span><strong>Dijkstra Route (${path.length} hops):</strong> ${pathNames.join(' ➔ ')}</span>
                    <span class="badge-count" style="background: #10b981; font-size: 0.85rem; padding: 4px 10px;">Total Distance: ${dist} meters</span>
                </div>
            `;
        }
    } catch (err) {
        console.error("Dijkstra error:", err);
        infoBar.innerText = "Error executing Dijkstra routing.";
    }
}

/**
 * Triggers Kruskal MST computation
 */
async function runKruskalMST() {
    stopAnimation();
    const infoBar = document.getElementById('routeInfoBar');
    infoBar.innerHTML = '<em>Computing Kruskal Minimum Spanning Tree with DSU...</em>';

    try {
        const res = await apiFetch('/campus/api/network');
        if (res.status === 'ok') {
            const data = res.data;
            activeHighlight = { type: 'mst', edges: data.mst_edges };
            drawMap();
            infoBar.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <span><strong>Kruskal MST (${data.mst_edges.length} edges):</strong> Connects all campus drop-boxes with zero cycles.</span>
                    <span class="badge-count" style="background: #059669; font-size: 0.85rem; padding: 4px 10px;">Total Cable/Walk: ${data.total_mst_meters}m</span>
                </div>
            `;
        }
    } catch (err) {
        console.error("Kruskal error:", err);
    }
}

/**
 * Triggers TSP Tour computation with animated dashed traversal
 */
async function runTSPTour() {
    stopAnimation();
    const infoBar = document.getElementById('routeInfoBar');
    infoBar.innerHTML = '<em>Solving TSP Branch & Bound security collection loop...</em>';

    try {
        const res = await apiFetch('/campus/api/network');
        if (res.status === 'ok') {
            const data = res.data;
            activeHighlight = { type: 'tsp', tour: data.tsp_tour };
            startAnimation();
            const tourNames = data.tsp_tour.map(id => CAMPUS_NODES.find(n => n.id === id)?.name || id);
            infoBar.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <span><strong>Security Patrol TSP Tour:</strong> ${tourNames.join(' ➔ ')}</span>
                    <span class="badge-count" style="background: #f59e0b; font-size: 0.85rem; padding: 4px 10px;">Optimal Loop: ${data.total_tour_meters}m</span>
                </div>
            `;
        }
    } catch (err) {
        console.error("TSP error:", err);
    }
}

function startAnimation() {
    stopAnimation();
    animationTimer = setInterval(() => {
        animationOffset = (animationOffset + 1) % 24;
        drawMap();
    }, 50);
}

function stopAnimation() {
    if (animationTimer) {
        clearInterval(animationTimer);
        animationTimer = null;
    }
    animationOffset = 0;
}

function resetCanvas() {
    stopAnimation();
    activeHighlight = null;
    drawMap();
    document.getElementById('routeInfoBar').innerText = 'Map reset to default campus graph. Click any node or action to trace routes.';
}

window.runDijkstra = runDijkstra;
window.runKruskalMST = runKruskalMST;
window.runTSPTour = runTSPTour;
window.resetCanvas = resetCanvas;
