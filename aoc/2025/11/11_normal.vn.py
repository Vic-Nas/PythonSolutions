# Advent of code Day 11
# https://adventofcode.com/2025/day/11
# 11/12/2025
    

from collections import defaultdict
from tqdm.auto import tqdm
import networkx as nx

    
with open("input.txt") as file:
    inp = list(
        map(
            lambda s: s.strip().replace(":", "").split(" "),
            file.readlines()
        )
    )



graph = defaultdict(list)
for row in inp:
    start = row[0]
    for dest in row[1:]:
        graph[start].append(
            dest
        )
        

G = nx.DiGraph(graph)
res1 = sum(1 for _ in nx.all_simple_paths(G, "you", "out"))

res2 = 0

pbar = tqdm()

for path in nx.all_simple_paths(G, "svr", "out"):
    pbar.set_postfix(
        {
            "res1": res1,
            "res2": res2
        }
    )
    pbar.update(1)
    if "fft" in path and "dac" in path:
        res2 += 1
        
        
pbar.close()
print(res1, res2)
