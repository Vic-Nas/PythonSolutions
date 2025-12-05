# Advent of code Day 05
# https://adventofcode.com/2025/day/5
# 05/12/2025
    
from collections import defaultdict
from tqdm.auto import tqdm

with open("input.txt") as file:
    inp = list(map(str.strip, file.readlines()))

res1, res2 = 0, 0
    
stop = inp.index("")
ranges = list(
    map(
        lambda x: tuple(map(int, x.split("-"))),
        inp[:stop]
    )
)

ingredients = list(
    map(
        int, 
        inp[stop + 1:]
    )
)

for ingredient in ingredients:
    for l, r in ranges:
        if l <= ingredient and ingredient <= r:
            res1 += 1
            break

ranges = sorted(ranges)
for i in range(len(ranges) -1):
    l, r = ranges[i]
    l1, r1 = ranges[i + 1]
    if r >= l1:
        ranges[i + 1] = (l, max(r, r1))
        ranges[i] = (0, -1)
        
for l, r in ranges:
    res2 += r - l + 1
    
print(res1, res2)
