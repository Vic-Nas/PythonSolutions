# Advent of code Day 03
# https://adventofcode.com/2025/day/3
# 03/12/2025
    
from tqdm.auto import tqdm
from functools import cache 
    
with open("input.txt", "r") as f:
    inp = f.readlines()

res1, res2 = 0, 0

@cache
def best(row, n, start=0):
    if len(row) - start < n or n == 0: return 0

    return  max(
        best(row, n, start + 1), 
        row[0] * 10**(n-1) + best(row[1:], start + 1, n - 1)
    )
    
for row in tqdm(inp):
    row = tuple(map(int, row.strip()))
    res1 += best(row, 2)
    res2 += best(row, 12)
    
    
    
print(res1, res2)       
    
