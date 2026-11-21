import math
from typing import Any, Dict, List
from algorithms.metrics import measure_daa

UNREACHABLE_SENTINEL = -1.0


@measure_daa(
    algorithm="Longest Common Subsequence",
    unit="Unit III",
    complexity="O(m * n)",
    input_size_fn=lambda *args, **kwargs: (
        len(args[0]) + len(args[1])
        if len(args) >= 2
        else len(kwargs.get("text_a", "")) + len(kwargs.get("text_b", ""))
    ),
)
def compute_lcs_similarity(text_a: str, text_b: str) -> Dict[str, Any]:
    if not isinstance(text_a, str) or not isinstance(text_b, str):
        raise TypeError("Both text_a and text_b must be strings.")

    m = len(text_a)
    n = len(text_b)

    if m == 0 and n == 0:
        return {"lcs_length": 0, "similarity_ratio": 1.0}
    if m == 0 or n == 0:
        return {"lcs_length": 0, "similarity_ratio": 0.0}

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        char_a = text_a[i - 1]
        for j in range(1, n + 1):
            if char_a == text_b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                top = dp[i - 1][j]
                left = dp[i][j - 1]
                dp[i][j] = top if top >= left else left

    lcs_length = dp[m][n]
    similarity_ratio = (2.0 * lcs_length) / (m + n)

    return {
        "lcs_length": lcs_length,
        "similarity_ratio": similarity_ratio,
    }


@measure_daa(
    algorithm="Floyd-Warshall",
    unit="Unit III",
    complexity="O(V^3)",
    input_size_fn=lambda *args, **kwargs: args[0] if args else kwargs.get("num_nodes", 0),
)
def all_pairs_shortest_paths(num_nodes: int, edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(num_nodes, int) or isinstance(num_nodes, bool) or num_nodes < 0:
        raise ValueError(f"num_nodes must be a non-negative integer, got {num_nodes!r}")

    if not isinstance(edges, list):
        raise ValueError(f"edges must be a list, got {type(edges).__name__}")

    if num_nodes == 0:
        return {"dist_matrix": []}

    dist = [[float("inf")] * num_nodes for _ in range(num_nodes)]
    for i in range(num_nodes):
        dist[i][i] = 0.0

    for idx, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise ValueError(f"Edge at index {idx} must be a dictionary, got {type(edge).__name__}")

        for field in ("src_loc_id", "dst_loc_id", "distance_meters"):
            if field not in edge:
                raise ValueError(f"Edge at index {idx} missing required field '{field}'")

        u = edge["src_loc_id"]
        v = edge["dst_loc_id"]
        if not isinstance(u, int) or isinstance(u, bool) or not isinstance(v, int) or isinstance(v, bool):
            raise ValueError(f"Edge endpoints must be integers, got: src={u!r}, dst={v!r}")

        if u < 1 or u > num_nodes or v < 1 or v > num_nodes:
            raise ValueError(f"Edge endpoint out of range [1, {num_nodes}]: src={u}, dst={v}")

        w = edge["distance_meters"]
        if isinstance(w, bool) or not isinstance(w, (int, float)):
            raise ValueError(f"distance_meters must be a numeric value, got {w!r}")

        weight = float(w)
        if not math.isfinite(weight) or weight < 0:
            raise ValueError(f"distance_meters must be a non-negative finite number, got {weight}")

        u_idx = u - 1
        v_idx = v - 1
        if weight < dist[u_idx][v_idx]:
            dist[u_idx][v_idx] = weight
            dist[v_idx][u_idx] = weight

    for k in range(num_nodes):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    dist_matrix = [
        [UNREACHABLE_SENTINEL if dist[i][j] == float("inf") else float(dist[i][j]) for j in range(num_nodes)]
        for i in range(num_nodes)
    ]

    return {"dist_matrix": dist_matrix}


@measure_daa(
    algorithm="0/1 Knapsack",
    unit="Unit III",
    complexity="O(n * W)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("items", [])),
)
def optimize_vault_packing(items: List[Dict[str, Any]], capacity: int) -> Dict[str, Any]:
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
        raise ValueError(f"capacity must be a non-negative integer, got {capacity!r}")

    if not isinstance(items, list):
        raise ValueError(f"items must be a list, got {type(items).__name__}")

    seen_ids = set()
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {idx} must be a dictionary, got {type(item).__name__}")

        for field in ("item_id", "item_weight", "priority_value"):
            if field not in item:
                raise ValueError(f"Item at index {idx} missing required field '{field}'")

        item_id = item["item_id"]
        if not isinstance(item_id, int) or isinstance(item_id, bool):
            raise ValueError(f"item_id must be an integer, got {item_id!r} at index {idx}")

        if item_id in seen_ids:
            raise ValueError(f"Duplicate item_id {item_id} found at index {idx}")
        seen_ids.add(item_id)

        weight = item["item_weight"]
        if not isinstance(weight, int) or isinstance(weight, bool) or weight < 0:
            raise ValueError(f"item_weight must be a non-negative integer, got {weight!r} at index {idx}")

        priority = item["priority_value"]
        if not isinstance(priority, int) or isinstance(priority, bool) or priority < 0:
            raise ValueError(f"priority_value must be a non-negative integer, got {priority!r} at index {idx}")

    n = len(items)
    W = capacity

    if n == 0:
        return {"selected_item_ids": [], "max_value": 0}

    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        item = items[i - 1]
        w_i = item["item_weight"]
        v_i = item["priority_value"]
        for w in range(W + 1):
            if w < w_i:
                dp[i][w] = dp[i - 1][w]
            else:
                exclude_val = dp[i - 1][w]
                include_val = dp[i - 1][w - w_i] + v_i
                dp[i][w] = include_val if include_val > exclude_val else exclude_val

    selected_item_ids: List[int] = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            item = items[i - 1]
            selected_item_ids.append(item["item_id"])
            w -= item["item_weight"]

    selected_item_ids.sort()

    return {
        "selected_item_ids": selected_item_ids,
        "max_value": dp[n][W],
    }


def _tsp_input_size(*args: Any, **kwargs: Any) -> int:
    if len(args) >= 2:
        locs = args[1]
    else:
        locs = kwargs.get("active_locs", [])
    try:
        return len(locs)
    except Exception:
        return 0


@measure_daa(
    algorithm="TSP (Branch and Bound)",
    unit="Unit III",
    complexity="O(n! * n^2) worst case",
    input_size_fn=_tsp_input_size,
)
def optimize_collection_tour(
    dist_matrix: List[List[float]],
    active_locs: List[int],
) -> Dict[str, Any]:
    if not isinstance(dist_matrix, list):
        raise ValueError(f"dist_matrix must be a list of lists, got {type(dist_matrix).__name__}")

    if not isinstance(active_locs, list):
        raise ValueError(f"active_locs must be a list, got {type(active_locs).__name__}")

    M = len(dist_matrix)

    if M == 0 and len(active_locs) > 0:
        raise ValueError("Cannot process active locations on an empty distance matrix")

    for row_idx, row in enumerate(dist_matrix):
        if not isinstance(row, list) or len(row) != M:
            raise ValueError(f"Row {row_idx} of dist_matrix is not a list of length {M}")

    matrix: List[List[float]] = [[0.0] * M for _ in range(M)]
    for i in range(M):
        diag = dist_matrix[i][i]
        if isinstance(diag, bool) or not isinstance(diag, (int, float)):
            raise ValueError(f"Diagonal entry at ({i}, {i}) must be numeric, got {diag!r}")
        if abs(float(diag)) > 1e-6:
            raise ValueError(f"Diagonal entry at ({i}, {i}) must be 0.0, got {diag}")
        matrix[i][i] = 0.0

        for j in range(i + 1, M):
            val_ij = dist_matrix[i][j]
            val_ji = dist_matrix[j][i]

            if isinstance(val_ij, bool) or not isinstance(val_ij, (int, float)):
                raise ValueError(f"Entry at ({i}, {j}) must be numeric, got {val_ij!r}")
            if isinstance(val_ji, bool) or not isinstance(val_ji, (int, float)):
                raise ValueError(f"Entry at ({j}, {i}) must be numeric, got {val_ji!r}")

            w_ij = float(val_ij)
            w_ji = float(val_ji)

            if not math.isfinite(w_ij) or not math.isfinite(w_ji):
                raise ValueError(f"Non-finite distance at ({i}, {j}) or ({j}, {i}): {w_ij}, {w_ji}")

            if w_ij == -1.0 or w_ji == -1.0:
                if w_ij != -1.0 or w_ji != -1.0:
                    raise ValueError(f"Asymmetric reachability at ({i}, {j}): {w_ij} vs {w_ji}")
                matrix[i][j] = UNREACHABLE_SENTINEL
                matrix[j][i] = UNREACHABLE_SENTINEL
            else:
                if w_ij < 0.0 or w_ji < 0.0:
                    raise ValueError(f"Negative distance other than -1.0 at ({i}, {j}): {w_ij}, {w_ji}")
                if abs(w_ij - w_ji) > 1e-6:
                    raise ValueError(f"dist_matrix not symmetric within 1e-6: ({i},{j})={w_ij} vs ({j},{i})={w_ji}")
                avg_w = (w_ij + w_ji) / 2.0
                matrix[i][j] = avg_w
                matrix[j][i] = avg_w

    seen_locs = set()
    for loc in active_locs:
        if isinstance(loc, bool) or not isinstance(loc, int):
            raise ValueError(f"Active location ID must be an integer, got {loc!r}")
        if loc < 1 or loc > M:
            raise ValueError(f"Active location ID {loc} out of valid range [1, {M}]")
        if loc in seen_locs:
            raise ValueError(f"Duplicate active location ID {loc} in active_locs")
        seen_locs.add(loc)

    k = len(active_locs)
    if k == 0:
        return {"tour": [], "total_distance": 0.0}

    if k == 1:
        return {"tour": [active_locs[0]], "total_distance": 0.0}

    if k == 2:
        u = active_locs[0]
        v = active_locs[1]
        edge_dist = matrix[u - 1][v - 1]
        if edge_dist < 0.0:
            return {"tour": [], "total_distance": UNREACHABLE_SENTINEL}
        return {"tour": [u, v, u], "total_distance": float(round(2.0 * edge_dist, 6))}

    start = active_locs[0]

    def _dist(u_loc: int, v_loc: int) -> float:
        return matrix[u_loc - 1][v_loc - 1]

    # Nearest-neighbor initial upper bound
    nn_tour = [start]
    nn_visited = {start}
    curr = start
    nn_cost = 0.0
    nn_valid = True

    for _ in range(k - 1):
        best_cand = None
        best_d = float("inf")
        for cand in active_locs:
            if cand not in nn_visited:
                d = _dist(curr, cand)
                if d >= 0.0 and d < best_d:
                    best_d = d
                    best_cand = cand
        if best_cand is None:
            nn_valid = False
            break
        nn_tour.append(best_cand)
        nn_visited.add(best_cand)
        nn_cost += best_d
        curr = best_cand

    if nn_valid:
        ret_d = _dist(curr, start)
        if ret_d >= 0.0:
            nn_tour.append(start)
            nn_cost += ret_d
        else:
            nn_valid = False

    best_cost: float = nn_cost if nn_valid else float("inf")
    best_tour: List[int] = nn_tour if nn_valid else []

    def _calc_lower_bound(curr_loc: int, unvisited_nodes: set) -> float:
        if not unvisited_nodes:
            d = _dist(curr_loc, start)
            return d if d >= 0.0 else float("inf")

        min_exit = float("inf")
        for cand in unvisited_nodes:
            d = _dist(curr_loc, cand)
            if d >= 0.0 and d < min_exit:
                min_exit = d
        if min_exit == float("inf"):
            return float("inf")

        sum_depart = 0.0
        for u_node in unvisited_nodes:
            min_dep = float("inf")
            target_pool = (unvisited_nodes - {u_node}) | {start}
            for v_node in target_pool:
                d = _dist(u_node, v_node)
                if d >= 0.0 and d < min_dep:
                    min_dep = d
            if min_dep == float("inf"):
                return float("inf")
            sum_depart += min_dep

        return min_exit + sum_depart

    def _search(curr_loc: int, unvisited_nodes: set, current_cost: float, current_path: List[int]) -> None:
        nonlocal best_cost, best_tour

        if not unvisited_nodes:
            ret_d = _dist(curr_loc, start)
            if ret_d >= 0.0:
                total_dist = current_cost + ret_d
                complete_tour = current_path + [start]
                if total_dist < best_cost - 1e-9:
                    best_cost = total_dist
                    best_tour = complete_tour
                elif abs(total_dist - best_cost) <= 1e-9:
                    if not best_tour or complete_tour < best_tour:
                        best_tour = complete_tour
                        best_cost = total_dist
            return

        lb_rem = _calc_lower_bound(curr_loc, unvisited_nodes)
        if lb_rem == float("inf") or current_cost + lb_rem > best_cost + 1e-9:
            return
        if current_cost + lb_rem >= best_cost - 1e-9 and best_tour:
            if current_path > best_tour[:len(current_path)]:
                return

        candidates = []
        for cand in unvisited_nodes:
            edge_d = _dist(curr_loc, cand)
            if edge_d < 0.0:
                continue
            cand_unvisited = unvisited_nodes - {cand}
            if not cand_unvisited:
                ret = _dist(cand, start)
                cand_lb = current_cost + edge_d + (ret if ret >= 0.0 else float("inf"))
            else:
                cand_lb = current_cost + edge_d + _calc_lower_bound(cand, cand_unvisited)

            if cand_lb <= best_cost + 1e-9:
                if cand_lb >= best_cost - 1e-9 and best_tour:
                    if (current_path + [cand]) > best_tour[:len(current_path) + 1]:
                        continue
                candidates.append((cand_lb, cand, edge_d))

        candidates.sort(key=lambda item: (item[0], item[1]))

        for cand_lb, cand, edge_d in candidates:
            if cand_lb > best_cost + 1e-9:
                continue
            if cand_lb >= best_cost - 1e-9 and best_tour:
                if (current_path + [cand]) > best_tour[:len(current_path) + 1]:
                    continue
            _search(cand, unvisited_nodes - {cand}, current_cost + edge_d, current_path + [cand])

    initial_unvisited = set(active_locs) - {start}
    _search(start, initial_unvisited, 0.0, [start])

    if best_cost == float("inf") or not best_tour:
        return {"tour": [], "total_distance": UNREACHABLE_SENTINEL}

    return {
        "tour": best_tour,
        "total_distance": float(round(best_cost, 6)),
    }
