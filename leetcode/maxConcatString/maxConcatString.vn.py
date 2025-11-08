
# 1239. Maximum Length of a Concatenated String with Unique Characters
# https://leetcode.com/problems/maximum-length-of-a-concatenated-string-with-unique-characters
# Dynamic programming
# 17/09/2025

def maxLength(self, arr: list[str]) -> int:
    totalSubsets = 2 ** (len(arr))
    # dp[mask] = (Mask length with mask, caracs used)
    for i in range(len(arr)):
        s = arr[i]
        arr[i] = 0
        for carac in s:
            j = ord(carac) - ord("a")
            if arr[i] & (1 << j):
                # strings with duplicates are considered empty
                arr[i] = 0
                break
            arr[i] |= (1 << j)

    dp = [
        (0, 0) for _ in range(totalSubsets)
    ]

    for mask in range(totalSubsets):
        for j in range(len(arr)):
            if mask == (1 << j):
                dp[mask] = (arr[j].bit_count(), arr[j])
            if mask & (1 << j):
                maskWithoutJ = mask & ~(1 << j)
                if dp[maskWithoutJ][0] > 0 and (dp[maskWithoutJ][1] & arr[j] == 0):
                    dp[mask] = (
                        dp[maskWithoutJ][0] + arr[j].bit_count(),
                        dp[maskWithoutJ][1] | arr[j]
                    )
    return max(dp)[0]