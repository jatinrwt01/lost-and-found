from typing import Any, Dict, List, Optional
from algorithms.metrics import measure_daa


def _merge(left: List[Dict[str, Any]], right: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i][key] <= right[j][key]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def _merge_sort(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = _merge_sort(items[:mid], key)
    right = _merge_sort(items[mid:], key)
    return _merge(left, right, key)


def _partition(arr: List[Dict[str, Any]], low: int, high: int, key: str) -> int:
    pivot = arr[high][key]
    i = low - 1

    for j in range(low, high):
        if arr[j][key] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _quick_sort_recursive(arr: List[Dict[str, Any]], low: int, high: int, key: str) -> None:
    if low < high:
        pi = _partition(arr, low, high, key)
        _quick_sort_recursive(arr, low, pi - 1, key)
        _quick_sort_recursive(arr, pi + 1, high, key)


def _quick_sort(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    if len(items) <= 1:
        return list(items)

    arr = list(items)
    _quick_sort_recursive(arr, 0, len(arr) - 1, key)
    return arr


@measure_daa(
    algorithm="Merge Sort",
    unit="Unit I",
    complexity="O(n log n)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("items", [])),
)
def _sort_items_merge(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    return _merge_sort(items, key)


@measure_daa(
    algorithm="Quick Sort",
    unit="Unit I",
    complexity="O(n log n) average case",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("items", [])),
)
def _sort_items_quick(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    return _quick_sort(items, key)


def sort_items(items: List[Dict[str, Any]], key: str, method: str = "merge") -> Dict[str, Any]:
    if method == "merge":
        return _sort_items_merge(items, key)
    if method == "quick":
        return _sort_items_quick(items, key)

    raise ValueError(f"Unsupported sorting method: '{method}'. Only 'merge' and 'quick' are supported.")


@measure_daa(
    algorithm="Binary Search",
    unit="Unit I",
    complexity="O(log n)",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("sorted_items", [])),
)
def binary_search_item_id(sorted_items: List[Dict[str, Any]], target_id: int) -> Dict[str, Any]:
    low = 0
    high = len(sorted_items) - 1

    while low <= high:
        mid = (low + high) // 2
        current_id = sorted_items[mid]["item_id"]

        if current_id == target_id:
            return sorted_items[mid]
        elif current_id < target_id:
            low = mid + 1
        else:
            high = mid - 1

    return None


class _DisjointSetUnion:
    def __init__(self, elements: List[int]) -> None:
        self.parent = {elem: elem for elem in elements}
        self.rank = {elem: 0 for elem in elements}

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True


@measure_daa(
    algorithm="Disjoint Set Union",
    unit="Unit I",
    complexity="O(n α(n))",
    input_size_fn=lambda *args, **kwargs: len(args[0]) if args else len(kwargs.get("items", [])),
)
def cluster_duplicate_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid_items = []
    for item in items:
        if item.get("status") != "OPEN":
            continue

        loc_id = item.get("loc_id")
        item_type = item.get("type")
        category = item.get("category")
        title = item.get("title")

        if loc_id is None or loc_id == "" or not item_type or not category or not title:
            continue

        norm_title = " ".join(str(title).strip().casefold().split())
        if not norm_title:
            continue

        valid_items.append((item, norm_title))

    dsu = _DisjointSetUnion([item["item_id"] for item, _ in valid_items])

    seen_keys: Dict[tuple, int] = {}
    for item, norm_title in valid_items:
        key = (
            item["loc_id"],
            item["type"],
            item["category"],
            norm_title,
        )

        item_id = item["item_id"]
        if key in seen_keys:
            dsu.union(seen_keys[key], item_id)
        else:
            seen_keys[key] = item_id

    components: Dict[int, List[int]] = {}
    for item, _ in valid_items:
        item_id = item["item_id"]
        root = dsu.find(item_id)
        components.setdefault(root, []).append(item_id)

    clusters = {
        root: members
        for root, members in components.items()
        if len(members) >= 2
    }

    return {
        "clusters": clusters,
        "duplicate_found": len(clusters) > 0,
    }
