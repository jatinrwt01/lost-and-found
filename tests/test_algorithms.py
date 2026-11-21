import math
import unittest

from algorithms import (
    all_pairs_shortest_paths,
    assign_conflict_free_slots,
    binary_search_item_id,
    cluster_duplicate_items,
    compute_dropbox_mst,
    compute_lcs_similarity,
    optimize_collection_tour,
    optimize_vault_packing,
    schedule_urgent_claims,
    shortest_campus_path,
    sort_items,
)


class TestUnit1Algorithms(unittest.TestCase):
    def test_merge_sort_basic(self):
        items = [
            {"id": 1, "priority": 25},
            {"id": 2, "priority": 10},
            {"id": 3, "priority": 15},
        ]
        res = sort_items(items, "priority", method="merge")
        self.assertEqual([x["priority"] for x in res["result"]], [10, 15, 25])
        self.assertEqual(res["telemetry"]["algorithm"], "Merge Sort")
        self.assertEqual(res["telemetry"]["unit"], "Unit I")
        self.assertEqual(res["telemetry"]["complexity"], "O(n log n)")
        self.assertEqual(res["telemetry"]["input_size"], 3)

    def test_quick_sort_basic(self):
        items = [
            {"id": 1, "priority": 30},
            {"id": 2, "priority": 5},
            {"id": 3, "priority": 20},
        ]
        res = sort_items(items, "priority", method="quick")
        self.assertEqual([x["priority"] for x in res["result"]], [5, 20, 30])
        self.assertEqual(res["telemetry"]["algorithm"], "Quick Sort")
        self.assertEqual(res["telemetry"]["complexity"], "O(n log n) average case")

    def test_sort_invalid_method(self):
        with self.assertRaises(ValueError):
            sort_items([], "priority", method="bubble")

    def test_binary_search(self):
        items = [
            {"item_id": 10, "title": "Keys"},
            {"item_id": 20, "title": "Phone"},
            {"item_id": 30, "title": "Wallet"},
        ]
        res = binary_search_item_id(items, 20)
        self.assertEqual(res["result"]["title"], "Phone")
        self.assertEqual(res["telemetry"]["algorithm"], "Binary Search")
        self.assertIsNone(binary_search_item_id(items, 99)["result"])
        self.assertIsNone(binary_search_item_id([], 10)["result"])

    def test_cluster_duplicate_items(self):
        items = [
            {"item_id": 1, "status": "OPEN", "loc_id": 1, "type": "LOST", "category": "Electronics", "title": "  Phone "},
            {"item_id": 2, "status": "OPEN", "loc_id": 1, "type": "LOST", "category": "Electronics", "title": "PHONE"},
            {"item_id": 3, "status": "CLAIMED", "loc_id": 1, "type": "LOST", "category": "Electronics", "title": "Phone"},
            {"item_id": 4, "status": "OPEN", "loc_id": None, "type": "LOST", "category": "Electronics", "title": "Phone"},
        ]
        res = cluster_duplicate_items(items)
        self.assertTrue(res["result"]["duplicate_found"])
        clusters = list(res["result"]["clusters"].values())
        self.assertEqual(len(clusters), 1)
        self.assertEqual(sorted(clusters[0]), [1, 2])


class TestUnit2Algorithms(unittest.TestCase):
    def test_dijkstra_shortest_path(self):
        edges = [
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 100.0},
            {"src_loc_id": 2, "dst_loc_id": 3, "distance_meters": 150.0},
            {"src_loc_id": 1, "dst_loc_id": 3, "distance_meters": 300.0},
        ]
        res = shortest_campus_path(edges, 1, 3)
        self.assertEqual(res["result"]["path"], [1, 2, 3])
        self.assertEqual(res["result"]["total_meters"], 250.0)
        self.assertEqual(res["telemetry"]["algorithm"], "Dijkstra's Algorithm")

    def test_dijkstra_identity_and_unreachable(self):
        edges = [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 50.0}]
        self.assertEqual(shortest_campus_path(edges, 1, 1)["result"]["path"], [1])
        self.assertEqual(shortest_campus_path(edges, 1, 1)["result"]["total_meters"], 0.0)
        self.assertEqual(shortest_campus_path(edges, 1, 99)["result"]["total_meters"], -1.0)
        self.assertEqual(shortest_campus_path(edges, 1, 99)["result"]["path"], [])

    def test_dijkstra_invalid_weights(self):
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": -5.0}], 1, 2)
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": float("nan")}], 1, 2)

    def test_dijkstra_boolean_and_endpoint_validation(self):
        # Boolean weights must be rejected
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": True}], 1, 2)
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": False}], 1, 2)
        # Non-numeric weights must be rejected
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": "invalid"}], 1, 2)
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": None}], 1, 2)

        # Boolean endpoints in edges must be rejected
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": True, "dst_loc_id": 2, "distance_meters": 10.0}], 1, 2)
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": False, "distance_meters": 10.0}], 1, 2)

        # Non-integer endpoints in edges must be rejected
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": "1", "dst_loc_id": 2, "distance_meters": 10.0}], 1, 2)
        with self.assertRaises(ValueError):
            shortest_campus_path([{"src_loc_id": 1, "dst_loc_id": 2.5, "distance_meters": 10.0}], 1, 2)

        # Boolean start_loc and end_loc must be rejected
        edges = [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 10.0}]
        with self.assertRaises(ValueError):
            shortest_campus_path(edges, True, 2)
        with self.assertRaises(ValueError):
            shortest_campus_path(edges, 1, False)
        with self.assertRaises(ValueError):
            shortest_campus_path(edges, True, True)

        # Non-integer start_loc and end_loc must be rejected
        with self.assertRaises(ValueError):
            shortest_campus_path(edges, "1", 2)
        with self.assertRaises(ValueError):
            shortest_campus_path(edges, 1, 2.0)
        with self.assertRaises(ValueError):
            shortest_campus_path(edges, None, 2)

    def test_kruskal_mst(self):
        edges = [
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 10.0},
            {"src_loc_id": 2, "dst_loc_id": 3, "distance_meters": 15.0},
            {"src_loc_id": 1, "dst_loc_id": 3, "distance_meters": 20.0},
        ]
        res = compute_dropbox_mst(3, edges)
        self.assertEqual(len(res["result"]["mst_edges"]), 2)
        self.assertEqual(res["result"]["total_cable_or_walk_meters"], 25.0)
        self.assertEqual(res["telemetry"]["algorithm"], "Kruskal's Algorithm")
        self.assertEqual(res["telemetry"]["complexity"], "O(V + E log E)")

    def test_kruskal_validation(self):
        with self.assertRaises(ValueError):
            compute_dropbox_mst(-1, [])
        with self.assertRaises(ValueError):
            compute_dropbox_mst(3, [{"src_loc_id": True, "dst_loc_id": 2, "distance_meters": 10.0}])
        with self.assertRaises(ValueError):
            compute_dropbox_mst(3, [{"src_loc_id": 1, "dst_loc_id": 4, "distance_meters": 10.0}])

    def test_kruskal_boolean_weight(self):
        with self.assertRaises(ValueError):
            compute_dropbox_mst(3, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": True}])
        with self.assertRaises(ValueError):
            compute_dropbox_mst(3, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": False}])
        with self.assertRaises(ValueError):
            compute_dropbox_mst(3, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": "invalid"}])
        with self.assertRaises(ValueError):
            compute_dropbox_mst(3, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": None}])

    def test_kruskal_zero_nodes_with_edges(self):
        # num_nodes == 0 with empty edges returns empty MST
        res = compute_dropbox_mst(0, [])
        self.assertEqual(res["result"]["mst_edges"], [])
        self.assertEqual(res["result"]["total_cable_or_walk_meters"], 0.0)

        # num_nodes == 0 with non-empty edges must be rejected
        with self.assertRaises(ValueError):
            compute_dropbox_mst(0, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 10.0}])

    def test_job_sequencing(self):
        claims = [
            {"claim_id": 1, "priority_value": 50, "deadline_hours": 2},
            {"claim_id": 2, "priority_value": 10, "deadline_hours": 1},
            {"claim_id": 3, "priority_value": 15, "deadline_hours": 2},
            {"claim_id": 4, "priority_value": 30, "deadline_hours": 1},
            {"claim_id": 5, "priority_value": 20, "deadline_hours": 0},
        ]
        res = schedule_urgent_claims(claims)
        self.assertEqual(res["result"]["total_priority_saved"], 80)
        scheduled = res["result"]["scheduled_claims"]
        self.assertEqual(len(scheduled), 2)
        self.assertEqual(scheduled[0]["claim_id"], 4)
        self.assertEqual(scheduled[0]["assigned_slot"], 1)
        self.assertEqual(scheduled[1]["claim_id"], 1)
        self.assertEqual(scheduled[1]["assigned_slot"], 2)
        self.assertEqual(res["telemetry"]["algorithm"], "Greedy Job Sequencing")
        self.assertEqual(res["telemetry"]["complexity"], "O(n^2)")


class TestGraphColoringBacktracking(unittest.TestCase):
    def test_empty_matches(self):
        res = assign_conflict_free_slots([])
        self.assertEqual(res["result"]["slot_assignments"], {})
        self.assertEqual(res["result"]["chromatic_number"], 0)
        self.assertEqual(res["telemetry"]["algorithm"], "Graph Coloring (Backtracking)")
        self.assertEqual(res["telemetry"]["unit"], "Unit II")
        self.assertEqual(res["telemetry"]["complexity"], "O(m^V) pruned")
        self.assertEqual(res["telemetry"]["input_size"], 0)

    def test_single_match(self):
        matches = [{"match_id": 1, "student_id": 101, "admin_id": 1}]
        res = assign_conflict_free_slots(matches)
        self.assertEqual(res["result"]["slot_assignments"], {1: 1})
        self.assertEqual(res["result"]["chromatic_number"], 1)
        self.assertEqual(res["telemetry"]["input_size"], 1)

    def test_no_conflicts_independent_set(self):
        matches = [
            {"match_id": 1, "student_id": 101, "admin_id": 1},
            {"match_id": 2, "student_id": 102, "admin_id": 2},
            {"match_id": 3, "student_id": 103, "admin_id": 3},
        ]
        res = assign_conflict_free_slots(matches)
        self.assertEqual(res["result"]["chromatic_number"], 1)
        self.assertEqual(res["result"]["slot_assignments"], {1: 1, 2: 1, 3: 1})

    def test_all_conflicts_clique(self):
        matches = [
            {"match_id": 1, "student_id": 101, "admin_id": 1},
            {"match_id": 2, "student_id": 101, "admin_id": 2},
            {"match_id": 3, "student_id": 101, "admin_id": 3},
        ]
        res = assign_conflict_free_slots(matches)
        self.assertEqual(res["result"]["chromatic_number"], 3)
        assigned_slots = list(res["result"]["slot_assignments"].values())
        self.assertEqual(sorted(assigned_slots), [1, 2, 3])

    def test_prd_example_scenario(self):
        matches = [
            {"match_id": 1, "student_id": 101, "admin_id": 1},
            {"match_id": 2, "student_id": 102, "admin_id": 1},
            {"match_id": 3, "student_id": 101, "admin_id": 2},
            {"match_id": 4, "student_id": 103, "admin_id": 3},
        ]
        matches_copy = [dict(m) for m in matches]
        res = assign_conflict_free_slots(matches)

        # Non-mutation check
        self.assertEqual(matches, matches_copy)

        slots = res["result"]["slot_assignments"]
        self.assertEqual(res["result"]["chromatic_number"], 2)
        # Match 1 conflicts with Match 2 (admin 1) and Match 3 (student 101)
        self.assertNotEqual(slots[1], slots[2])
        self.assertNotEqual(slots[1], slots[3])
        # All assigned slots must be in 1..chromatic_number
        for s in slots.values():
            self.assertIn(s, [1, 2])

    def test_dual_conflict(self):
        matches = [
            {"match_id": 1, "student_id": 101, "admin_id": 1},
            {"match_id": 2, "student_id": 101, "admin_id": 1},
        ]
        res = assign_conflict_free_slots(matches)
        self.assertEqual(res["result"]["chromatic_number"], 2)
        self.assertNotEqual(res["result"]["slot_assignments"][1], res["result"]["slot_assignments"][2])

    def test_validation_errors(self):
        # Non-list input
        with self.assertRaises(ValueError):
            assign_conflict_free_slots("invalid")

        # Non-dict element
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([1])

        # Missing required field
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([{"match_id": 1, "student_id": 101}])

        # Boolean ID rejection
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([{"match_id": True, "student_id": 101, "admin_id": 1}])
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([{"match_id": 1, "student_id": False, "admin_id": 1}])
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([{"match_id": 1, "student_id": 101, "admin_id": True}])

        # Non-positive ID
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([{"match_id": 0, "student_id": 101, "admin_id": 1}])
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([{"match_id": 1, "student_id": -5, "admin_id": 1}])

        # Duplicate match_id
        with self.assertRaises(ValueError):
            assign_conflict_free_slots([
                {"match_id": 1, "student_id": 101, "admin_id": 1},
                {"match_id": 1, "student_id": 102, "admin_id": 2},
            ])


class TestUnit3Algorithms(unittest.TestCase):
    def test_lcs_both_empty(self):
        res = compute_lcs_similarity("", "")
        self.assertEqual(res["result"]["lcs_length"], 0)
        self.assertEqual(res["result"]["similarity_ratio"], 1.0)
        self.assertEqual(res["telemetry"]["algorithm"], "Longest Common Subsequence")
        self.assertEqual(res["telemetry"]["unit"], "Unit III")
        self.assertEqual(res["telemetry"]["complexity"], "O(m * n)")
        self.assertEqual(res["telemetry"]["input_size"], 0)

    def test_lcs_one_empty(self):
        res_a = compute_lcs_similarity("hello", "")
        self.assertEqual(res_a["result"]["lcs_length"], 0)
        self.assertEqual(res_a["result"]["similarity_ratio"], 0.0)
        self.assertEqual(res_a["telemetry"]["input_size"], 5)

        res_b = compute_lcs_similarity("", "world")
        self.assertEqual(res_b["result"]["lcs_length"], 0)
        self.assertEqual(res_b["result"]["similarity_ratio"], 0.0)
        self.assertEqual(res_b["telemetry"]["input_size"], 5)

    def test_lcs_identical_strings(self):
        res = compute_lcs_similarity("calculator", "calculator")
        self.assertEqual(res["result"]["lcs_length"], 10)
        self.assertEqual(res["result"]["similarity_ratio"], 1.0)
        self.assertEqual(res["telemetry"]["input_size"], 20)

    def test_lcs_case_sensitivity(self):
        res = compute_lcs_similarity("abc", "ABC")
        self.assertEqual(res["result"]["lcs_length"], 0)
        self.assertEqual(res["result"]["similarity_ratio"], 0.0)

    def test_lcs_disjoint_strings(self):
        res = compute_lcs_similarity("abc", "def")
        self.assertEqual(res["result"]["lcs_length"], 0)
        self.assertEqual(res["result"]["similarity_ratio"], 0.0)

    def test_lcs_subsequence(self):
        # LCS of "aggtab" and "gxtxayb" is "gtab" (length 4)
        # Ratio = 2 * 4 / (6 + 7) = 8 / 13
        res = compute_lcs_similarity("aggtab", "gxtxayb")
        self.assertEqual(res["result"]["lcs_length"], 4)
        self.assertAlmostEqual(res["result"]["similarity_ratio"], 8.0 / 13.0)
        self.assertEqual(res["telemetry"]["input_size"], 13)

    def test_lcs_seed_pair(self):
        # "Dell XPS 15 Laptop" (len 18) vs "Dell Laptop" (len 11)
        # LCS is "Dell Laptop" (len 11)
        # Ratio = 2 * 11 / (18 + 11) = 22 / 29
        res = compute_lcs_similarity("Dell XPS 15 Laptop", "Dell Laptop")
        self.assertEqual(res["result"]["lcs_length"], 11)
        self.assertEqual(res["result"]["similarity_ratio"], 22.0 / 29.0)

    def test_lcs_invalid_types(self):
        with self.assertRaises(TypeError):
            compute_lcs_similarity(123, "text")
        with self.assertRaises(TypeError):
            compute_lcs_similarity("text", None)

    def test_floyd_warshall_empty_graph(self):
        res = all_pairs_shortest_paths(0, [])
        self.assertEqual(res["result"]["dist_matrix"], [])
        self.assertEqual(res["telemetry"]["algorithm"], "Floyd-Warshall")
        self.assertEqual(res["telemetry"]["unit"], "Unit III")
        self.assertEqual(res["telemetry"]["complexity"], "O(V^3)")
        self.assertEqual(res["telemetry"]["input_size"], 0)

    def test_floyd_warshall_single_node(self):
        res = all_pairs_shortest_paths(1, [])
        self.assertEqual(res["result"]["dist_matrix"], [[0.0]])
        self.assertEqual(res["telemetry"]["input_size"], 1)

    def test_floyd_warshall_prd_example(self):
        edges = [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 4.0}]
        res = all_pairs_shortest_paths(2, edges)
        expected = [
            [0.0, 4.0],
            [4.0, 0.0],
        ]
        self.assertEqual(res["result"]["dist_matrix"], expected)
        self.assertEqual(res["telemetry"]["input_size"], 2)

    def test_floyd_warshall_multihop_and_relaxation(self):
        edges = [
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 3.0},
            {"src_loc_id": 2, "dst_loc_id": 3, "distance_meters": 5.0},
        ]
        res = all_pairs_shortest_paths(3, edges)
        expected = [
            [0.0, 3.0, 8.0],
            [3.0, 0.0, 5.0],
            [8.0, 5.0, 0.0],
        ]
        self.assertEqual(res["result"]["dist_matrix"], expected)

    def test_floyd_warshall_shortcut(self):
        edges = [
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 10.0},
            {"src_loc_id": 2, "dst_loc_id": 3, "distance_meters": 10.0},
            {"src_loc_id": 1, "dst_loc_id": 3, "distance_meters": 5.0},
        ]
        res = all_pairs_shortest_paths(3, edges)
        expected = [
            [0.0, 10.0, 5.0],
            [10.0, 0.0, 10.0],
            [5.0, 10.0, 0.0],
        ]
        self.assertEqual(res["result"]["dist_matrix"], expected)

    def test_floyd_warshall_disconnected_graph(self):
        edges = [
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 2.5},
            {"src_loc_id": 3, "dst_loc_id": 4, "distance_meters": 6.0},
        ]
        res = all_pairs_shortest_paths(4, edges)
        matrix = res["result"]["dist_matrix"]
        self.assertEqual(matrix[0][1], 2.5)
        self.assertEqual(matrix[1][0], 2.5)
        self.assertEqual(matrix[2][3], 6.0)
        self.assertEqual(matrix[3][2], 6.0)
        self.assertEqual(matrix[0][2], -1.0)
        self.assertEqual(matrix[0][3], -1.0)
        self.assertEqual(matrix[1][2], -1.0)
        self.assertEqual(matrix[1][3], -1.0)
        self.assertEqual(matrix[2][0], -1.0)
        self.assertEqual(matrix[3][0], -1.0)

    def test_floyd_warshall_parallel_edges_keeps_minimum(self):
        edges = [
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 15.0},
            {"src_loc_id": 2, "dst_loc_id": 1, "distance_meters": 4.5},
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 8.0},
        ]
        res = all_pairs_shortest_paths(2, edges)
        self.assertEqual(res["result"]["dist_matrix"], [[0.0, 4.5], [4.5, 0.0]])

    def test_floyd_warshall_self_loop_ignored(self):
        edges = [
            {"src_loc_id": 1, "dst_loc_id": 1, "distance_meters": 10.0},
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 3.0},
        ]
        res = all_pairs_shortest_paths(2, edges)
        self.assertEqual(res["result"]["dist_matrix"], [[0.0, 3.0], [3.0, 0.0]])

    def test_floyd_warshall_preserves_edges_input(self):
        original_edges = [
            {"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": 5.0},
        ]
        edges_copy = [dict(e) for e in original_edges]
        all_pairs_shortest_paths(2, original_edges)
        self.assertEqual(original_edges, edges_copy)

    def test_floyd_warshall_invalid_num_nodes(self):
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(-1, [])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(True, [])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(False, [])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths("3", [])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2.5, [])

    def test_floyd_warshall_invalid_edges_structure(self):
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, "not_a_list")
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, None)
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, ["not_a_dict"])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": 2}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "distance_meters": 4.0}])

    def test_floyd_warshall_invalid_endpoints(self):
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 0, "dst_loc_id": 2, "distance_meters": 4.0}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": 3, "distance_meters": 4.0}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": True, "dst_loc_id": 2, "distance_meters": 4.0}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": "2", "distance_meters": 4.0}])

    def test_floyd_warshall_invalid_weights(self):
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": True}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": "five"}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": -1.0}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": float("inf")}])
        with self.assertRaises(ValueError):
            all_pairs_shortest_paths(2, [{"src_loc_id": 1, "dst_loc_id": 2, "distance_meters": float("nan")}])

    def test_knapsack_empty_items(self):
        res = optimize_vault_packing([], 10)
        self.assertEqual(res["result"]["selected_item_ids"], [])
        self.assertEqual(res["result"]["max_value"], 0)
        self.assertEqual(res["telemetry"]["algorithm"], "0/1 Knapsack")
        self.assertEqual(res["telemetry"]["unit"], "Unit III")
        self.assertEqual(res["telemetry"]["complexity"], "O(n * W)")
        self.assertEqual(res["telemetry"]["input_size"], 0)

    def test_knapsack_zero_capacity(self):
        items = [{"item_id": 1, "item_weight": 5, "priority_value": 20}]
        res = optimize_vault_packing(items, 0)
        self.assertEqual(res["result"]["selected_item_ids"], [])
        self.assertEqual(res["result"]["max_value"], 0)
        self.assertEqual(res["telemetry"]["input_size"], 1)

    def test_knapsack_single_item_fits(self):
        items = [{"item_id": 101, "item_weight": 3, "priority_value": 15}]
        res = optimize_vault_packing(items, 5)
        self.assertEqual(res["result"]["selected_item_ids"], [101])
        self.assertEqual(res["result"]["max_value"], 15)

    def test_knapsack_single_item_exceeds(self):
        items = [{"item_id": 102, "item_weight": 6, "priority_value": 15}]
        res = optimize_vault_packing(items, 5)
        self.assertEqual(res["result"]["selected_item_ids"], [])
        self.assertEqual(res["result"]["max_value"], 0)

    def test_knapsack_combination_optimal(self):
        items = [
            {"item_id": 1, "item_weight": 2, "priority_value": 20},
            {"item_id": 2, "item_weight": 3, "priority_value": 30},
            {"item_id": 3, "item_weight": 4, "priority_value": 40},
        ]
        res = optimize_vault_packing(items, 5)
        self.assertEqual(res["result"]["selected_item_ids"], [1, 2])
        self.assertEqual(res["result"]["max_value"], 50)

    def test_knapsack_highest_value_not_optimal(self):
        items = [
            {"item_id": 1, "item_weight": 5, "priority_value": 60},
            {"item_id": 2, "item_weight": 3, "priority_value": 40},
            {"item_id": 3, "item_weight": 2, "priority_value": 35},
        ]
        res = optimize_vault_packing(items, 5)
        self.assertEqual(res["result"]["selected_item_ids"], [2, 3])
        self.assertEqual(res["result"]["max_value"], 75)

    def test_knapsack_exact_capacity_utilization(self):
        items = [
            {"item_id": 10, "item_weight": 3, "priority_value": 30},
            {"item_id": 20, "item_weight": 7, "priority_value": 70},
        ]
        res = optimize_vault_packing(items, 10)
        self.assertEqual(res["result"]["selected_item_ids"], [10, 20])
        self.assertEqual(res["result"]["max_value"], 100)

    def test_knapsack_zero_weight_item(self):
        items = [{"item_id": 1, "item_weight": 0, "priority_value": 50}]
        res = optimize_vault_packing(items, 0)
        self.assertEqual(res["result"]["selected_item_ids"], [1])
        self.assertEqual(res["result"]["max_value"], 50)

    def test_knapsack_multiple_zero_weight_items_with_ordinary_items(self):
        items = [
            {"item_id": 1, "item_weight": 0, "priority_value": 15},
            {"item_id": 2, "item_weight": 0, "priority_value": 25},
            {"item_id": 3, "item_weight": 4, "priority_value": 60},
            {"item_id": 4, "item_weight": 6, "priority_value": 70},
        ]
        res = optimize_vault_packing(items, 4)
        self.assertEqual(res["result"]["selected_item_ids"], [1, 2, 3])
        self.assertEqual(res["result"]["max_value"], 100)

    def test_knapsack_tie_handling_prefers_earlier(self):
        items = [
            {"item_id": 1, "item_weight": 2, "priority_value": 20},
            {"item_id": 2, "item_weight": 2, "priority_value": 20},
        ]
        res = optimize_vault_packing(items, 2)
        self.assertEqual(res["result"]["selected_item_ids"], [1])
        self.assertEqual(res["result"]["max_value"], 20)

    def test_knapsack_all_exceed_capacity(self):
        items = [
            {"item_id": 1, "item_weight": 10, "priority_value": 100},
            {"item_id": 2, "item_weight": 20, "priority_value": 200},
        ]
        res = optimize_vault_packing(items, 5)
        self.assertEqual(res["result"]["selected_item_ids"], [])
        self.assertEqual(res["result"]["max_value"], 0)

    def test_knapsack_invalid_capacity(self):
        items = [{"item_id": 1, "item_weight": 1, "priority_value": 10}]
        with self.assertRaises(ValueError):
            optimize_vault_packing(items, -1)
        with self.assertRaises(ValueError):
            optimize_vault_packing(items, True)
        with self.assertRaises(ValueError):
            optimize_vault_packing(items, False)
        with self.assertRaises(ValueError):
            optimize_vault_packing(items, 5.5)
        with self.assertRaises(ValueError):
            optimize_vault_packing(items, "5")
        with self.assertRaises(ValueError):
            optimize_vault_packing(items, None)

    def test_knapsack_invalid_item_structures(self):
        with self.assertRaises(ValueError):
            optimize_vault_packing("not_a_list", 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([None], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_weight": 2, "priority_value": 10}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "priority_value": 10}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "item_weight": 2}], 5)

    def test_knapsack_duplicate_item_ids(self):
        items = [
            {"item_id": 1, "item_weight": 2, "priority_value": 10},
            {"item_id": 1, "item_weight": 3, "priority_value": 20},
        ]
        with self.assertRaises(ValueError):
            optimize_vault_packing(items, 5)

    def test_knapsack_invalid_weights_and_priorities(self):
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "item_weight": True, "priority_value": 10}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "item_weight": 2, "priority_value": False}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "item_weight": -1, "priority_value": 10}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "item_weight": 2, "priority_value": -5}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "item_weight": 2.5, "priority_value": 10}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": 1, "item_weight": 2, "priority_value": "high"}], 5)
        with self.assertRaises(ValueError):
            optimize_vault_packing([{"item_id": True, "item_weight": 2, "priority_value": 10}], 5)

    def test_knapsack_preserves_input(self):
        items = [
            {"item_id": 1, "item_weight": 3, "priority_value": 30},
            {"item_id": 2, "item_weight": 4, "priority_value": 50},
        ]
        copy_items = [dict(it) for it in items]
        optimize_vault_packing(items, 6)
        self.assertEqual(items, copy_items)

    def test_knapsack_telemetry(self):
        items = [{"item_id": 1, "item_weight": 2, "priority_value": 10}]
        res = optimize_vault_packing(items, 5)
        tel = res["telemetry"]
        self.assertEqual(tel["algorithm"], "0/1 Knapsack")
        self.assertEqual(tel["unit"], "Unit III")
        self.assertEqual(tel["complexity"], "O(n * W)")
        self.assertEqual(tel["input_size"], 1)
        self.assertGreaterEqual(tel["time_ms"], 0.0)

    def test_tsp_empty_active_locs(self):
        dist_matrix = [[0.0, 5.0], [5.0, 0.0]]
        res = optimize_collection_tour(dist_matrix, [])
        self.assertEqual(res["result"]["tour"], [])
        self.assertEqual(res["result"]["total_distance"], 0.0)
        self.assertEqual(res["telemetry"]["algorithm"], "TSP (Branch and Bound)")
        self.assertEqual(res["telemetry"]["unit"], "Unit III")
        self.assertEqual(res["telemetry"]["complexity"], "O(n! * n^2) worst case")
        self.assertEqual(res["telemetry"]["input_size"], 0)

    def test_tsp_single_location(self):
        dist_matrix = [[0.0, 5.0], [5.0, 0.0]]
        res = optimize_collection_tour(dist_matrix, [1])
        self.assertEqual(res["result"]["tour"], [1])
        self.assertEqual(res["result"]["total_distance"], 0.0)
        self.assertEqual(res["telemetry"]["input_size"], 1)

    def test_tsp_two_locations_reachable(self):
        dist_matrix = [[0.0, 5.0], [5.0, 0.0]]
        res = optimize_collection_tour(dist_matrix, [1, 2])
        self.assertEqual(res["result"]["tour"], [1, 2, 1])
        self.assertEqual(res["result"]["total_distance"], 10.0)

    def test_tsp_two_locations_unreachable(self):
        dist_matrix = [[0.0, -1.0], [-1.0, 0.0]]
        res = optimize_collection_tour(dist_matrix, [1, 2])
        self.assertEqual(res["result"]["tour"], [])
        self.assertEqual(res["result"]["total_distance"], -1.0)

    def test_tsp_three_locations_prd_example(self):
        dist_matrix = [
            [0.0, 3.0, 5.0],
            [3.0, 0.0, 4.0],
            [5.0, 4.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3])
        self.assertEqual(res["result"]["tour"], [1, 2, 3, 1])
        self.assertEqual(res["result"]["total_distance"], 12.0)

    def test_tsp_nearest_neighbor_suboptimal(self):
        # 4 locations where greedy nearest neighbor chooses [1, 2, 3, 4, 1] (cost 104.0)
        # while Branch and Bound finds the optimal tour [1, 3, 2, 4, 1] (cost 23.0)
        dist_matrix = [
            [0.0, 1.0, 10.0, 2.0],
            [1.0, 0.0, 1.0, 10.0],
            [10.0, 1.0, 0.0, 100.0],
            [2.0, 10.0, 100.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4])
        self.assertEqual(res["result"]["tour"], [1, 3, 2, 4, 1])
        self.assertEqual(res["result"]["total_distance"], 23.0)

    def test_tsp_unreachable_edges(self):
        # 4 locations with some unreachable edges (-1.0), but a reachable Hamiltonian cycle exists
        dist_matrix = [
            [0.0, 2.0, -1.0, 3.0],
            [2.0, 0.0, 4.0, -1.0],
            [-1.0, 4.0, 0.0, 1.0],
            [3.0, -1.0, 1.0, 0.0],
        ]
        # Only feasible tour is 1 - 2 - 3 - 4 - 1 (cost 2 + 4 + 1 + 3 = 10.0)
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4])
        self.assertEqual(res["result"]["tour"], [1, 2, 3, 4, 1])
        self.assertEqual(res["result"]["total_distance"], 10.0)

    def test_tsp_no_complete_tour(self):
        # Disconnected graph: node 3 has no reachable edges
        dist_matrix = [
            [0.0, 5.0, -1.0],
            [5.0, 0.0, -1.0],
            [-1.0, -1.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3])
        self.assertEqual(res["result"]["tour"], [])
        self.assertEqual(res["result"]["total_distance"], -1.0)

    def test_tsp_equal_cost_tours_deterministic(self):
        # 3 locations with equal edge costs (symmetric equilateral triangle)
        # Tours [1, 2, 3, 1] and [1, 3, 2, 1] both have cost 9.0.
        # Lexicographical tie-breaking deterministically selects [1, 2, 3, 1].
        dist_matrix = [
            [0.0, 3.0, 3.0],
            [3.0, 0.0, 3.0],
            [3.0, 3.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3])
        self.assertEqual(res["result"]["tour"], [1, 2, 3, 1])
        self.assertEqual(res["result"]["total_distance"], 9.0)

    def test_tsp_equal_cost_lexicographical_over_nearest_neighbor(self):
        # 4 locations where initial nearest-neighbor greedily selects:
        # 1 -> 3 (cost 1.0) -> 4 (cost 5.0) -> 2 (cost 1.0) -> 1 (cost 5.0) = [1, 3, 4, 2, 1] (cost 12.0)
        # However, the equal-cost tour 1 -> 2 -> 4 -> 3 -> 1 also has cost 12.0
        # (5.0 + 1.0 + 5.0 + 1.0 = 12.0), and is lexicographically smaller:
        # [1, 2, 4, 3, 1] < [1, 3, 4, 2, 1].
        # Branch-and-bound must explore equal-cost branches to select [1, 2, 4, 3, 1].
        dist_matrix = [
            [0.0, 5.0, 1.0, 10.0],
            [5.0, 0.0, 10.0, 1.0],
            [1.0, 10.0, 0.0, 5.0],
            [10.0, 1.0, 5.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4])
        self.assertEqual(res["result"]["tour"], [1, 2, 4, 3, 1])
        self.assertEqual(res["result"]["total_distance"], 12.0)

    def test_tsp_multiple_equal_cost_tours_lexicographical(self):
        # 5 locations in a symmetric ring where forward cycle [1, 2, 3, 4, 5, 1]
        # and reverse cycle [1, 5, 4, 3, 2, 1] both have cost 10.0.
        # Lexicographically smaller tour [1, 2, 3, 4, 5, 1] must be selected.
        dist_matrix = [
            [0.0, 2.0, 10.0, 10.0, 2.0],
            [2.0, 0.0, 2.0, 10.0, 10.0],
            [10.0, 2.0, 0.0, 2.0, 10.0],
            [10.0, 10.0, 2.0, 0.0, 2.0],
            [2.0, 10.0, 10.0, 2.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4, 5])
        self.assertEqual(res["result"]["tour"], [1, 2, 3, 4, 5, 1])
        self.assertEqual(res["result"]["total_distance"], 10.0)

    def test_tsp_equal_cost_with_unreachable_edges(self):
        # 5 locations with some unreachable edges (-1.0).
        # Two feasible equal-cost tours:
        # [1, 2, 4, 3, 5, 1] (cost 3 + 4 + 2 + 5 + 3 = 17.0)
        # [1, 5, 3, 4, 2, 1] (cost 3 + 5 + 2 + 4 + 3 = 17.0)
        # The lexicographically smaller tour [1, 2, 4, 3, 5, 1] must be selected.
        dist_matrix = [
            [0.0, 3.0, -1.0, -1.0, 3.0],
            [3.0, 0.0, -1.0, 4.0, -1.0],
            [-1.0, -1.0, 0.0, 2.0, 5.0],
            [-1.0, 4.0, 2.0, 0.0, -1.0],
            [3.0, -1.0, 5.0, -1.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4, 5])
        self.assertEqual(res["result"]["tour"], [1, 2, 4, 3, 5, 1])
        self.assertEqual(res["result"]["total_distance"], 17.0)

    def test_tsp_floating_point_cost_tie_break(self):
        # 4 locations with fractional edge costs where tours have identical float sums.
        # [1, 2, 4, 3, 1] and [1, 3, 4, 2, 1] both have cost 12.0.
        dist_matrix = [
            [0.0, 4.75, 1.25, 10.0],
            [4.75, 0.0, 10.0, 1.25],
            [1.25, 10.0, 0.0, 4.75],
            [10.0, 1.25, 4.75, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4])
        self.assertEqual(res["result"]["tour"], [1, 2, 4, 3, 1])
        self.assertEqual(res["result"]["total_distance"], 12.0)

    def test_tsp_non_binary_exact_decimal_tie_break(self):
        # 4 locations with non-binary-exact floats (0.1, 0.2, 0.3).
        # Forward tour 1 -> 2 (0.3) -> 4 (0.1) -> 3 (0.2) -> 1 (0.1)
        # Reverse tour 1 -> 3 (0.1) -> 4 (0.2) -> 2 (0.1) -> 1 (0.3)
        # Due to float representation, 0.3 + 0.1 + 0.2 + 0.1 = 0.7000000000000001
        # while 0.1 + 0.2 + 0.1 + 0.3 = 0.7, differing by ~1.1e-16 (within 1e-9 tolerance).
        # Initial nearest-neighbor selects [1, 3, 4, 2, 1].
        # Lexicographically smaller tour [1, 2, 4, 3, 1] must be selected.
        # Returned total_distance must correspond exactly to the selected tour.
        dist_matrix = [
            [0.0, 0.3, 0.1, 1.0],
            [0.3, 0.0, 1.0, 0.1],
            [0.1, 1.0, 0.0, 0.2],
            [1.0, 0.1, 0.2, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4])
        tour = res["result"]["tour"]
        self.assertEqual(tour, [1, 2, 4, 3, 1])
        actual_dist = sum(dist_matrix[u - 1][v - 1] for u, v in zip(tour[:-1], tour[1:]))
        self.assertEqual(res["result"]["total_distance"], actual_dist)

    def test_tsp_returned_distance_synchronized_with_tour(self):
        # Regression test verifying returned total_distance equals actual tour distance
        dist_matrix = [
            [0.0, 5.0, 1.0, 10.0],
            [5.0, 0.0, 10.0, 1.0],
            [1.0, 10.0, 0.0, 5.0],
            [10.0, 1.0, 5.0, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2, 3, 4])
        tour = res["result"]["tour"]
        actual_dist = sum(dist_matrix[u - 1][v - 1] for u, v in zip(tour[:-1], tour[1:]))
        self.assertEqual(res["result"]["total_distance"], actual_dist)

    def test_tsp_symmetry_tolerance_and_normalization(self):
        # Near-symmetric within 1e-6 tolerance: (0, 1)=4.0000001, (1, 0)=4.0000003
        dist_matrix = [
            [0.0, 4.0000001],
            [4.0000003, 0.0],
        ]
        res = optimize_collection_tour(dist_matrix, [1, 2])
        self.assertEqual(res["result"]["tour"], [1, 2, 1])
        # Averaged: 4.0000002 * 2 = 8.0000004 -> rounded to 6 decimals: 8.0
        self.assertAlmostEqual(res["result"]["total_distance"], 8.000000, places=5)

        # Asymmetric beyond 1e-6 tolerance must raise ValueError
        asym_matrix = [
            [0.0, 4.0],
            [4.5, 0.0],
        ]
        with self.assertRaises(ValueError):
            optimize_collection_tour(asym_matrix, [1, 2])

        # One direction unreachable must raise ValueError
        one_unreach = [
            [0.0, -1.0],
            [5.0, 0.0],
        ]
        with self.assertRaises(ValueError):
            optimize_collection_tour(one_unreach, [1, 2])

    def test_tsp_invalid_matrix_dimensions(self):
        with self.assertRaises(ValueError):
            optimize_collection_tour("not_a_list", [1])
        with self.assertRaises(ValueError):
            optimize_collection_tour([[0.0, 1.0]], [1])  # 1x2 non-square
        with self.assertRaises(ValueError):
            optimize_collection_tour([[0.0, 1.0], [1.0]], [1])  # ragged row
        with self.assertRaises(ValueError):
            optimize_collection_tour([], [1])  # empty matrix with active locations

    def test_tsp_invalid_distances(self):
        # Negative distance not -1.0
        with self.assertRaises(ValueError):
            optimize_collection_tour([[0.0, -2.0], [-2.0, 0.0]], [1, 2])
        # Boolean in matrix
        with self.assertRaises(ValueError):
            optimize_collection_tour([[0.0, True], [True, 0.0]], [1, 2])
        # Non-zero diagonal
        with self.assertRaises(ValueError):
            optimize_collection_tour([[1.0, 2.0], [2.0, 0.0]], [1, 2])
        # Non-numeric string
        with self.assertRaises(ValueError):
            optimize_collection_tour([[0.0, "two"], ["two", 0.0]], [1, 2])
        # NaN / inf
        with self.assertRaises(ValueError):
            optimize_collection_tour([[0.0, float("nan")], [float("nan"), 0.0]], [1, 2])
        with self.assertRaises(ValueError):
            optimize_collection_tour([[0.0, float("inf")], [float("inf"), 0.0]], [1, 2])

    def test_tsp_invalid_active_locs(self):
        dist_matrix = [[0.0, 2.0], [2.0, 0.0]]
        with self.assertRaises(ValueError):
            optimize_collection_tour(dist_matrix, "not_a_list")
        with self.assertRaises(ValueError):
            optimize_collection_tour(dist_matrix, [0, 1])  # 0 is out of 1-based range
        with self.assertRaises(ValueError):
            optimize_collection_tour(dist_matrix, [1, 3])  # 3 > 2 (out of range)
        with self.assertRaises(ValueError):
            optimize_collection_tour(dist_matrix, [1, 1])  # duplicate location ID
        with self.assertRaises(ValueError):
            optimize_collection_tour(dist_matrix, [True, 2])  # boolean location ID

    def test_tsp_input_immutability(self):
        dist_matrix = [
            [0.0, 4.0000001],
            [4.0000003, 0.0],
        ]
        active_locs = [1, 2]
        matrix_copy = [list(r) for r in dist_matrix]
        locs_copy = list(active_locs)

        optimize_collection_tour(dist_matrix, active_locs)
        self.assertEqual(dist_matrix, matrix_copy)
        self.assertEqual(active_locs, locs_copy)

    def test_tsp_telemetry(self):
        dist_matrix = [[0.0, 3.0], [3.0, 0.0]]
        res = optimize_collection_tour(dist_matrix, [1, 2])
        tel = res["telemetry"]
        self.assertEqual(tel["algorithm"], "TSP (Branch and Bound)")
        self.assertEqual(tel["unit"], "Unit III")
        self.assertEqual(tel["complexity"], "O(n! * n^2) worst case")
        self.assertEqual(tel["input_size"], 2)
        self.assertGreaterEqual(tel["time_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
