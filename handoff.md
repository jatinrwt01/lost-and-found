# Developer 2 (Anshu Kala) ➔ Developer 1 (Jatin Rawat) Technical Handoff

> **Document Purpose**: This document provides Developer 1 with full technical context on Developer 2's completed presentation, routing, and UI implementation. It outlines file boundaries, integration contracts, SQLite expectations, and step-by-step instructions to prevent Git merge conflicts.

---

## 1. Executive Summary & Git Branch Status

Developer 2 has completed and fully verified **Phases 1, 2, and 3** of the PRD. The application is completely functional with high-fidelity fallback stubs matching the frozen Section 5 PRD contracts.

* **Latest Active Branch**: `dev2/phase3-admin-map` (Contains all work from Phases 1, 2, and 3)
* **GitHub Remote Repository**: `https://github.com/jatinrwt01/lost-and-found.git`
* **Pull Request**: [dev2/phase3-admin-map PR](https://github.com/jatinrwt01/lost-and-found/pull/new/dev2/phase3-admin-map)

---

## 2. Zero-Conflict File Boundary Architecture

To guarantee that **zero merge conflicts** occur, strict single-owner file isolation has been enforced:

```
smart-lost-found/
├── .gitignore                  # [SHARED - FROZEN] Excludes *.db, *.db-wal, *.db-shm, __pycache__, .venv
├── .gitattributes              # [SHARED - FROZEN] Enforces LF line endings across Windows/Linux/WSL
├── PRD.md                      # [SHARED - FROZEN] Markdown copy of the PRD specification
├── handoff.md                  # [SHARED] This technical integration guide
├── config.py                   # [SHARED] App config & MOCK_MODE toggle (Defaults to True)
├── requirements.txt            # [SHARED] Python package dependencies (Flask 3.1.3, Jinja2, Werkzeug)
├── app.py                      # [DEV 2 - FROZEN] Flask application factory & Blueprint registration
│
├── database/                   # 🔴 [EXCLUSIVE TO DEVELOPER 1 - DEV 2 DID NOT TOUCH]
│   ├── __init__.py
│   ├── schema.sql              # DDL for users, locations, campus_edges, items, matches
│   ├── db.py                   # SQLite connection helper (WAL mode + foreign keys + busy_timeout)
│   └── seed.py                 # Seeds 7 campus nodes, weighted edges, test users & items
│
├── algorithms/                 # 🔴 [EXCLUSIVE TO DEVELOPER 1 - DEV 2 DID NOT TOUCH]
│   ├── __init__.py             # Frozen public exports consumed by Developer 2's routes
│   ├── metrics.py              # @measure_daa timing decorator using time.perf_counter()
│   ├── unit1_basics.py         # Merge Sort, Quick Sort, Binary Search, Disjoint Set (DSU)
│   ├── unit2_greedy_bt.py      # Dijkstra, Kruskal MST, Job Sequencing, Graph Colouring
│   ├── unit3_dp_bb.py          # LCS, Floyd-Warshall, 0/1 Knapsack, TSP (Branch & Bound)
│   └── unit4_str_flow.py       # KMP, Rabin-Karp, Ford-Fulkerson (Max Flow), Bitonic Sort
│
├── tests/                      # 🔴 [EXCLUSIVE TO DEVELOPER 1 - DEV 2 DID NOT TOUCH]
│   ├── test_algorithms.py      # Unit tests verifying algorithm correctness
│   └── benchmark_runner.py     # Generates N=10..500 timing JSON datasets
│
├── routes/                     # 🟢 [EXCLUSIVE OWNER: DEVELOPER 2]
│   ├── __init__.py             # Exports auth_bp, items_bp, admin_bp, campus_bp
│   ├── auth_bp.py              # /auth/* (login, register, logout, session guards)
│   ├── items_bp.py             # / (feed), /report, /api/items/*, /api/items/search, candidates
│   ├── admin_bp.py             # /admin, /admin/api/bipartite-match, schedule-handovers, vault-pack
│   └── campus_bp.py            # /campus/map, /campus/benchmarks, /campus/api/route, network, benchmarks
│
├── templates/                  # 🟢 [EXCLUSIVE OWNER: DEVELOPER 2]
│   ├── base.html               # Navbar, alerts, persistent DAA Telemetry Drawer with Unit filtering
│   ├── login.html              # Sign-in form with demo student & admin accounts
│   ├── register.html           # Account registration
│   ├── index.html              # Public feed, KMP/Binary search bar, sorting toggle, match modal
│   ├── report.html             # Item report form + live DSU duplicate alert banner + LCS match ranking
│   ├── admin.html              # Admin optimization suite (Bipartite, Job Queue, Knapsack Vault)
│   ├── campus_map.html         # Interactive HTML5 Canvas map (800x500)
│   └── benchmarks.html         # Empirical complexity curves & comparison tables
│
└── static/                     # 🟢 [EXCLUSIVE OWNER: DEVELOPER 2]
    ├── css/style.css           # Responsive modern styling, status pills, dark telemetry drawer
    └── js/
        ├── api.js              # Universal fetch wrapper that updates the DAA Telemetry Drawer
        ├── feed.js             # Live search debouncing, sorting switcher, category filter pills
        ├── admin.js            # Admin optimization triggers, timetable grid, vault capacity
        └── canvas_map.js       # HTML5 Canvas graph renderer with Dijkstra, Kruskal, and TSP overlays
```

---

## 3. How the Decoupled Integration Works (`MOCK_MODE`)

In `routes/items_bp.py`, `routes/admin_bp.py`, and `routes/campus_bp.py`, Developer 2 structured every endpoint with dynamic imports and safe fallbacks:

```python
# Standard pattern used across all routes:
if not current_app.config.get("MOCK_MODE", True):
    try:
        from algorithms import function_name
        res = function_name(...)
    except (ImportError, AttributeError):
        # Graceful fallback to contract-compliant pure Python implementation
        res = _fallback_function_name(...)
```

### How Developer 1 Connects to the UI:
1. Developer 1 builds the algorithm functions in `algorithms/` and exports them in `algorithms/__init__.py`.
2. Developer 1 builds `database/db.py` with `get_db()`.
3. In `config.py` (or by setting environment variable `MOCK_MODE=False`), toggle `MOCK_MODE = False`.
4. Run `python app.py`. All API routes and UI buttons will immediately call Developer 1's live algorithms without needing any changes to Developer 2's code!

---

## 4. Frozen Interface Contract: Expected Signatures & Envelopes

Every algorithm exported in `algorithms/__init__.py` **must return a dictionary** matching this exact standardized envelope:

```python
{
    "result": <algorithm_specific_payload>,
    "telemetry": {
        "algorithm": "Knuth-Morris-Pratt (KMP)",
        "unit": "Unit IV",
        "input_size": 128,
        "time_ms": 0.42,
        "complexity": "O(n + m)"
    }
}
```

### Table of 15 Frozen Functions Consumed by Routes:

| Module | Function Signature | Expected `result` Payload | Calling Route |
| :--- | :--- | :--- | :--- |
| `unit1_basics.py` | `cluster_duplicate_items(items: list[dict]) -> dict` | `{"clusters": {root_id: [item_ids...]}, "duplicate_found": bool}` | `POST /api/items/report` |
| `unit1_basics.py` | `sort_items(items: list[dict], key: str, method: str = "merge") -> dict` | Sorted `list[dict]` (`method` in `{"merge", "quick"}`) | `GET /api/items/search` |
| `unit1_basics.py` | `binary_search_item_id(sorted_items: list[dict], target_id: int) -> dict` | Matched item `dict` or `None` | `GET /api/items/search?mode=binary` |
| `unit2_greedy_bt.py` | `shortest_campus_path(edges: list[dict], start_loc: int, end_loc: int) -> dict` | `{"path": [loc_ids...], "total_meters": float}` | `GET /api/campus/route` |
| `unit2_greedy_bt.py` | `compute_dropbox_mst(num_nodes: int, edges: list[dict]) -> dict` | `{"mst_edges": [edge_dicts...], "total_cable_or_walk_meters": float}` | `GET /api/campus/network` |
| `unit2_greedy_bt.py` | `schedule_urgent_claims(claims: list[dict]) -> dict` | `{"scheduled_claims": [claim_dicts...], "total_priority_saved": int}` | `POST /admin/api/schedule-handovers` |
| `unit2_greedy_bt.py` | `assign_conflict_free_slots(matches: list[dict]) -> dict` | `{"slot_assignments": {match_id: slot_int}, "chromatic_number": int}` | `POST /admin/api/schedule-handovers` |
| `unit3_dp_bb.py` | `compute_lcs_similarity(text_a: str, text_b: str) -> dict` | `{"lcs_length": int, "similarity_ratio": float}` | `POST /api/items/report`, `/candidates` |
| `unit3_dp_bb.py` | `all_pairs_shortest_paths(num_nodes: int, edges: list[dict]) -> dict` | `{"dist_matrix": list[list[float]]}` | `POST /api/items/report`, `/candidates` |
| `unit3_dp_bb.py` | `optimize_vault_packing(items: list[dict], capacity: int) -> dict` | `{"selected_item_ids": list[int], "max_value": int}` | `POST /admin/api/vault-pack` |
| `unit3_dp_bb.py` | `optimize_collection_tour(dist_matrix: list[list[float]], active_locs: list[int]) -> dict` | `{"tour": list[int], "total_distance": float}` | `GET /api/campus/network` |
| `unit4_str_flow.py` | `kmp_search_items(items: list[dict], pattern: str) -> dict` | Filtered `list[dict]` matching pattern without backtracking | `GET /api/items/search?mode=kmp` |
| `unit4_str_flow.py` | `rabin_karp_watchlist_scan(text: str, watchlist: list[str]) -> dict` | `{"flagged": bool, "matched_patterns": list[str]}` | `POST /api/items/report` |
| `unit4_str_flow.py` | `global_bipartite_match(lost_items: list[dict], found_items: list[dict], score_matrix: dict) -> dict` | `{"pairs": [{"lost_id": int, "found_id": int, "score": float}], "max_matches": int}` | `POST /admin/api/bipartite-match` |
| `unit4_str_flow.py` | `bitonic_sort_scores(candidates: list[dict]) -> dict` | Power-of-2 padded and sorted `list[dict]` | `GET /api/items/search?sort=bitonic` |

---

## 5. SQLite Database Integration Contract (`database/db.py`)

When Developer 1 implements `database/db.py`, ensure:
1. `get_db()` returns an active connection with `sqlite3.Row` row factory:
   ```python
   def get_db():
       if "db" not in g:
           g.db = sqlite3.connect(current_app.config["DATABASE"])
           g.db.row_factory = sqlite3.Row
           g.db.execute("PRAGMA journal_mode = WAL;")
           g.db.execute("PRAGMA synchronous = NORMAL;")
           g.db.execute("PRAGMA foreign_keys = ON;")
           g.db.execute("PRAGMA busy_timeout = 5000;")
       return g.db

   def close_db(e=None):
       db = g.pop("db", None)
       if db is not None:
           db.close()
   ```
2. `app.py` already registers `app.teardown_appcontext(close_db)` safely if `close_db` is exported.
3. **Database schema table names and fields expected by `routes/`**:
   - `users`: `user_id`, `name`, `roll_no`, `email`, `password_hash`, `role` ('student' or 'admin')
   - `locations`: `loc_id`, `name`, `x_coord`, `y_coord` (matches $800 \times 500$ canvas coordinates)
   - `campus_edges`: `edge_id`, `src_loc_id`, `dst_loc_id`, `distance_meters`
   - `items`: `item_id`, `user_id`, `type` ('LOST'/'FOUND'), `title`, `category`, `description`, `serial_tag`, `loc_id`, `cluster_root_id`, `item_weight`, `priority_value`, `deadline_hours`, `status`, `created_at`
   - `matches`: `match_id`, `lost_item_id`, `found_item_id`, `lcs_score`, `spatial_dist`, `confidence_score`, `assigned_slot`, `status`

---

## 6. How Developer 1 Should Pull and Work (Conflict-Free Workflow)

To start work without causing conflicts:

```bash
# 1. Fetch the latest branches from GitHub
git fetch origin

# 2. Review and merge Developer 2's PR (dev2/phase3-admin-map) into main, OR rebase:
git checkout main
git pull origin main
git merge origin/dev2/phase3-admin-map

# 3. Create your isolated Developer 1 feature branch (always prefixed with dev1/):
git checkout -b dev1/algorithms-and-db

# 4. Now create and build ONLY within your assigned directories:
#    - database/ (schema.sql, db.py, seed.py)
#    - algorithms/ (metrics.py, unit1_basics.py, unit2_greedy_bt.py, etc.)
#    - tests/ (test_algorithms.py, benchmark_runner.py)

# 5. When ready to test with the live UI, set in config.py or environment:
#    MOCK_MODE = False

# 6. Run the application:
python app.py
```

---

## 7. Developer 2 Verification Tests Already Passing

All routes and fallback DAA pipelines passed automated unit tests with 100% success:
- `GET /`: Status 200 (Feed rendering)
- `GET /auth/login` & `/register`: Status 200 (Session guards)
- `GET /api/items/search`: Status 200 (KMP + Merge Sort telemetries)
- `POST /api/items/report`: Status 201 (Rabin-Karp + DSU duplicate clustering + LCS + Floyd-Warshall)
- `GET /campus/map`: Status 200 (Interactive HTML5 Canvas map)
- `GET /campus/api/route`: Status 200 (Dijkstra Shortest Path)
- `GET /campus/api/network`: Status 200 (Kruskal MST & TSP Branch & Bound)
- `POST /admin/api/bipartite-match`: Status 200 (Ford-Fulkerson Maximum Flow)
- `POST /admin/api/schedule-handovers`: Status 200 (Greedy Job Sequencing & Graph Colouring)
- `POST /admin/api/vault-pack`: Status 200 (0/1 Knapsack DP)
