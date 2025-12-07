# Advent of code Day 07
# https://adventofcode.com/2025/day/7
# 07/12/2025


with open("input.txt") as file:
    inp = list(map(
        lambda s: list(s.strip()), 
        file.readlines()
    ))
    

res1, res2 = 0, 1

from copy import deepcopy
rows = deepcopy(inp)

for i, row in enumerate(rows[:-2]):
    if i % 2 == 1: continue
    for j, el in enumerate(row):
        if el in ["^", "."]: continue
        down = rows[i + 2][j]
        if down != "^":
            rows[i + 2][j] = "|"
        else:
            res1 += 1
            if j - 1 >= 0:
                rows[i + 2][j - 1] = "|"

            if j + 1 < len(row):
                rows[i + 2][j + 1] = "|"


nRows = len(inp)
nCols = len(inp[0])

# dp[i][j] = number of ways to reach position (i, j)
dp = [[0] * nCols for _ in range(nRows)]


startCol = inp[0].index("S")
dp[0][startCol] = 1  # 1 way to start

for i in range(0, nRows - 2, 2):
    for j in range(nCols):
        if dp[i][j] == 0:  # No way to get here
            continue
        
        cpt = dp[i][j]  # Number of ways to get here
        downRow = i + 2
        down = inp[downRow][j]
        
        if down != "^":
            # Just falls
            dp[downRow][j] += cpt
        else:
            # Can go left or right
            if j > 0 and inp[downRow][j - 1] != "|":
                dp[downRow][j - 1] += cpt
            
            if j + 1 < nCols and inp[downRow][j + 1] != "|":
                dp[downRow][j + 1] += cpt

# Sum all positions in the last row
lastRow = nRows - 2
res2 = sum(dp[lastRow])

print(res1, res2)