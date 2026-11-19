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
