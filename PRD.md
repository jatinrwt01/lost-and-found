Product Requirements Document (PRD): Smart Lost & Found Management Portal

AI Coding Assistant & Developer Context Header

Project: Smart Lost & Found Management Portal (Design & Analysis of Algorithms — Units I–IV)

Stack: Python 3.11+ (Flask 3.x), SQLite 3 (WAL mode), Vanilla HTML5, CSS3, JavaScript (ES6+), HTML5 Canvas

Team Topology: 2 Developers working simultaneously (Developer 1: Anshu Kala and Developer 2: Team Partner)

Critical Rule for AI Assistants: Do not modify files outside the active developer's ownership boundary listed in Section 3. Never alter frozen Python function signatures or REST JSON schemas in Section 5 without updating both sides of the contract.

1. Product Overview & Objectives

1.1 Problem Statement

Traditional campus lost-and-found systems rely on manual registers or unstructured notice boards, leading to duplicate reports, slow text searches, suboptimal item-to-claimant pairing, and scheduling bottlenecks at verification desks.

1.2 Product Vision

Build an end-to-end, full-stack web application that automates lost-and-found reporting, duplicate detection, fuzzy text/spatial matching, global optimal pairing, conflict-free handover scheduling, and security collection routing—powered entirely by pure-Python implementations of Design and Analysis of Algorithms (DAA) syllabus concepts (Units I–IV) with live runtime telemetry.

1.3 Core Engineering Constraints

Zero Black-Box Algorithm Libraries: All syllabus algorithms (sorting, DSU, Dijkstra, Kruskal, Graph Colouring, LCS, Floyd-Warshall, 0/1 Knapsack, TSP Branch & Bound, KMP, Rabin-Karp, Ford-Fulkerson, Bitonic Sort) must be written from scratch in Python inside algorithms/ using only standard built-in modules (heapq, collections, math, time). Do not use networkx, scipy, or external graph/string-matching packages.

Simultaneous Conflict-Free Development: Both team members must be able to write, commit, and push code concurrently every day without touching the same files or breaking each other's local runtime.

Live Algorithmic Telemetry: Every API call executing a DAA algorithm must return execution metrics (algorithm, unit, input_size, time_ms, theoretical_complexity) rendered in a collapsible UI telemetry drawer.

2. Parallel Team Work Distribution

Work is split vertically along a strict Engine-vs-Interface boundary so neither developer is ever blocked waiting for the other:

Developer 1 (Jatin Rawat) — Algorithm Engine, Database & Benchmarking:

Designs and maintains schema.sql, database/db.py, and deterministic seed scripts (database/seed.py).

Implements all Unit I–IV algorithms in algorithms/ with @measure_daa timing wrappers.

Builds automated empirical stress tests and complexity benchmark datasets (tests/benchmark_runner.py).

Developer 2 (Anshu Kala) — Flask Blueprints, REST APIs, Frontend UI & Canvas Map:

Builds the modular Flask application factory (app.py) and isolated route Blueprints (routes/).

Develops all Jinja2 HTML templates (templates/), responsive CSS (static/css/), and Vanilla JS API controllers (static/js/).

3. Zero-Conflict Project Architecture & File Ownership

To eliminate Git merge conflicts, the project uses Flask Blueprints and strict single-owner file isolation. Each file has exactly one primary owner.

Plaintext

smart-lost-found/├── .gitignore                  # [SHARED - FROZEN] Excludes *.db, *.db-wal, *.db-shm, __pycache__, .env├── .gitattributes              # [SHARED - FROZEN] Enforces LF line endings across Windows/Linux/WSL├── PRD.md                      # [SHARED - FROZEN] This specification document├── config.py                   # [SHARED - FROZEN] App config & MOCK_MODE toggle├── app.py                      # [DEV 2 - FROZEN AFTER INIT] Flask app factory & Blueprint registration│├── database/                   # [EXCLUSIVE OWNER: DEVELOPER 1]│   ├── __init__.py│   ├── schema.sql              # DDL for users, locations, campus_edges, items, matches│   ├── db.py                   # SQLite connection helper (WAL mode + foreign keys)│   └── seed.py                 # Populates 10 campus nodes, weighted edges, and 30 test items│├── algorithms/                 # [EXCLUSIVE OWNER: DEVELOPER 1]│   ├── __init__.py             # Frozen public exports consumed by Developer 2's routes│   ├── metrics.py              # @measure_daa decorator using time.perf_counter()│   ├── unit1_basics.py         # Merge Sort, Quick Sort, Binary Search, Disjoint Set (DSU)│   ├── unit2_greedy_bt.py      # Dijkstra, Kruskal MST, Job Sequencing, Graph Colouring│   ├── unit3_dp_bb.py          # LCS, Floyd-Warshall, 0/1 Knapsack, TSP (Branch & Bound)│   └── unit4_str_flow.py       # KMP, Rabin-Karp, Ford-Fulkerson (Max Bipartite), Bitonic Sort│├── routes/                     # [EXCLUSIVE OWNER: DEVELOPER 2]│   ├── __init__.py│   ├── auth_bp.py              # /auth/* (login, register, logout, session guard)│   ├── items_bp.py             # /api/items/*, /api/search, /api/matches/*│   ├── admin_bp.py             # /api/admin/* (bipartite match, job queue, slot colouring, knapsack)│   └── campus_bp.py            # /api/campus/* (dijkstra route, kruskal mst, tsp tour, benchmarks)│├── templates/                  # [EXCLUSIVE OWNER: DEVELOPER 2]│   ├── base.html               # Navbar, flash alerts, collapsible DAA Telemetry Drawer│   ├── index.html              # Public Lost & Found feed + KMP/Rabin-Karp/Binary Search bar│   ├── report.html             # Submit Lost/Found item + live DSU duplicate warning│   ├── admin.html              # Admin verification suite (Bipartite Match, Job Queue, Slot Graph)│   ├── campus_map.html         # Interactive Canvas map for Dijkstra, Kruskal MST & TSP routes│   └── benchmarks.html         # Empirical runtime charts (Unit I–IV complexity verification)│├── static/                     # [EXCLUSIVE OWNER: DEVELOPER 2]│   ├── css/style.css           # Unified layout, tables, cards, and telemetry bar styles│   └── js/│       ├── api.js              # Fetch wrapper that automatically updates Telemetry Drawer│       ├── feed.js             # Search, sorting toggle (Merge/Quick/Bitonic), match modal│       ├── admin.js            # Admin optimization triggers & slot calendar rendering│       └── canvas_map.js       # HTML5 Canvas renderer for campus graph overlays│└── tests/                      # [EXCLUSIVE OWNER: DEVELOPER 1]    ├── test_algorithms.py      # Unit tests verifying correctness & edge cases for Units I–IV    └── benchmark_runner.py     # Generates N=10..500 timing JSON for benchmarks.html

AI & Developer Boundary Rules

Never cross-edit directories: Developer 1 never edits routes/, templates/, or static/. Developer 2 never edits database/ or algorithms/.

Decoupled Development via MOCK_MODE: config.py includes MOCK_MODE = False (or True during early frontend work). In routes/, Developer 2 imports functions exclusively from algorithms/__init__.py. If a function is still a stub, algorithms/__init__.py returns valid mock data matching Section 5 contracts so the UI runs end-to-end from Day 1.

4. Database Schema & Concurrency Rules (SQLite)

4.1 Concurrency Configuration (database/db.py)

To prevent sqlite3.OperationalError: database is locked when concurrent Flask requests read/write during demos, get_db() must execute these pragmas on connection setup:

SQL

PRAGMA journal_mode = WAL;PRAGMA synchronous = NORMAL;PRAGMA foreign_keys = ON;PRAGMA busy_timeout = 5000;

Git Rule: Binary SQLite files (*.db, *.db-wal, *.db-shm) are never committed to Git. Each developer runs python -m database.seed locally to generate a clean, identical database.

4.2 Relational Schema (database/schema.sql)

users:

user_id INTEGER PRIMARY KEY AUTOINCREMENT

name TEXT NOT NULL

roll_no TEXT UNIQUE NOT NULL

email TEXT UNIQUE NOT NULL

password_hash TEXT NOT NULL

role TEXT CHECK(role IN ('student', 'admin')) DEFAULT 'student'

locations (Graph Vertices ):

loc_id INTEGER PRIMARY KEY AUTOINCREMENT

name TEXT UNIQUE NOT NULL (e.g., Main Gate, Central Library, Academic Block A, Canteen, Hostel Complex, Sports Ground, Admin Vault)

x_coord INTEGER NOT NULL (0–800 Canvas X coordinate)

y_coord INTEGER NOT NULL (0–500 Canvas Y coordinate)

campus_edges (Undirected Weighted Edges ):

edge_id INTEGER PRIMARY KEY AUTOINCREMENT

src_loc_id INTEGER REFERENCES locations(loc_id)

dst_loc_id INTEGER REFERENCES locations(loc_id)

distance_meters REAL NOT NULL

items:

item_id INTEGER PRIMARY KEY AUTOINCREMENT

user_id INTEGER REFERENCES users(user_id)

type TEXT CHECK(type IN ('LOST', 'FOUND')) NOT NULL

title TEXT NOT NULL

category TEXT NOT NULL (Electronics, ID/Documents, Keys, Books, Accessories, Other)

description TEXT NOT NULL

serial_tag TEXT (Optional IMEI, roll number, or engraving)

loc_id INTEGER REFERENCES locations(loc_id)

cluster_root_id INTEGER (Populated by DSU to group duplicate reports)

item_weight INTEGER DEFAULT 1 (Used in 0/1 Knapsack locker/bag packing)

priority_value INTEGER DEFAULT 10 (Used in Greedy Job Sequencing & Knapsack)

deadline_hours INTEGER DEFAULT 48 (Used in Greedy Job Sequencing)

status TEXT CHECK(status IN ('OPEN', 'MATCHED', 'CLAIMED')) DEFAULT 'OPEN'

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

matches:

match_id INTEGER PRIMARY KEY AUTOINCREMENT

lost_item_id INTEGER REFERENCES items(item_id)

found_item_id INTEGER REFERENCES items(item_id)

lcs_score REAL NOT NULL

spatial_dist REAL NOT NULL

confidence_score REAL NOT NULL

assigned_slot INTEGER (Time slot ID assigned by Backtracking Graph Colouring)

status TEXT CHECK(status IN ('PENDING', 'APPROVED', 'COLLECTED')) DEFAULT 'PENDING'

5. Frozen Interface Contracts

5.1 Standardized Telemetry Envelope

Every function exported in algorithms/__init__.py must return a dictionary with this exact structure:

JSON

{  "result": "<algorithm_specific_payload>",  "telemetry": {    "algorithm": "Knuth-Morris-Pratt (KMP)",    "unit": "Unit IV",    "input_size": 128,    "time_ms": 0.42,    "complexity": "O(n + m)"  }}

5.2 Frozen Python Function Signatures (algorithms/__init__.py)

Developer 1 implements these exact signatures; Developer 2 calls them inside routes/:

Module

Function Signature

Expected result Payload

unit1_basics.py

cluster_duplicate_items(items: list[dict]) -> dict

{"clusters": {root_id: [item_ids...]}, "duplicate_found": bool}

unit1_basics.py

sort_items(items: list[dict], key: str, method: str = "merge") -> dict

Sorted list[dict] (method in {"merge", "quick"})

unit1_basics.py

binary_search_item_id(sorted_items: list[dict], target_id: int) -> dict

Matched item dict or None

unit2_greedy_bt.py

shortest_campus_path(edges: list[dict], start_loc: int, end_loc: int) -> dict

{"path": [loc_ids...], "total_meters": float} (Dijkstra)

unit2_greedy_bt.py

compute_dropbox_mst(num_nodes: int, edges: list[dict]) -> dict

{"mst_edges": [edge_dicts...], "total_cable_or_walk_meters": float} (Kruskal)

unit2_greedy_bt.py

schedule_urgent_claims(claims: list[dict]) -> dict

{"scheduled_claims": [claim_dicts...], "total_priority_saved": int} (Greedy Job Sequencing)

unit2_greedy_bt.py

assign_conflict_free_slots(matches: list[dict]) -> dict

{"slot_assignments": {match_id: slot_int}, "chromatic_number": int} (Graph Colouring)

unit3_dp_bb.py

compute_lcs_similarity(text_a: str, text_b: str) -> dict

{"lcs_length": int, "similarity_ratio": float}

unit3_dp_bb.py

all_pairs_shortest_paths(num_nodes: int, edges: list[dict]) -> dict

{"dist_matrix": list[list[float]]} (Floyd-Warshall)

unit3_dp_bb.py

optimize_vault_packing(items: list[dict], capacity: int) -> dict

{"selected_item_ids": list[int], "max_value": int} (0/1 Knapsack)

unit3_dp_bb.py

optimize_collection_tour(dist_matrix: list[list[float]], active_locs: list[int]) -> dict

{"tour": list[int], "total_distance": float} (TSP Branch & Bound)

unit4_str_flow.py

kmp_search_items(items: list[dict], pattern: str) -> dict

Filtered list[dict] matching pattern without backtracking

unit4_str_flow.py

rabin_karp_watchlist_scan(text: str, watchlist: list[str]) -> dict

{"flagged": bool, "matched_patterns": list[str]}

unit4_str_flow.py

global_bipartite_match(lost_items: list[dict], found_items: list[dict], score_matrix: dict) -> dict

{"pairs": [{"lost_id": int, "found_id": int, "score": float}], "max_matches": int} (Ford-Fulkerson)

unit4_str_flow.py

bitonic_sort_scores(candidates: list[dict]) -> dict

Power-of-2 padded and sorted list[dict]

5.3 Frozen REST API Endpoints (routes/)

All /api/* endpoints return JSON: { "status": "ok", "data": ..., "telemetry": [...] }.

POST /api/items/report — Runs rabin_karp_watchlist_scan + cluster_duplicate_items (DSU) + compute_lcs_similarity + all_pairs_shortest_paths (Floyd-Warshall) + sort_items (Merge Sort) to insert an item and return ranked candidate matches.

GET /api/items/search?q=...&mode=kmp|binary&sort=merge|quick|bitonic — Searches and sorts active items.

POST /api/admin/bipartite-match — Runs global_bipartite_match (Ford-Fulkerson / Edmonds-Karp) across all OPEN lost and found items.

POST /api/admin/schedule-handovers — Runs schedule_urgent_claims (Greedy Job Sequencing) followed by assign_conflict_free_slots (Backtracking Graph Colouring).

POST /api/admin/vault-pack — Runs optimize_vault_packing (0/1 Knapsack) for security collection bag/locker capacity .

GET /api/campus/route?src=1&dst=5 — Runs shortest_campus_path (Dijkstra).

GET /api/campus/network — Runs compute_dropbox_mst (Kruskal) and optimize_collection_tour (TSP Branch & Bound) for active drop-boxes.

GET /api/benchmarks — Serves empirical runtime metrics across .

6. Functional Requirements & DAA Syllabus Mapping

Requirement ID

Feature Description

Syllabus Algorithm (Unit)

Complexity Target

FR-01

Duplicate Report Clustering: Automatically detect if a newly submitted item matches an existing open report at the same location and merge them into an equivalence set.

Disjoint Set Union with path compression & union by rank (Unit I)

 amortized

FR-02

Multi-Mode Feed Sorting: Allow users to sort feed items by urgency, timestamp, or match confidence using Merge Sort (stable), Quick Sort (in-place), or Bitonic Sorting Network ( padded batches).

Merge Sort, Quick Sort (Unit I); Bitonic Sorting Network (Unit IV)

 / 

FR-03

Exact ID & Keyword Lookup: Support  lookup by item_id and linear-time exact substring/serial search without character backtracking.

Binary Search (Unit I); Knuth-Morris-Pratt (Unit IV)

 / 

FR-04

Watchlist & Spam Screening: Scan incoming descriptions against blocked spam keywords and high-value serial watchlists simultaneously via rolling hashes.

Rabin-Karp Algorithm (Unit IV)

 average

FR-05

Fuzzy Text + Spatial Confidence Scoring: Score LOST vs. FOUND pairs using normalized LCS text similarity combined with Floyd-Warshall all-pairs shortest campus distance.

Longest Common Subsequence & Floyd-Warshall (Unit III)

 & 

FR-06

Global Optimal Item Pairing: Prevent greedy mismatching when multiple similar items exist by solving a flow network from Source  Lost  Found  Sink.

Ford-Fulkerson / Edmonds-Karp Maximum Bipartite Matching (Unit IV)

FR-07

Urgent Claim Prioritization: Order pending verification claims with strict expiry deadlines to maximize recovered priority value.

Greedy Job Sequencing with Deadlines (Unit II)

FR-08

Conflict-Free Handover Desk Scheduling: Assign minimum handover time slots to approved matches where two matches share an edge if they involve the same student or admin verifier.

Backtracking: Graph Colouring (Unit II)

 pruned

FR-09

Security Drop-Box Patrol & Locker Packing: Compute shortest claimant walking directions, minimum campus drop-box network, optimal round-trip collection tour, and capacity-bounded bag packing.

Dijkstra & Kruskal MST (Unit II); 0/1 Knapsack & TSP Branch & Bound (Unit III)

, , 

7. Phased Parallel Execution Plan (14-Day Sprint)

Phase

Developer 1 (database/, algorithms/, tests/)

Developer 2 (routes/, templates/, static/)

Integration Milestone

Phase 1

(Days 1–3) | Write schema.sql, db.py (WAL mode), and seed.py. Implement metrics.py and unit1_basics.py (Merge, Quick, Binary Search, DSU). | Scaffold app.py, auth_bp.py, base.html, index.html, report.html, and api.js using MOCK_MODE=True. | Both run python app.py locally with seeded SQLite DB and verify mock UI flows. | | Phase 2

(Days 4–7) | Implement unit3_dp_bb.py (LCS, Floyd-Warshall) and unit4_str_flow.py (KMP, Rabin-Karp). Write unit tests in test_algorithms.py. | Wire items_bp.py to live Unit I, III, and IV search/matching functions. Build the collapsible DAA Telemetry Drawer in base.html. | Flip MOCK_MODE=False for item reporting, duplicate detection, and live search. | | Phase 3

(Days 8–11) | Implement unit2_greedy_bt.py (Dijkstra, Kruskal, Job Sequencing, Graph Colouring) and remaining Unit III/IV (Knapsack, TSP, Ford-Fulkerson, Bitonic). | Build admin.html + admin_bp.py (Bipartite Match, Job Queue, Slot Graph) and campus_map.html + canvas_map.js (HTML5 Canvas path/MST/TSP overlays). | Full end-to-end admin verification and interactive campus route visualization working live. | | Phase 4

(Days 12–14) | Run benchmark_runner.py ($N = 10 \dots 500$) contrasting polynomial vs. NP-hard runtimes and Naive vs. KMP/RK search. | Build benchmarks.html charts displaying empirical curves vs. Big- bounds; polish responsive UI and edge-case alerts. | Final freeze, full end-to-end walkthrough, and DAA viva preparation. |

8. Git Branching, Rebase & Conflict-Prevention Protocol

Both developers must follow these five rules so commits merge cleanly without conflicts:

Isolated Branch Naming:

Developer 1 always works on branches prefixed with dev1/ (e.g., dev1/unit1-sorting-dsu, dev1/unit3-lcs-floyd).

Developer 2 always works on branches prefixed with dev2/ (e.g., dev2/items-blueprint, dev2/canvas-campus-map).

Never commit directly to main.

Short-Lived Branches & Daily Rebase:

Keep feature branches small (1–2 days max) and merge via Pull Request once tested.

Before starting work or opening a PR, synchronize with main using rebase:

Bash

git checkout maingit pull origin maingit checkout dev1/your-branchgit rebase main

Never Commit Runtime Artifacts:

Ensure .gitignore includes *.db, *.db-wal, *.db-shm, __pycache__/, .venv/, and .DS_Store. Committing binary SQLite files guarantees unresolvable binary merge conflicts.

Uniform Formatting & Line Endings:

Use 4 spaces for Python, HTML, and JS indentation, and enforce LF line endings in .gitattributes (* text=auto eol=lf) so Windows/WSL vs. Linux commits never generate artificial whitespace diffs.

Contract Change Protocol:

If either developer needs an extra field in a JSON response or function signature, update PRD.md and algorithms/__init__.py in a dedicated 1-file PR on main first, then rebase both feature branches onto main.