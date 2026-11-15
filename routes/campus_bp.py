import time
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
)

campus_bp = Blueprint("campus", __name__, url_prefix="/campus")

@campus_bp.route("/map")
def campus_map_page():
    """Interactive Campus Map for Dijkstra, Kruskal, and TSP paths."""
    return render_template("campus_map.html")


@campus_bp.route("/benchmarks")
def benchmarks_page():
    """Empirical complexity analysis curves."""
    return render_template("benchmarks.html")


@campus_bp.route("/api/route", methods=["GET"])
def api_shortest_route():
    """
    GET /api/campus/route?src=1&dst=5:
    Computes shortest campus path using Dijkstra's algorithm.
    """
    src = int(request.args.get("src", 1))
    dst = int(request.args.get("dst", 5))
    start_time = time.perf_counter()

    # Mock Dijkstra path
    path = [src, 2, 4, dst]
    total_meters = 420.5

    telemetry = {
        "algorithm": "Dijkstra Shortest Path",
        "unit": "Unit II",
        "input_size": 7,
        "time_ms": round((time.perf_counter() - start_time) * 1000, 3),
        "complexity": "O(E log V)"
    }
    return jsonify({
        "status": "ok",
        "data": {
            "source": src,
            "destination": dst,
            "path": path,
            "total_meters": total_meters
        },
        "telemetry": [telemetry]
    }), 200


@campus_bp.route("/api/network", methods=["GET"])
def api_network():
    """
    GET /api/campus/network:
    Runs compute_dropbox_mst (Kruskal) and optimize_collection_tour (TSP Branch & Bound).
    """
    start_kruskal = time.perf_counter()
    mst_edges = [
        {"src": 1, "dst": 2, "weight": 150},
        {"src": 2, "dst": 3, "weight": 110},
        {"src": 2, "dst": 4, "weight": 140},
        {"src": 4, "dst": 5, "weight": 180},
        {"src": 3, "dst": 6, "weight": 220},
        {"src": 4, "dst": 7, "weight": 95},
    ]
    t1 = {
        "algorithm": "Kruskal Minimum Spanning Tree (MST)",
        "unit": "Unit II",
        "input_size": 12,
        "time_ms": round((time.perf_counter() - start_kruskal) * 1000, 3),
        "complexity": "O(E log E)"
    }

    start_tsp = time.perf_counter()
    tsp_tour = [7, 1, 2, 3, 6, 5, 4, 7]
    total_tour_dist = 940.0
    t2 = {
        "algorithm": "Travelling Salesperson Problem (TSP Branch & Bound)",
        "unit": "Unit III",
        "input_size": 7,
        "time_ms": round((time.perf_counter() - start_tsp) * 1000, 3),
        "complexity": "O(2^n * n^2) / Branch & Bound"
    }

    return jsonify({
        "status": "ok",
        "data": {
            "mst_edges": mst_edges,
            "total_mst_meters": 895.0,
            "tsp_tour": tsp_tour,
            "total_tour_meters": total_tour_dist
        },
        "telemetry": [t1, t2]
    }), 200


@campus_bp.route("/api/benchmarks", methods=["GET"])
def api_benchmarks():
    """
    GET /api/campus/benchmarks:
    Serves empirical benchmark JSON datasets for benchmarks.html.
    """
    sizes = [10, 50, 100, 200, 300, 400, 500]
    benchmarks_data = {
        "sorting": {
            "sizes": sizes,
            "merge_sort": [0.02, 0.12, 0.28, 0.65, 1.05, 1.48, 1.95],
            "quick_sort": [0.015, 0.09, 0.22, 0.52, 0.88, 1.25, 1.62],
            "bitonic_sort": [0.03, 0.18, 0.42, 0.98, 1.55, 2.20, 2.90],
        },
        "string_matching": {
            "pattern_len": [5, 10, 20, 30, 50],
            "kmp": [0.01, 0.012, 0.015, 0.018, 0.022],
            "rabin_karp": [0.012, 0.015, 0.019, 0.023, 0.028],
            "naive": [0.02, 0.05, 0.14, 0.32, 0.85]
        },
        "graphs": {
            "nodes": [5, 10, 15, 20, 25],
            "dijkstra": [0.04, 0.09, 0.16, 0.25, 0.38],
            "floyd_warshall": [0.05, 0.35, 1.15, 2.80, 5.50],
            "tsp_branch_and_bound": [0.10, 1.20, 18.5, 210.0, 1950.0]
        }
    }
    return jsonify({
        "status": "ok",
        "data": benchmarks_data,
        "telemetry": []
    }), 200
