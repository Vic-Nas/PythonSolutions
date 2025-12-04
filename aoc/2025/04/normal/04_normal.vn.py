# Advent of code Day 04
# https://adventofcode.com/2025/day/4
# 04/12/2025
    
from tqdm.auto import tqdm
from functools import reduce

with open("input.txt") as file:
    inp = list(map(lambda row: list(row.strip()), file.readlines()))
    
def adjacents(i, j):
    res = []
    for i1 in (i, i + 1, i - 1):
        for j1 in (j, j + 1, j - 1):
            if (i, j) == (i1, j1) or i1 < 0 or j1 < 0: continue
            try:
                res.append(inp[i1][j1])
            except:
                pass
    return res

def hash(mat):
    step1 = reduce(lambda a, b: a + b, mat, [])
    return reduce(lambda a, b: a + b, step1, "")

PAPER = "@"
OTHER = "."
    
res1 = 0
for i in range(len(inp)):
    for j in range(len(inp)):
        if inp[i][j] != PAPER: continue
        if adjacents(i, j).count(PAPER) < 4:
            res1 += 1
          
res2 = 0
newOnes = True
while newOnes:
    newOnes = False
    for i in range(len(inp)):
        for j in range(len(inp)):
            if inp[i][j] != PAPER: continue
            if adjacents(i, j).count(PAPER) < 4:
                res2 += 1
                inp[i][j] = OTHER
                newOnes = True

            
print(res1, res2)