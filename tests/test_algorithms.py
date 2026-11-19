import unittest

from algorithms import (
    binary_search_item_id,
    cluster_duplicate_items,
    kmp_search_items,
    rabin_karp_watchlist_scan,
    sort_items,
)
from algorithms.unit4_str_flow import _rabin_karp_search


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
        found = binary_search_item_id(items, 20)
        self.assertEqual(found["result"]["title"], "Phone")
        not_found = binary_search_item_id(items, 99)
        self.assertIsNone(not_found["result"])

    def test_cluster_duplicate_items(self):
        items = [
            {
                "item_id": 1,
                "loc_id": 1,
                "type": "LOST",
                "category": "Electronics",
                "title": "Dell XPS 15",
                "status": "OPEN",
            },
            {
                "item_id": 2,
                "loc_id": 1,
                "type": "LOST",
                "category": "Electronics",
                "title": "dell xps 15",
                "status": "OPEN",
            },
            {
                "item_id": 3,
                "loc_id": 2,
                "type": "LOST",
                "category": "Electronics",
                "title": "Dell XPS 15",
                "status": "OPEN",
            },
        ]
        res = cluster_duplicate_items(items)
        clusters = res["result"]["clusters"]
        self.assertTrue(res["result"]["duplicate_found"])
        self.assertEqual(len(clusters), 1)
        root = list(clusters.keys())[0]
        self.assertEqual(sorted(clusters[root]), [1, 2])


class TestUnit4Algorithms(unittest.TestCase):
    def test_kmp_empty_items(self):
        res = kmp_search_items([], "laptop")
        self.assertEqual(res["result"], [])
        self.assertEqual(res["telemetry"]["algorithm"], "Knuth-Morris-Pratt (KMP)")
        self.assertEqual(res["telemetry"]["unit"], "Unit IV")
        self.assertEqual(res["telemetry"]["complexity"], "O(n + m)")
        self.assertEqual(res["telemetry"]["input_size"], len("laptop"))

    def test_kmp_empty_pattern(self):
        items = [
            {"item_id": 1, "title": "Keys"},
            {"item_id": 2, "title": "Phone"},
        ]
        res = kmp_search_items(items, "")
        self.assertEqual(res["result"], items)
        self.assertEqual(res["telemetry"]["input_size"], len("Keys") + len("Phone"))

    def test_kmp_pattern_in_title(self):
        items = [
            {"item_id": 1, "title": "Dell XPS 15 Laptop", "description": "Silver color"},
            {"item_id": 2, "title": "Hydro Flask", "description": "Blue bottle"},
        ]
        res = kmp_search_items(items, "dell")
        self.assertEqual(len(res["result"]), 1)
        self.assertEqual(res["result"][0]["item_id"], 1)

    def test_kmp_pattern_in_description(self):
        items = [
            {"item_id": 1, "title": "Backpack", "description": "Lost near study desks in Central Library"},
            {"item_id": 2, "title": "Notebook", "description": "Math notes"},
        ]
        res = kmp_search_items(items, "study desks")
        self.assertEqual(len(res["result"]), 1)
        self.assertEqual(res["result"][0]["item_id"], 1)

    def test_kmp_pattern_not_found(self):
        items = [
            {"item_id": 1, "title": "Dell Laptop", "description": "Silver"},
            {"item_id": 2, "title": "Water bottle", "description": "Blue"},
        ]
        res = kmp_search_items(items, "MacBook")
        self.assertEqual(res["result"], [])

    def test_kmp_multiple_occurrences_single_item(self):
        items = [
            {"item_id": 1, "title": "Blue Blue Blue Bottle", "description": "Very blue bottle"},
        ]
        res = kmp_search_items(items, "blue")
        self.assertEqual(len(res["result"]), 1)
        self.assertEqual(res["result"][0]["item_id"], 1)

    def test_kmp_overlapping_pattern_occurrences(self):
        items = [
            {"item_id": 1, "title": "AAAAAA", "description": "ABABA"},
            {"item_id": 2, "title": "XYZ", "description": "Nothing"},
        ]
        res_a = kmp_search_items(items, "AAAA")
        self.assertEqual(len(res_a["result"]), 1)
        self.assertEqual(res_a["result"][0]["item_id"], 1)

        res_b = kmp_search_items(items, "ABA")
        self.assertEqual(len(res_b["result"]), 1)
        self.assertEqual(res_b["result"][0]["item_id"], 1)

    def test_kmp_case_sensitivity(self):
        items = [
            {"item_id": 1, "title": "Dell XPS 15", "description": "Silver Laptop"},
        ]
        self.assertEqual(len(kmp_search_items(items, "dell")["result"]), 1)
        self.assertEqual(len(kmp_search_items(items, "DELL")["result"]), 1)
        self.assertEqual(len(kmp_search_items(items, "xPs")["result"]), 1)
        self.assertEqual(len(kmp_search_items(items, "SILVER")["result"]), 1)

    def test_kmp_empty_searchable_fields(self):
        items = [
            {"item_id": 1, "title": "", "category": "", "description": "", "serial_tag": ""},
        ]
        res = kmp_search_items(items, "laptop")
        self.assertEqual(res["result"], [])

    def test_kmp_missing_searchable_fields(self):
        items = [
            {"item_id": 1, "title": "Water bottle"},
            {"item_id": 2, "title": None, "category": None, "description": "Keys found", "serial_tag": None},
        ]
        res_bottle = kmp_search_items(items, "bottle")
        self.assertEqual(len(res_bottle["result"]), 1)
        self.assertEqual(res_bottle["result"][0]["item_id"], 1)

        res_keys = kmp_search_items(items, "keys")
        self.assertEqual(len(res_keys["result"]), 1)
        self.assertEqual(res_keys["result"][0]["item_id"], 2)

    def test_kmp_category_matching(self):
        items = [
            {"item_id": 1, "title": "Earphones", "category": "Electronics", "description": "White"},
            {"item_id": 2, "title": "Cap", "category": "Clothing", "description": "Red"},
        ]
        res = kmp_search_items(items, "electronics")
        self.assertEqual(len(res["result"]), 1)
        self.assertEqual(res["result"][0]["item_id"], 1)

    def test_kmp_serial_tag_matching(self):
        items = [
            {"item_id": 1, "title": "Laptop", "serial_tag": "DELL-9821-X"},
            {"item_id": 2, "title": "Tablet", "serial_tag": "TAB-4512-Y"},
        ]
        res = kmp_search_items(items, "9821")
        self.assertEqual(len(res["result"]), 1)
        self.assertEqual(res["result"][0]["item_id"], 1)

    def test_kmp_invalid_pattern_type(self):
        with self.assertRaises(ValueError):
            kmp_search_items([], 123)
        with self.assertRaises(ValueError):
            kmp_search_items([], None)
        with self.assertRaises(ValueError):
            kmp_search_items([], True)
        with self.assertRaises(ValueError):
            kmp_search_items([], ["pattern"])

    def test_kmp_invalid_items_type(self):
        with self.assertRaises(ValueError):
            kmp_search_items("not_a_list", "pat")
        with self.assertRaises(ValueError):
            kmp_search_items(None, "pat")
        with self.assertRaises(ValueError):
            kmp_search_items(123, "pat")

    def test_kmp_invalid_item_element(self):
        with self.assertRaises(ValueError):
            kmp_search_items(["not_a_dict"], "pat")
        with self.assertRaises(ValueError):
            kmp_search_items([None], "pat")
        with self.assertRaises(ValueError):
            kmp_search_items([123], "pat")

    def test_kmp_invalid_field_types(self):
        with self.assertRaises(ValueError):
            kmp_search_items([{"title": 123}], "pat")
        with self.assertRaises(ValueError):
            kmp_search_items([{"category": True}], "pat")
        with self.assertRaises(ValueError):
            kmp_search_items([{"description": ["desc"]}], "pat")
        with self.assertRaises(ValueError):
            kmp_search_items([{"serial_tag": False}], "pat")

    def test_kmp_input_immutability(self):
        items = [
            {"item_id": 1, "title": "Laptop", "category": "Electronics"},
        ]
        copy_items = [dict(it) for it in items]
        res = kmp_search_items(items, "laptop")
        self.assertEqual(items, copy_items)
        res["result"][0]["title"] = "Modified"
        self.assertEqual(items[0]["title"], "Laptop")

    def test_kmp_preserves_original_order(self):
        items = [
            {"item_id": 3, "title": "Device Gamma", "description": "common"},
            {"item_id": 1, "title": "Device Alpha", "description": "common"},
            {"item_id": 2, "title": "Device Beta", "description": "common"},
        ]
        res = kmp_search_items(items, "common")
        self.assertEqual([it["item_id"] for it in res["result"]], [3, 1, 2])

    def test_kmp_telemetry(self):
        items = [
            {"title": "Dell", "description": "Laptop"},
        ]
        res = kmp_search_items(items, "dell")
        tel = res["telemetry"]
        self.assertEqual(tel["algorithm"], "Knuth-Morris-Pratt (KMP)")
        self.assertEqual(tel["unit"], "Unit IV")
        self.assertEqual(tel["complexity"], "O(n + m)")
        expected_input_size = len("Dell Laptop") + len("dell")
        self.assertEqual(tel["input_size"], expected_input_size)
        self.assertGreaterEqual(tel["time_ms"], 0.0)

    def test_rk_empty_text(self):
        res = rabin_karp_watchlist_scan("", ["stolen"])
        self.assertFalse(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], [])
        self.assertEqual(res["telemetry"]["algorithm"], "Rabin-Karp")
        self.assertEqual(res["telemetry"]["unit"], "Unit IV")
        self.assertEqual(res["telemetry"]["complexity"], "O(n * P) worst case, O(n * d + P) average")
        self.assertEqual(res["telemetry"]["input_size"], len("stolen"))

    def test_rk_empty_watchlist(self):
        res = rabin_karp_watchlist_scan("This is safe text", [])
        self.assertFalse(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], [])
        self.assertEqual(res["telemetry"]["input_size"], len("This is safe text"))

    def test_rk_single_pattern_found(self):
        res = rabin_karp_watchlist_scan("This item was stolen from lab", ["stolen"])
        self.assertTrue(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], ["stolen"])

    def test_rk_single_pattern_not_found(self):
        res = rabin_karp_watchlist_scan("Lost blue backpack in library", ["stolen"])
        self.assertFalse(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], [])

    def test_rk_multiple_patterns_found(self):
        text = "Suspected fraud involving a stolen identity tag"
        watchlist = ["stolen", "fraud"]
        res = rabin_karp_watchlist_scan(text, watchlist)
        self.assertTrue(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], ["stolen", "fraud"])

    def test_rk_only_some_patterns_found(self):
        text = "Lost keys found near cafeteria"
        watchlist = ["stolen", "lost", "fraud"]
        res = rabin_karp_watchlist_scan(text, watchlist)
        self.assertTrue(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], ["lost"])

    def test_rk_pattern_longer_than_text(self):
        res = rabin_karp_watchlist_scan("hi", ["longerpatternthanhi"])
        self.assertFalse(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], [])

    def test_rk_empty_watchlist_pattern(self):
        res1 = rabin_karp_watchlist_scan("some text", [""])
        self.assertTrue(res1["result"]["flagged"])
        self.assertEqual(res1["result"]["matched_patterns"], [""])

        res2 = rabin_karp_watchlist_scan("", [""])
        self.assertTrue(res2["result"]["flagged"])
        self.assertEqual(res2["result"]["matched_patterns"], [""])

    def test_rk_duplicate_watchlist_patterns(self):
        text = "fraudulent activity detected"
        watchlist = ["fraud", "fraud", "fraud"]
        res = rabin_karp_watchlist_scan(text, watchlist)
        self.assertTrue(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], ["fraud"])

    def test_rk_case_insensitive(self):
        res1 = rabin_karp_watchlist_scan("STOLEN laptop reported", ["stolen"])
        self.assertTrue(res1["result"]["flagged"])
        self.assertEqual(res1["result"]["matched_patterns"], ["stolen"])

        res2 = rabin_karp_watchlist_scan("stolen laptop reported", ["STOLEN"])
        self.assertTrue(res2["result"]["flagged"])
        self.assertEqual(res2["result"]["matched_patterns"], ["STOLEN"])

        res3 = rabin_karp_watchlist_scan("FrAuD alert", ["fraud"])
        self.assertTrue(res3["result"]["flagged"])
        self.assertEqual(res3["result"]["matched_patterns"], ["fraud"])

    def test_rk_hash_collision_verification(self):
        # Using modulus=1 causes all string hashes to be 0 (guaranteed hash collision).
        # Character verification must correctly determine that "world" does not appear in "hello".
        self.assertFalse(_rabin_karp_search("hello", "world", base=257, modulus=1))
        # But when the substring actually matches, it returns True even under modulus=1.
        self.assertTrue(_rabin_karp_search("hello world", "world", base=257, modulus=1))

    def test_rk_overlapping_occurrences(self):
        res = rabin_karp_watchlist_scan("aaaaa", ["aaa"])
        self.assertTrue(res["result"]["flagged"])
        self.assertEqual(res["result"]["matched_patterns"], ["aaa"])

    def test_rk_invalid_text_type(self):
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan(123, ["stolen"])
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan(None, ["stolen"])
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan(True, ["stolen"])
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan(["text"], ["stolen"])

    def test_rk_invalid_watchlist_type(self):
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan("text", "not_a_list")
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan("text", None)
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan("text", 123)

    def test_rk_invalid_watchlist_elements(self):
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan("text", [123])
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan("text", [None])
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan("text", [True])
        with self.assertRaises(ValueError):
            rabin_karp_watchlist_scan("text", [["nested"]])

    def test_rk_input_immutability(self):
        text = "This item was stolen"
        watchlist = ["stolen", "fraud"]
        copy_wl = list(watchlist)
        rabin_karp_watchlist_scan(text, watchlist)
        self.assertEqual(watchlist, copy_wl)

    def test_rk_matched_pattern_ordering(self):
        text = "Suspected fraud and stolen bicycle"
        watchlist1 = ["fraud", "stolen"]
        res1 = rabin_karp_watchlist_scan(text, watchlist1)
        self.assertEqual(res1["result"]["matched_patterns"], ["fraud", "stolen"])

        watchlist2 = ["stolen", "fraud"]
        res2 = rabin_karp_watchlist_scan(text, watchlist2)
        self.assertEqual(res2["result"]["matched_patterns"], ["stolen", "fraud"])

    def test_rk_telemetry(self):
        text = "Watchlist text"
        watchlist = ["list", "watch"]
        res = rabin_karp_watchlist_scan(text, watchlist)
        tel = res["telemetry"]
        self.assertEqual(tel["algorithm"], "Rabin-Karp")
        self.assertEqual(tel["unit"], "Unit IV")
        self.assertEqual(tel["complexity"], "O(n * P) worst case, O(n * d + P) average")
        expected_size = len(text) + sum(len(p) for p in watchlist)
        self.assertEqual(tel["input_size"], expected_size)
        self.assertGreaterEqual(tel["time_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
