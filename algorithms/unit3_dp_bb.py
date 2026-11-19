from typing import Any, Dict
from algorithms.metrics import measure_daa


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
