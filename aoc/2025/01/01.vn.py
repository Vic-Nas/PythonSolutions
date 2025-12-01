# Advent of code Day 1
# https://adventofcode.com/2025/day/1
# 01/12/2025

with open("input.txt", "r") as f:
    inp = f.readlines()
    

res1, res2 = 0, 0
pointer = 50
n = 0
for row in inp:
    row = row.strip()
    sens = 1 if row[0] == "R" else -1
    n = int(row[1:])
    for _ in range(n):
        pointer += sens
        pointer %= 100
        res2 += pointer == 0
    res1 += pointer == 0

print(res1, res2)