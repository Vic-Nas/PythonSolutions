# Advent of code Day 02
# https://adventofcode.com/2025/day/2
# 02/12/2025

from tqdm.auto import tqdm

with open("input.txt") as f:
    inp = list(
        map(
            lambda l: tuple(map(int, l.split("-"))),
            f.readlines()[0].strip().split(","))
    )
    
res1 = 0    
res2 = 0
for l, r in tqdm(inp):
    for n in range(l, r + 1):
        s = str(n)
        s1 = s[:len(s)//2]
        s2 = s[len(s)//2:]
        if s1 == s2:
            res1 += n
            
        for p in range(1, len(s)//2 + 1):
            if s == s[:p] * (len(s) // p):
                res2 += n
                break
            
print(res1, res2)