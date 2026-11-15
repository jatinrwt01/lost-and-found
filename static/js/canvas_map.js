/**
 * canvas_map.js - HTML5 Canvas Campus Graph Renderer
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
let activeHighlight = null; // { type: 'path'|'mst'|'tsp', data: ... }

document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('campusCanvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    drawMap();
});

/**
 * Base graph rendering routine
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
            // Draw edge weight
            const midX = (u.x + v.x) / 2;
            const midY = (u.y + v.y) / 2;
            ctx.fillStyle = '#64748b';
            ctx.font = '11px sans-serif';
            ctx.fillText(`${edge.weight}m`, midX - 10, midY - 5);
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
        // Outer glow/circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, 16, 0, 2 * Math.PI);
        ctx.fillStyle = '#2563eb';
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

        // Node Name label
        ctx.fillStyle = '#1e293b';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.name, node.x, node.y + 28);
    });
}

function drawLine(x1, y1, x2, y2, color, width, dashed = false) {
    ctx.beginPath();
    if (dashed) {
        ctx.setLineDash([6, 6]);
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
            drawLine(u.x, u.y, v.x, v.y, '#10b981', 5);
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
            drawLine(u.x, u.y, v.x, v.y, '#f59e0b', 4, true);
        }
    }
}

/**
 * Triggers Dijkstra Shortest Path calculation
 */
async function runDijkstra() {
    const src = document.getElementById('mapSrcSelect').value;
    const dst = document.getElementById('mapDstSelect').value;
    const infoBar = document.getElementById('routeInfoBar');

    try {
        const res = await apiFetch(`/campus/api/route?src=${src}&dst=${dst}`);
        if (res.status === 'ok') {
            const path = res.data.path;
            const dist = res.data.total_meters;
            activeHighlight = { type: 'path', path };
            drawMap();
            infoBar.innerHTML = `<strong>Dijkstra Shortest Path:</strong> [${path.join(' ➔ ')}] — Total Distance: <strong>${dist} meters</strong>.`;
        }
    } catch (err) {
        console.error(err);
    }
}

/**
 * Triggers Kruskal MST computation
 */
async function runKruskalMST() {
    const infoBar = document.getElementById('routeInfoBar');
    try {
        const res = await apiFetch('/campus/api/network');
        if (res.status === 'ok') {
            activeHighlight = { type: 'mst', edges: res.data.mst_edges };
            drawMap();
            infoBar.innerHTML = `<strong>Kruskal Minimum Spanning Tree:</strong> Connects all drop-boxes with <strong>${res.data.total_mst_meters}m</strong> total cable length.`;
        }
    } catch (err) {
        console.error(err);
    }
}

/**
 * Triggers TSP Tour computation
 */
async function runTSPTour() {
    const infoBar = document.getElementById('routeInfoBar');
    try {
        const res = await apiFetch('/campus/api/network');
        if (res.status === 'ok') {
            activeHighlight = { type: 'tsp', tour: res.data.tsp_tour };
            drawMap();
            infoBar.innerHTML = `<strong>TSP Security Patrol Tour:</strong> Loop: [${res.data.tsp_tour.join(' ➔ ')}] — Total Loop: <strong>${res.data.total_tour_meters}m</strong>.`;
        }
    } catch (err) {
        console.error(err);
    }
}

function resetCanvas() {
    activeHighlight = null;
    drawMap();
    document.getElementById('routeInfoBar').innerText = 'Map reset to default campus graph.';
}

window.runDijkstra = runDijkstra;
window.runKruskalMST = runKruskalMST;
window.runTSPTour = runTSPTour;
window.resetCanvas = resetCanvas;
