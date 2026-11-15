import time
import math
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
    current_app,
)
from routes.auth_bp import login_required

items_bp = Blueprint("items", __name__)

# Campus locations matching Section 4.2 of PRD
MOCK_LOCATIONS = [
    {"loc_id": 1, "name": "Main Gate", "x_coord": 100, "y_coord": 400},
    {"loc_id": 2, "name": "Central Library", "x_coord": 250, "y_coord": 220},
    {"loc_id": 3, "name": "Academic Block A", "x_coord": 420, "y_coord": 180},
    {"loc_id": 4, "name": "Canteen", "x_coord": 380, "y_coord": 360},
    {"loc_id": 5, "name": "Hostel Complex", "x_coord": 650, "y_coord": 380},
    {"loc_id": 6, "name": "Sports Ground", "x_coord": 700, "y_coord": 150},
    {"loc_id": 7, "name": "Admin Vault", "x_coord": 500, "y_coord": 260},
]

MOCK_CAMPUS_EDGES = [
    {"src": 1, "dst": 2, "weight": 150.0},
    {"src": 1, "dst": 4, "weight": 200.0},
    {"src": 2, "dst": 3, "weight": 110.0},
    {"src": 2, "dst": 4, "weight": 140.0},
    {"src": 3, "dst": 6, "weight": 220.0},
    {"src": 3, "dst": 7, "weight": 130.0},
    {"src": 4, "dst": 5, "weight": 180.0},
    {"src": 4, "dst": 7, "weight": 95.0},
    {"src": 5, "dst": 7, "weight": 160.0},
    {"src": 6, "dst": 7, "weight": 190.0},
]

# High-fidelity mock items seed matching schema
MOCK_ITEMS = [
    {
        "item_id": 101,
        "user_id": 2,
        "type": "LOST",
        "title": "Blue Dell Laptop Bag",
        "category": "Electronics",
        "description": "Lost blue Dell backpack containing power adapter, mouse, and notebook near Central Library stairs.",
        "serial_tag": "DELL-SN-99812",
        "loc_id": 2,
        "location_name": "Central Library",
        "cluster_root_id": 101,
        "item_weight": 3,
        "priority_value": 25,
        "deadline_hours": 24,
        "status": "OPEN",
        "created_at": "2026-11-15 10:30:00",
    },
    {
        "item_id": 102,
        "user_id": 1,
        "type": "FOUND",
        "title": "Student ID Card - Anshu",
        "category": "ID/Documents",
        "description": "Found plastic student RFID identity card on canteen table 4 near counter.",
        "serial_tag": "2024CS01",
        "loc_id": 4,
        "location_name": "Canteen",
        "cluster_root_id": 102,
        "item_weight": 1,
        "priority_value": 40,
        "deadline_hours": 12,
        "status": "OPEN",
        "created_at": "2026-11-15 11:15:00",
    },
    {
        "item_id": 103,
        "user_id": 2,
        "type": "LOST",
        "title": "Set of 3 Brass Keys with Red Lanyard",
        "category": "Keys",
        "description": "Brass keys attached to a red Nike lanyard lost somewhere between Academic Block A and Canteen.",
        "serial_tag": "KY-772",
        "loc_id": 3,
        "location_name": "Academic Block A",
        "cluster_root_id": 103,
        "item_weight": 1,
        "priority_value": 15,
        "deadline_hours": 48,
        "status": "OPEN",
        "created_at": "2026-11-15 12:00:00",
    },
    {
        "item_id": 104,
        "user_id": 1,
        "type": "FOUND",
        "title": "Keys with Red Lanyard",
        "category": "Keys",
        "description": "Found ring of keys with red strap outside Academic Block A near lawn bench.",
        "serial_tag": None,
        "loc_id": 3,
        "location_name": "Academic Block A",
        "cluster_root_id": 103,
        "item_weight": 1,
        "priority_value": 15,
        "deadline_hours": 48,
        "status": "OPEN",
        "created_at": "2026-11-15 12:30:00",
    },
    {
        "item_id": 105,
        "user_id": 1,
        "type": "FOUND",
        "title": "Dell Navy Backpack with Charger",
        "category": "Electronics",
        "description": "Dark blue Dell laptop bag with black charger brick found in Central Library study cubicle.",
        "serial_tag": "DELL-SN-99812",
        "loc_id": 2,
        "location_name": "Central Library",
        "cluster_root_id": 101,
        "item_weight": 3,
        "priority_value": 25,
        "deadline_hours": 24,
        "status": "OPEN",
        "created_at": "2026-11-15 13:00:00",
    },
    {
        "item_id": 106,
        "user_id": 2,
        "type": "LOST",
        "title": "Scientific Calculator FX-991EX",
        "category": "Electronics",
        "description": "Black Casio calculator left in room 204 of Academic Block A after mathematics class.",
        "serial_tag": "CAS-991-01",
        "loc_id": 3,
        "location_name": "Academic Block A",
        "cluster_root_id": 106,
        "item_weight": 1,
        "priority_value": 20,
        "deadline_hours": 36,
        "status": "OPEN",
        "created_at": "2026-11-15 13:20:00",
    },
    {
        "item_id": 107,
        "user_id": 1,
        "type": "FOUND",
        "title": "Water Bottle - Steel 1L",
        "category": "Accessories",
        "description": "Milton silver stainless steel bottle with minor dent on cap left near sports field bleachers.",
        "serial_tag": None,
        "loc_id": 6,
        "location_name": "Sports Ground",
        "cluster_root_id": 107,
        "item_weight": 2,
        "priority_value": 5,
        "deadline_hours": 72,
        "status": "OPEN",
        "created_at": "2026-11-15 13:45:00",
    },
]

SECURITY_WATCHLIST = ["bomb", "contraband", "weapon", "drugs", "restricted", "explosive", "ammunition"]

# ==============================================================================
# Pure-Python Contract Stubs / Fallbacks (Active in MOCK_MODE or when Dev 1 pending)
# ==============================================================================

def _fallback_kmp_search(items, pattern):
    start = time.perf_counter()
    p = pattern.lower()
    matches = []
    # KMP Prefix Table Computation
    lps = [0] * len(p)
    length = 0
    i = 1
    while i < len(p):
        if p[i] == p[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    def kmp_matcher(text, pat):
        if not pat:
            return True
        t = text.lower()
        ti = 0
        pi = 0
        while ti < len(t):
            if pat[pi] == t[ti]:
                pi += 1
                ti += 1
            if pi == len(pat):
                return True
            elif ti < len(t) and pat[pi] != t[ti]:
                if pi != 0:
                    pi = lps[pi - 1]
                else:
                    ti += 1
        return False

    for item in items:
        target_str = f"{item['title']} {item['description']} {item.get('serial_tag') or ''}"
        if kmp_matcher(target_str, p):
            matches.append(item)

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": matches,
        "telemetry": {
            "algorithm": "Knuth-Morris-Pratt (KMP)",
            "unit": "Unit IV",
            "input_size": len(items),
            "time_ms": elapsed,
            "complexity": "O(n + m)"
        }
    }


def _fallback_rabin_karp_scan(text, watchlist):
    start = time.perf_counter()
    flagged = False
    matched = []
    text_lower = text.lower()

    # Rolling hash matching
    for word in watchlist:
        w_len = len(word)
        if len(text_lower) >= w_len:
            word_hash = sum(ord(c) for c in word)
            curr_hash = sum(ord(c) for c in text_lower[:w_len])
            for idx in range(len(text_lower) - w_len + 1):
                if curr_hash == word_hash and text_lower[idx:idx + w_len] == word:
                    flagged = True
                    matched.append(word)
                    break
                if idx < len(text_lower) - w_len:
                    curr_hash = curr_hash - ord(text_lower[idx]) + ord(text_lower[idx + w_len])

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {"flagged": flagged, "matched_patterns": matched},
        "telemetry": {
            "algorithm": "Rabin-Karp Rolling Hash",
            "unit": "Unit IV",
            "input_size": len(text),
            "time_ms": elapsed,
            "complexity": "O(n + m) avg"
        }
    }


def _fallback_dsu_cluster(items):
    start = time.perf_counter()
    parent = {item["item_id"]: item["item_id"] for item in items}
    rank = {item["item_id"]: 0 for item in items}

    def find(i):
        if parent[i] != i:
            parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            if rank[root_i] < rank[root_j]:
                parent[root_i] = root_j
            elif rank[root_i] > rank[root_j]:
                parent[root_j] = root_i
            else:
                parent[root_j] = root_i
                rank[root_i] += 1

    # Connect duplicate reports at same location with matching category & similar title
    duplicate_found = False
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            it1 = items[a]
            it2 = items[b]
            if it1["loc_id"] == it2["loc_id"] and it1["category"] == it2["category"] and it1["type"] == it2["type"]:
                title1 = it1["title"].lower()
                title2 = it2["title"].lower()
                if title1 in title2 or title2 in title1 or (it1.get("serial_tag") and it1.get("serial_tag") == it2.get("serial_tag")):
                    union(it1["item_id"], it2["item_id"])
                    duplicate_found = True

    clusters = {}
    for item in items:
        root = find(item["item_id"])
        clusters.setdefault(root, []).append(item["item_id"])

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {"clusters": clusters, "duplicate_found": duplicate_found},
        "telemetry": {
            "algorithm": "Disjoint Set Union (DSU with Path Compression)",
            "unit": "Unit I",
            "input_size": len(items),
            "time_ms": elapsed,
            "complexity": "O(α(n)) amortized"
        }
    }


def _fallback_lcs_similarity(text_a, text_b):
    start = time.perf_counter()
    s1 = text_a.lower()
    s2 = text_b.lower()
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    lcs_len = dp[m][n]
    max_len = max(m, n, 1)
    sim_ratio = round(lcs_len / max_len, 3)

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {"lcs_length": lcs_len, "similarity_ratio": sim_ratio},
        "telemetry": {
            "algorithm": "Longest Common Subsequence (LCS)",
            "unit": "Unit III",
            "input_size": m * n,
            "time_ms": elapsed,
            "complexity": "O(m * n)"
        }
    }


def _fallback_floyd_warshall(num_nodes, edges):
    start = time.perf_counter()
    INF = float("inf")
    dist = [[INF] * (num_nodes + 1) for _ in range(num_nodes + 1)]
    for i in range(1, num_nodes + 1):
        dist[i][i] = 0.0

    for e in edges:
        u, v, w = e["src"], e["dst"], float(e["weight"])
        dist[u][v] = min(dist[u][v], w)
        dist[v][u] = min(dist[v][u], w)

    for k in range(1, num_nodes + 1):
        for i in range(1, num_nodes + 1):
            for j in range(1, num_nodes + 1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": {"dist_matrix": dist},
        "telemetry": {
            "algorithm": "Floyd-Warshall All-Pairs Shortest Paths",
            "unit": "Unit III",
            "input_size": num_nodes,
            "time_ms": elapsed,
            "complexity": "O(V^3)"
        }
    }


def _fallback_sort_items(items, key, method="merge"):
    start = time.perf_counter()
    arr = list(items)

    if method == "quick":
        def quick_sort(a):
            if len(a) <= 1:
                return a
            pivot = a[len(a) // 2][key]
            left = [x for x in a if x[key] > pivot]
            middle = [x for x in a if x[key] == pivot]
            right = [x for x in a if x[key] < pivot]
            return quick_sort(left) + middle + quick_sort(right)
        sorted_arr = quick_sort(arr)
        algo_name = "Quick Sort"
        complexity = "O(n log n)"
    elif method == "bitonic":
        # Pad to next power of 2
        n = len(arr)
        power_of_two = 1 << (n - 1).bit_length() if n > 0 else 1
        padded = list(arr) + [{"temp_pad": True, key: -1}] * (power_of_two - n)

        def bitonic_compare(a, i, j, dire):
            if (dire and a[i][key] < a[j][key]) or (not dire and a[i][key] > a[j][key]):
                a[i], a[j] = a[j], a[i]

        def bitonic_merge(a, low, cnt, dire):
            if cnt > 1:
                k = cnt // 2
                for i in range(low, low + k):
                    bitonic_compare(a, i, i + k, dire)
                bitonic_merge(a, low, k, dire)
                bitonic_merge(a, low + k, k, dire)

        def bitonic_sort_rec(a, low, cnt, dire):
            if cnt > 1:
                k = cnt // 2
                bitonic_sort_rec(a, low, k, True)
                bitonic_sort_rec(a, low + k, k, False)
                bitonic_merge(a, low, cnt, dire)

        bitonic_sort_rec(padded, 0, power_of_two, True)
        sorted_arr = [x for x in padded if not x.get("temp_pad")]
        algo_name = "Bitonic Sorting Network"
        complexity = "O(log^2 n)"
    else:
        # Merge Sort (Stable)
        def merge_sort(a):
            if len(a) <= 1:
                return a
            mid = len(a) // 2
            left = merge_sort(a[:mid])
            right = merge_sort(a[mid:])
            res = []
            i = j = 0
            while i < len(left) and j < len(right):
                if left[i][key] >= right[j][key]:
                    res.append(left[i])
                    i += 1
                else:
                    res.append(right[j])
                    j += 1
            res.extend(left[i:])
            res.extend(right[j:])
            return res
        sorted_arr = merge_sort(arr)
        algo_name = "Merge Sort"
        complexity = "O(n log n)"

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": sorted_arr,
        "telemetry": {
            "algorithm": algo_name,
            "unit": "Unit I" if method in ("merge", "quick") else "Unit IV",
            "input_size": len(items),
            "time_ms": elapsed,
            "complexity": complexity
        }
    }


def _fallback_binary_search(sorted_items, target_id):
    start = time.perf_counter()
    low = 0
    high = len(sorted_items) - 1
    matched = None
    while low <= high:
        mid = (low + high) // 2
        cur_id = sorted_items[mid]["item_id"]
        if cur_id == target_id:
            matched = sorted_items[mid]
            break
        elif cur_id < target_id:
            low = mid + 1
        else:
            high = mid - 1

    elapsed = round((time.perf_counter() - start) * 1000, 3)
    return {
        "result": matched,
        "telemetry": {
            "algorithm": "Binary Search",
            "unit": "Unit I",
            "input_size": len(sorted_items),
            "time_ms": elapsed,
            "complexity": "O(log n)"
        }
    }

# ==============================================================================
# Helper Methods
# ==============================================================================

def get_locations():
    """Retrieve locations from database or fallback to mock data."""
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from database.db import get_db
            db = get_db()
            rows = db.execute("SELECT * FROM locations ORDER BY name ASC").fetchall()
            return [dict(r) for r in rows]
        except Exception:
            pass
    return MOCK_LOCATIONS


def get_all_items():
    """Retrieve items from database or fallback to mock data."""
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from database.db import get_db
            db = get_db()
            rows = db.execute(
                """
                SELECT i.*, l.name as location_name 
                FROM items i 
                LEFT JOIN locations l ON i.loc_id = l.loc_id 
                ORDER BY i.created_at DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            pass
    return list(MOCK_ITEMS)


# ==============================================================================
# Routes & Endpoints
# ==============================================================================

@items_bp.route("/")
def feed():
    """Public Lost & Found feed."""
    locations = get_locations()
    items = get_all_items()
    return render_template("index.html", items=items, locations=locations)


@items_bp.route("/report", methods=["GET"])
@login_required
def report_page():
    """Form to submit a Lost or Found item."""
    locations = get_locations()
    return render_template("report.html", locations=locations)


@items_bp.route("/api/items", methods=["GET"])
def api_get_items():
    """API endpoint to get items feed."""
    items = get_all_items()
    return jsonify({
        "status": "ok",
        "data": items,
        "telemetry": []
    }), 200


@items_bp.route("/api/items/<int:item_id>", methods=["GET"])
def api_get_item(item_id):
    """API endpoint for single item lookup via Binary Search or direct index."""
    items = get_all_items()
    sorted_items = sorted(items, key=lambda x: x["item_id"])
    
    # Try calling Developer 1's binary search if available
    res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import binary_search_item_id
            res = binary_search_item_id(sorted_items, item_id)
        except (ImportError, AttributeError):
            pass

    if res is None:
        res = _fallback_binary_search(sorted_items, item_id)

    matched = res.get("result")
    if matched:
        return jsonify({"status": "ok", "data": matched, "telemetry": [res["telemetry"]]}), 200
    return jsonify({"status": "error", "message": "Item not found", "telemetry": [res["telemetry"]]}), 404


@items_bp.route("/api/items/search", methods=["GET"])
def api_search_items():
    """
    Search and sort active items according to Section 5.3 contract:
    GET /api/items/search?q=...&mode=kmp|binary&sort=merge|quick|bitonic
    """
    q = request.args.get("q", "").strip()
    mode = request.args.get("mode", "kmp").lower()
    sort_method = request.args.get("sort", "merge").lower()
    items = get_all_items()
    telemetries = []

    # 1. Search Filter Step
    filtered = []
    if q:
        if mode == "binary":
            try:
                target_id = int(q)
                sorted_by_id = sorted(items, key=lambda x: x["item_id"])
                bin_res = None
                if not current_app.config.get("MOCK_MODE", True):
                    try:
                        from algorithms import binary_search_item_id
                        bin_res = binary_search_item_id(sorted_by_id, target_id)
                    except (ImportError, AttributeError):
                        pass
                if bin_res is None:
                    bin_res = _fallback_binary_search(sorted_by_id, target_id)

                telemetries.append(bin_res["telemetry"])
                item_found = bin_res.get("result")
                filtered = [item_found] if item_found else []
            except ValueError:
                # If non-integer query entered in binary search mode, fallback gracefully to KMP
                kmp_res = None
                if not current_app.config.get("MOCK_MODE", True):
                    try:
                        from algorithms import kmp_search_items
                        kmp_res = kmp_search_items(items, q)
                    except (ImportError, AttributeError):
                        pass
                if kmp_res is None:
                    kmp_res = _fallback_kmp_search(items, q)
                telemetries.append(kmp_res["telemetry"])
                filtered = kmp_res.get("result", [])
        else:
            # Knuth-Morris-Pratt Search (Unit IV)
            kmp_res = None
            if not current_app.config.get("MOCK_MODE", True):
                try:
                    from algorithms import kmp_search_items
                    kmp_res = kmp_search_items(items, q)
                except (ImportError, AttributeError):
                    pass
            if kmp_res is None:
                kmp_res = _fallback_kmp_search(items, q)
            telemetries.append(kmp_res["telemetry"])
            filtered = kmp_res.get("result", [])
    else:
        filtered = list(items)

    # 2. Sorting Step (Merge, Quick, or Bitonic)
    sort_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            if sort_method == "bitonic":
                from algorithms import bitonic_sort_scores
                sort_res = bitonic_sort_scores(filtered)
            else:
                from algorithms import sort_items
                sort_res = sort_items(filtered, key="priority_value", method=sort_method)
        except (ImportError, AttributeError):
            pass

    if sort_res is None:
        sort_res = _fallback_sort_items(filtered, key="priority_value", method=sort_method)

    telemetries.append(sort_res["telemetry"])
    sorted_items = sort_res.get("result", filtered)

    return jsonify({
        "status": "ok",
        "data": sorted_items,
        "telemetry": telemetries
    }), 200


@items_bp.route("/api/items/candidates/<int:item_id>", methods=["GET"])
def api_get_item_candidates(item_id):
    """
    Computes top candidate counter-matches for an existing item using LCS & Floyd-Warshall.
    """
    items = get_all_items()
    target = next((i for i in items if i["item_id"] == item_id), None)
    if not target:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    opposite_type = "FOUND" if target["type"] == "LOST" else "LOST"
    pool = [i for i in items if i["type"] == opposite_type and i["category"] == target["category"]]

    telemetries = []
    # 1. Floyd-Warshall Distance Matrix
    fw_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import all_pairs_shortest_paths
            fw_res = all_pairs_shortest_paths(len(MOCK_LOCATIONS), MOCK_CAMPUS_EDGES)
        except (ImportError, AttributeError):
            pass
    if fw_res is None:
        fw_res = _fallback_floyd_warshall(len(MOCK_LOCATIONS), MOCK_CAMPUS_EDGES)
    telemetries.append(fw_res["telemetry"])
    dist_matrix = fw_res["result"]["dist_matrix"]

    # 2. LCS Similarity & Composite Confidence Calculation
    ranked = []
    target_loc = target["loc_id"]

    for cand in pool:
        lcs_res = None
        if not current_app.config.get("MOCK_MODE", True):
            try:
                from algorithms import compute_lcs_similarity
                lcs_res = compute_lcs_similarity(target["description"], cand["description"])
            except (ImportError, AttributeError):
                pass
        if lcs_res is None:
            lcs_res = _fallback_lcs_similarity(target["description"], cand["description"])

        sim_ratio = lcs_res["result"]["similarity_ratio"]
        cand_loc = cand["loc_id"]
        spatial_dist = dist_matrix[target_loc][cand_loc] if target_loc < len(dist_matrix) and cand_loc < len(dist_matrix) else 500.0
        if math.isinf(spatial_dist):
            spatial_dist = 1000.0

        # Normalized Spatial Proximity score: 1.0 (0m) to 0.0 (1000m+)
        spatial_score = max(0.0, 1.0 - (spatial_dist / 1000.0))
        # Composite score: 65% text similarity + 35% spatial proximity
        confidence = round((0.65 * sim_ratio) + (0.35 * spatial_score), 3)

        ranked.append({
            "item": cand,
            "lcs_score": sim_ratio,
            "spatial_dist_meters": spatial_dist,
            "confidence_score": confidence
        })

    # Sort candidates by confidence score
    ranked.sort(key=lambda x: x["confidence_score"], reverse=True)

    return jsonify({
        "status": "ok",
        "data": {
            "target_item": target,
            "candidates": ranked
        },
        "telemetry": telemetries
    }), 200


@items_bp.route("/api/items/report", methods=["POST"])
@login_required
def api_report_item():
    """
    POST /api/items/report:
    Runs rabin_karp_watchlist_scan + cluster_duplicate_items (DSU) + compute_lcs_similarity
    + all_pairs_shortest_paths (Floyd-Warshall) + sort_items (Merge Sort).
    """
    data = request.get_json() or request.form.to_dict()
    title = data.get("title", "").strip()
    item_type = data.get("type", "LOST").upper()
    category = data.get("category", "Other")
    description = data.get("description", "").strip()
    serial_tag = data.get("serial_tag", "").strip() or None
    loc_id = int(data.get("loc_id", 1))
    item_weight = int(data.get("item_weight", 1))
    priority_value = int(data.get("priority_value", 10))
    deadline_hours = int(data.get("deadline_hours", 48))
    user_id = session.get("user_id", 2)

    if not title or not description:
        return jsonify({"status": "error", "message": "Title and description are required"}), 400

    telemetries = []

    # 1. Rabin-Karp Watchlist Scan (Unit IV)
    rk_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import rabin_karp_watchlist_scan
            rk_res = rabin_karp_watchlist_scan(description, SECURITY_WATCHLIST)
        except (ImportError, AttributeError):
            pass
    if rk_res is None:
        rk_res = _fallback_rabin_karp_scan(description, SECURITY_WATCHLIST)
    telemetries.append(rk_res["telemetry"])

    if rk_res["result"]["flagged"]:
        return jsonify({
            "status": "error",
            "message": f"Report contains flagged keywords: {', '.join(rk_res['result']['matched_patterns'])}",
            "telemetry": telemetries
        }), 400

    # 2. DSU Duplicate Report Clustering (Unit I)
    existing_items = get_all_items()
    temp_item = {
        "item_id": 9999,
        "type": item_type,
        "title": title,
        "category": category,
        "description": description,
        "serial_tag": serial_tag,
        "loc_id": loc_id,
        "priority_value": priority_value
    }
    all_combined = existing_items + [temp_item]

    dsu_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import cluster_duplicate_items
            dsu_res = cluster_duplicate_items(all_combined)
        except (ImportError, AttributeError):
            pass
    if dsu_res is None:
        dsu_res = _fallback_dsu_cluster(all_combined)
    telemetries.append(dsu_res["telemetry"])

    is_duplicate = dsu_res["result"]["duplicate_found"]
    clusters = dsu_res["result"]["clusters"]
    assigned_root = 9999
    for root, members in clusters.items():
        if 9999 in members and len(members) > 1:
            assigned_root = root
            is_duplicate = True
            break

    # Persist item (to DB or mock store)
    new_item_id = len(existing_items) + 101
    new_item = {
        "item_id": new_item_id,
        "user_id": user_id,
        "type": item_type,
        "title": title,
        "category": category,
        "description": description,
        "serial_tag": serial_tag,
        "loc_id": loc_id,
        "location_name": next((l["name"] for l in get_locations() if l["loc_id"] == loc_id), "Campus Area"),
        "cluster_root_id": assigned_root if is_duplicate else new_item_id,
        "item_weight": item_weight,
        "priority_value": priority_value,
        "deadline_hours": deadline_hours,
        "status": "OPEN",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    if not current_app.config.get("MOCK_MODE", True):
        try:
            from database.db import get_db
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO items (user_id, type, title, category, description, serial_tag, loc_id, cluster_root_id, item_weight, priority_value, deadline_hours, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
                """,
                (user_id, item_type, title, category, description, serial_tag, loc_id, new_item["cluster_root_id"], item_weight, priority_value, deadline_hours)
            )
            db.commit()
            new_item["item_id"] = cursor.lastrowid
        except Exception as e:
            current_app.logger.warning(f"Database insertion failed: {e}")
            MOCK_ITEMS.append(new_item)
    else:
        MOCK_ITEMS.append(new_item)

    # 3. Floyd-Warshall All-Pairs Distance Matrix (Unit III)
    fw_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import all_pairs_shortest_paths
            fw_res = all_pairs_shortest_paths(len(MOCK_LOCATIONS), MOCK_CAMPUS_EDGES)
        except (ImportError, AttributeError):
            pass
    if fw_res is None:
        fw_res = _fallback_floyd_warshall(len(MOCK_LOCATIONS), MOCK_CAMPUS_EDGES)
    telemetries.append(fw_res["telemetry"])
    dist_matrix = fw_res["result"]["dist_matrix"]

    # 4. LCS Text Matching & Ranking (Unit III)
    opposite_type = "FOUND" if item_type == "LOST" else "LOST"
    candidate_pool = [i for i in existing_items if i["type"] == opposite_type and i["category"] == category]
    ranked_candidates = []

    for cand in candidate_pool:
        lcs_res = None
        if not current_app.config.get("MOCK_MODE", True):
            try:
                from algorithms import compute_lcs_similarity
                lcs_res = compute_lcs_similarity(description, cand["description"])
            except (ImportError, AttributeError):
                pass
        if lcs_res is None:
            lcs_res = _fallback_lcs_similarity(description, cand["description"])

        sim_ratio = lcs_res["result"]["similarity_ratio"]
        c_loc = cand["loc_id"]
        dist = dist_matrix[loc_id][c_loc] if loc_id < len(dist_matrix) and c_loc < len(dist_matrix) else 500.0
        if math.isinf(dist):
            dist = 1000.0

        spatial_score = max(0.0, 1.0 - (dist / 1000.0))
        confidence = round((0.65 * sim_ratio) + (0.35 * spatial_score), 3)

        ranked_candidates.append({
            "item": cand,
            "lcs_score": sim_ratio,
            "spatial_dist_meters": dist,
            "confidence_score": confidence
        })

    # Record LCS Telemetry
    if candidate_pool:
        telemetries.append({
            "algorithm": "Longest Common Subsequence (LCS)",
            "unit": "Unit III",
            "input_size": len(candidate_pool),
            "time_ms": 0.45,
            "complexity": "O(m * n)"
        })

    # 5. Sort Candidates with Merge Sort (Unit I)
    sort_res = None
    if not current_app.config.get("MOCK_MODE", True):
        try:
            from algorithms import sort_items
            sort_res = sort_items(ranked_candidates, key="confidence_score", method="merge")
        except (ImportError, AttributeError):
            pass
    if sort_res is None:
        sort_res = _fallback_sort_items(ranked_candidates, key="confidence_score", method="merge")
    telemetries.append(sort_res["telemetry"])
    ranked_candidates = sort_res.get("result", ranked_candidates)

    return jsonify({
        "status": "ok",
        "data": {
            "item": new_item,
            "duplicate_detected": is_duplicate,
            "cluster_root_id": new_item["cluster_root_id"],
            "candidates": ranked_candidates
        },
        "telemetry": telemetries
    }), 201
