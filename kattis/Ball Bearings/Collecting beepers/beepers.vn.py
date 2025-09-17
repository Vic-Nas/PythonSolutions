
from functools import cache

@cache
def dist(A: tuple[float], B: tuple[float]) -> float:
    return sum(
        abs(x - y) for x, y in zip(A, B)
    )

for _ in range(int(input())):
    X, Y = map(int, input().split())
    start = tuple(map(int, input().split()))
    beepers = [
        (*map(int, input().split()), ) for _ in range(int(input()))
        ]
    totalSubsets = 1 << len(beepers) # 2 ** n sets
    
    # dp[j][mask] = Minimal cost to be at j, 
    # while having visited beepers in mask
    dp = [[float("inf") for _ in range(totalSubsets)] for _ in range(len(beepers))]
    for mask in range(totalSubsets):
        for j in range(len(beepers)):
            if mask == (1 << j):
                dp[j][mask] = dist(start, beepers[j])
            elif mask & (1 << j):
                dp[j][mask] = min(
                    dist(
                        beepers[j], beepers[k]
                    ) + dp[k][mask & ~(1 << j)] for k in range(len(beepers))
                    if (mask & ~(1 << j)) & (1 << k)
                )
                
    res = min(
        dp[j][totalSubsets - 1] + dist(beepers[j], start) for j in range(len(beepers))
    )
                
                
    print(res)
                
                
