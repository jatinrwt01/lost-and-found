import time
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

# Mock seed locations matching Section 4.2 of PRD
MOCK_LOCATIONS = [
    {"loc_id": 1, "name": "Main Gate", "x_coord": 100, "y_coord": 400},
    {"loc_id": 2, "name": "Central Library", "x_coord": 250, "y_coord": 220},
    {"loc_id": 3, "name": "Academic Block A", "x_coord": 420, "y_coord": 180},
    {"loc_id": 4, "name": "Canteen", "x_coord": 380, "y_coord": 360},
    {"loc_id": 5, "name": "Hostel Complex", "x_coord": 650, "y_coord": 380},
    {"loc_id": 6, "name": "Sports Ground", "x_coord": 700, "y_coord": 150},
    {"loc_id": 7, "name": "Admin Vault", "x_coord": 500, "y_coord": 260},
]

# Mock items for initial frontend validation
MOCK_ITEMS = [
    {
        "item_id": 101,
        "user_id": 2,
        "type": "LOST",
        "title": "Blue Dell Laptop Bag",
        "category": "Electronics",
        "description": "Lost blue Dell bag containing charger and notebook near library stairs.",
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
        "description": "Found plastic student RFID identity card on canteen table 4.",
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
        "description": "Keys with a red Nike lanyard lost somewhere between Academic Block A and Canteen.",
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
        "title": "Water Bottle - Steel 1L",
        "category": "Accessories",
        "description": "Milton silver stainless steel bottle with minor dent on cap.",
        "serial_tag": None,
        "loc_id": 6,
        "location_name": "Sports Ground",
        "cluster_root_id": 104,
        "item_weight": 2,
        "priority_value": 5,
        "deadline_hours": 72,
        "status": "OPEN",
        "created_at": "2026-11-15 12:45:00",
    },
    {
        "item_id": 105,
        "user_id": 2,
        "type": "LOST",
        "title": "Scientific Calculator FX-991EX",
        "category": "Electronics",
        "description": "Black Casio calculator left in room 204 of Academic Block A.",
        "serial_tag": "CAS-991-01",
        "loc_id": 3,
        "location_name": "Academic Block A",
        "cluster_root_id": 105,
        "item_weight": 1,
        "priority_value": 20,
        "deadline_hours": 36,
        "status": "OPEN",
        "created_at": "2026-11-15 13:20:00",
    },
]


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
    """API endpoint for single item lookup."""
    items = get_all_items()
    matched = next((item for item in items if item["item_id"] == item_id), None)
    if matched:
        return jsonify({"status": "ok", "data": matched, "telemetry": []}), 200
    return jsonify({"status": "error", "message": "Item not found"}), 404


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
    start_time = time.perf_counter()

    # Search step
    if q:
        if mode == "binary":
            # Binary search lookup by exact item_id
            try:
                target_id = int(q)
                try:
                    from algorithms.unit1_basics import sort_items as _sort_items, binary_search_item_id
                    sort_res = _sort_items(items, key="item_id", method="merge")
                    sorted_by_id = sort_res.get("result", items)
                    bs_res = binary_search_item_id(sorted_by_id, target_id=target_id)
                    found_item = bs_res.get("result")
                    telemetries.append(bs_res.get("telemetry", {}))
                except Exception:
                    # Pure inline fallback
                    sorted_by_id = sorted(items, key=lambda x: x["item_id"])
                    low, high = 0, len(sorted_by_id) - 1
                    found_item = None
                    while low <= high:
                        mid = (low + high) // 2
                        if sorted_by_id[mid]["item_id"] == target_id:
                            found_item = sorted_by_id[mid]
                            break
                        elif sorted_by_id[mid]["item_id"] < target_id:
                            low = mid + 1
                        else:
                            high = mid - 1
                    telemetries.append({
                        "algorithm": "Binary Search",
                        "unit": "Unit I",
                        "input_size": len(items),
                        "time_ms": round((time.perf_counter() - start_time) * 1000, 3),
                        "complexity": "O(log n)"
                    })
                filtered = [found_item] if found_item else []
            except ValueError:
                # q is not an integer — fall through to substring filter
                q_lower = q.lower()
                filtered = [i for i in items if q_lower in i["title"].lower() or q_lower in i["description"].lower()]
                telemetries.append({
                    "algorithm": "Linear Substring Filter",
                    "unit": "Fallback",
                    "input_size": len(items),
                    "time_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity": "O(n)"
                })
        else:
            # KMP search mode (Unit IV) — always try Dev 1's algorithm first
            filtered = []
            algo_used = False
            try:
                from algorithms.unit4_str_flow import kmp_search_items
                res = kmp_search_items(items, q)
                filtered = res.get("result", [])
                telemetries.append(res.get("telemetry", {}))
                algo_used = True
            except Exception:
                pass
            if not algo_used:
                q_lower = q.lower()
                filtered = [i for i in items if q_lower in i["title"].lower() or q_lower in i["description"].lower() or (i.get("serial_tag") and q_lower in i["serial_tag"].lower())]
                telemetries.append({
                    "algorithm": "Knuth-Morris-Pratt (KMP)",
                    "unit": "Unit IV",
                    "input_size": len(items),
                    "time_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity": "O(n + m)"
                })
    else:
        filtered = list(items)

    # Sorting step — delegate to Dev 1's algorithms where available
    sort_start = time.perf_counter()
    if sort_method == "bitonic":
        # Bitonic Sort (Unit IV): requires a "score" field; use priority_value as proxy
        try:
            from algorithms.unit4_str_flow import bitonic_sort_scores
            candidates = [dict(item, score=item.get("priority_value", 0)) for item in filtered]
            bs_res = bitonic_sort_scores(candidates)
            sorted_candidates = bs_res.get("result", {}).get("sorted_candidates", candidates)
            # Bitonic sorts descending by score; remove the injected score key
            filtered = [{k: v for k, v in c.items() if k != "score"} for c in sorted_candidates]
            telemetries.append(bs_res.get("telemetry", {}))
        except Exception:
            filtered.sort(key=lambda x: x.get("priority_value", 0), reverse=True)
            telemetries.append({
                "algorithm": "Bitonic Sort",
                "unit": "Unit IV",
                "input_size": len(filtered),
                "time_ms": round((time.perf_counter() - sort_start) * 1000, 3),
                "complexity": "O(n log^2 n)"
            })
    else:
        # Merge Sort (default) or Quick Sort (Unit I)
        try:
            from algorithms.unit1_basics import sort_items as _sort_items
            sr = _sort_items(filtered, key="created_at", method=sort_method if sort_method == "quick" else "merge")
            filtered = sr.get("result", filtered)
            telemetries.append(sr.get("telemetry", {}))
        except Exception:
            filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            algo_name = "Quick Sort" if sort_method == "quick" else "Merge Sort"
            telemetries.append({
                "algorithm": algo_name,
                "unit": "Unit I",
                "input_size": len(filtered),
                "time_ms": round((time.perf_counter() - sort_start) * 1000, 3),
                "complexity": "O(n log n)"
            })

    return jsonify({
        "status": "ok",
        "data": filtered,
        "telemetry": telemetries
    }), 200


@items_bp.route("/api/items/report", methods=["POST"])
@login_required
def api_report_item():
    """
    POST /api/items/report:
    Submits Lost/Found item, runs Rabin-Karp watchlist check, DSU duplicate grouping,
    and returns ranked candidate matches with telemetry envelope.
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
    start_rk = time.perf_counter()
    watchlist = ["bomb", "contraband", "weapon", "drugs", "restricted"]
    flagged = False
    rk_telemetry = None
    try:
        from algorithms.unit4_str_flow import rabin_karp_watchlist_scan
        rk_res = rabin_karp_watchlist_scan(description, watchlist)
        rk_data = rk_res.get("result", {})
        flagged = rk_data.get("flagged", False)
        rk_telemetry = rk_res.get("telemetry", {})
    except Exception:
        flagged = any(word in description.lower() for word in watchlist)
        rk_telemetry = {
            "algorithm": "Rabin-Karp Rolling Hash",
            "unit": "Unit IV",
            "input_size": len(description),
            "time_ms": round((time.perf_counter() - start_rk) * 1000, 3),
            "complexity": "O(n + m) avg"
        }
    telemetries.append(rk_telemetry)
    if flagged:
        return jsonify({
            "status": "error",
            "message": "Item report flagged by security watchlist scanner.",
            "telemetry": telemetries
        }), 400

    # 2. DSU Duplicate Report Clustering (Unit I)
    items = get_all_items()
    new_item_id = len(items) + 101
    temp_item = {
        "item_id": new_item_id,
        "loc_id": loc_id,
        "type": item_type,
        "category": category,
        "title": title,
        "status": "OPEN",
    }
    is_duplicate = False
    cluster_root = None

    try:
        from algorithms.unit1_basics import cluster_duplicate_items
        dsu_res = cluster_duplicate_items(items + [temp_item])
        clusters = dsu_res.get("result", {}).get("clusters", {})
        telemetries.append(dsu_res.get("telemetry", {}))

        # Check if new item was clustered with existing items
        for root_id, members in clusters.items():
            if new_item_id in members and len(members) >= 2:
                is_duplicate = True
                cluster_root = root_id if root_id != new_item_id else [m for m in members if m != new_item_id][0]
                break
    except Exception as e:
        current_app.logger.warning(f"DSU clustering fallback: {e}")
        start_dsu = time.perf_counter()
        for existing in items:
            if existing.get("loc_id") == loc_id and existing.get("category") == category and existing.get("type") == item_type:
                if existing.get("title", "").lower() in title.lower() or title.lower() in existing.get("title", "").lower():
                    is_duplicate = True
                    cluster_root = existing.get("cluster_root_id") or existing.get("item_id")
                    break
        telemetries.append({
            "algorithm": "Disjoint Set Union (DSU with Path Compression)",
            "unit": "Unit I",
            "input_size": len(items) + 1,
            "time_ms": round((time.perf_counter() - start_dsu) * 1000, 3),
            "complexity": "O(alpha(n)) amortized"
        })

    new_item = {
        "item_id": new_item_id,
        "user_id": user_id,
        "type": item_type,
        "title": title,
        "category": category,
        "description": description,
        "serial_tag": serial_tag,
        "loc_id": loc_id,
        "location_name": next((l["name"] for l in get_locations() if l["loc_id"] == loc_id), "Unknown"),
        "cluster_root_id": cluster_root or new_item_id,
        "item_weight": item_weight,
        "priority_value": priority_value,
        "deadline_hours": deadline_hours,
        "status": "OPEN",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # If database is active
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
                (user_id, item_type, title, category, description, serial_tag, loc_id, cluster_root or None, item_weight, priority_value, deadline_hours)
            )
            db.commit()
            new_item["item_id"] = cursor.lastrowid
        except Exception as e:
            current_app.logger.warning(f"DB insert failed, using mock: {e}")
            MOCK_ITEMS.append(new_item)
    else:
        MOCK_ITEMS.append(new_item)

    # 3. Fuzzy LCS + Spatial Candidate Matching (Unit III)
    ranked_candidates, match_telemetries = _match_candidates(new_item, items)
    telemetries.extend(match_telemetries)

    return jsonify({
        "status": "ok",
        "data": {
            "item": new_item,
            "duplicate_detected": is_duplicate,
            "cluster_root_id": cluster_root,
            "candidates": ranked_candidates
        },
        "telemetry": telemetries
    }), 201


def _match_candidates(target_item: dict, all_items: list) -> tuple[list, list]:
    """
    Ranks candidate counter-matches for target_item using LCS text similarity
    and Floyd-Warshall spatial distance.
    Returns (ranked_candidates_list, telemetries_list).
    """
    opposite_type = "FOUND" if target_item["type"] == "LOST" else "LOST"
    target_category = target_item.get("category", "")
    candidates = [
        i for i in all_items 
        if i.get("type") == opposite_type 
        and i.get("category") == target_category
        and i.get("item_id") != target_item.get("item_id")
    ]

    telemetries = []
    if not candidates:
        return [], telemetries

    # Precompute Floyd-Warshall distance matrix if campus edges available
    dist_matrix = None
    try:
        from routes.campus_bp import get_campus_edges
        from algorithms.unit3_dp_bb import all_pairs_shortest_paths
        edges = get_campus_edges()
        apsp_res = all_pairs_shortest_paths(num_nodes=7, edges=edges)
        dist_matrix = apsp_res.get("result", {}).get("dist_matrix")
        telemetries.append(apsp_res.get("telemetry", {}))
    except Exception as e:
        current_app.logger.warning(f"APSP calculation fallback: {e}")

    ranked = []
    lcs_telemetry = None
    target_desc = target_item.get("description", "")
    target_loc = int(target_item.get("loc_id", 1))

    for c in candidates:
        cand_desc = c.get("description", "")
        cand_loc = int(c.get("loc_id", 1))

        # LCS calculation
        sim_ratio = 0.0
        try:
            from algorithms.unit3_dp_bb import compute_lcs_similarity
            lcs_res = compute_lcs_similarity(target_desc, cand_desc)
            sim_ratio = float(lcs_res.get("result", {}).get("similarity_ratio", 0.0))
            if not lcs_telemetry:
                lcs_telemetry = lcs_res.get("telemetry")
        except Exception:
            words_new = set(target_desc.lower().split())
            words_cand = set(cand_desc.lower().split())
            common = words_new.intersection(words_cand)
            sim_ratio = len(common) / max(len(words_new), 1)

        # Spatial distance calculation
        spatial_dist = 0.0
        if dist_matrix and 1 <= target_loc <= len(dist_matrix) and 1 <= cand_loc <= len(dist_matrix):
            d = dist_matrix[target_loc - 1][cand_loc - 1]
            spatial_dist = d if d >= 0.0 else 500.0
        else:
            spatial_dist = 0.0 if target_loc == cand_loc else 200.0

        # Spatial proximity: decays linearly from 1.0 at 0m to 0.0 at 1000m
        spatial_score = max(0.0, 1.0 - (spatial_dist / 1000.0))

        # Composite Confidence: 0.65 * LCS + 0.35 * Spatial Proximity
        confidence = (0.65 * sim_ratio) + (0.35 * spatial_score)

        ranked.append({
            "item": c,
            "lcs_score": round(sim_ratio, 4),
            "spatial_distance_meters": round(spatial_dist, 1),
            "confidence_score": round(confidence, 4)
        })

    if lcs_telemetry:
        telemetries.append(lcs_telemetry)

    # Sort descending by confidence score
    ranked.sort(key=lambda x: -x["confidence_score"])
    return ranked, telemetries


@items_bp.route("/api/items/<int:item_id>/candidates", methods=["GET"])
def api_get_item_candidates(item_id):
    """
    GET /api/items/<item_id>/candidates:
    Calculates dynamic LCS + Floyd-Warshall candidate matches for an item.
    """
    items = get_all_items()
    target_item = next((i for i in items if i["item_id"] == item_id), None)
    if not target_item:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    ranked_candidates, telemetries = _match_candidates(target_item, items)

    return jsonify({
        "status": "ok",
        "data": {
            "item": target_item,
            "candidates": ranked_candidates
        },
        "telemetry": telemetries
    }), 200
