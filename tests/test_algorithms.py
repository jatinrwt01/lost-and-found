import unittest

from algorithms import (
    binary_search_item_id,
    cluster_duplicate_items,
    kmp_search_items,
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


if __name__ == "__main__":
    unittest.main()
