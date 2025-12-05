# Advent of code Day 05
# https://adventofcode.com/2025/day/5
# 05/12/2025


with open("input.txt") as file:
    inp = list(map(str.strip, file.readlines()))
    
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

ranges = sorted(ranges)
for i in range(len(ranges) -1):
    l, r = ranges[i]
    l1, r1 = ranges[i + 1]
    if r >= l1:
        ranges[i + 1] = (l, max(r, r1))
        ranges[i] = (0, -1) 
        # I should remove it but saying
        # it is empty is enough

# They're all independant now

res1 = 0
for ingredient in ingredients:
    for l, r in ranges:
        if l <= ingredient and ingredient <= r:
            res1 += 1

res2 = 0
for l, r in ranges:
    res2 += r - l + 1
    
print(res1, res2)