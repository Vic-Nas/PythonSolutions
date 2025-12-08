# Advent of code Day 08
# https://adventofcode.com/2025/day/8
# 08/12/2025
    
from tqdm.auto import tqdm

with open("input.txt") as file:
    inp = list(
        map(
            lambda s: tuple(
                map(
                    int, s.strip().split(",")
                )
            ),
            file.readlines()
        )
    )
    
edges = []
parent = [i for i in range(len(inp))]
size = [1 for _ in range(len(inp))]

for i, (x1, y1, z1) in tqdm(enumerate(inp), desc="Adding edges"):
    for j, (x2, y2, z2) in enumerate(inp[i+1:], start=i+1):
        cost = (x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2
        edges.append(
            (cost, i, j)
        )
edges.sort()

def find(a):
    if parent[a]!= a:
        parent[a] = find(parent[a])
    return parent[a]

def union(a, b):
    root1 = find(a)
    root2 = find(b)
    parent[root2] = root1
    size[root1] += size[root2]
    size[root2] = 0


res1, res2 = 0, 0
cpt, wanted = 0, 1000
for edge in tqdm(edges, desc="Computing res"):
    if cpt == wanted:
        a, b, c = sorted(size, reverse=True)[:3]
        res1 = a*b*c
    cost, vertexA, vertexB = edge
    cpt += 1
    if find(vertexA) != find(vertexB):
        union(vertexA, vertexB)
        # We just need the last res2
        res2 = inp[vertexA][0] * inp[vertexB][0]
        

print(res1, res2)