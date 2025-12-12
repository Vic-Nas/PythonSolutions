# Advent of code Day 12
# https://adventofcode.com/2025/day/12
# 12/12/2025
# Failed

from copy import deepcopy 
from tqdm.auto import tqdm   
with open("input.txt") as file:
    inp = list(
        map(
            lambda s: s.strip(),
            file.readlines()
        )
    )
    

class Region:
    def __init__(self, row=None):
        if row:
            row = row.split(": ")
            rows, cols = tuple(map(int, row[0].split("x")))
            self.needs = list(map(int, row[1].split(" ")))
            self.grid = [
                [0 for _ in range(cols)]
                for _ in range(rows)
            ]

    def place(self, i, j, gift):
        res = deepcopy(self)
        for i1 in range(3):
            for j1 in range(3):
                if gift[i1][j1]:
                    if i + i1 >= len(res.grid) or j + j1 >= len(res.grid[0]):
                        return None
                    if res.grid[i+i1][j+j1]: return None
                    res.grid[i+i1][j+j1] = 1
        return res
    
    
    def isValid(self):
        # Quick check
        totalCellsNeeded = 0
        for i, need in enumerate(self.needs):
            if need:
                cells = sum(sum(row) for row in gifts[i].grid)
                totalCellsNeeded += cells * need
        
        totalCellsAvailable = len(self.grid) * len(self.grid[0])
        if totalCellsNeeded > totalCellsAvailable:
            return False
        
        toPlace = []
        for i, need in enumerate(self.needs):
            toPlace.extend([i] * need)
        
        maxTries = 100
        tries = [0]
        
        def tryPlace(reg, placedCount):
            tries[0] += 1
            if tries[0] > maxTries:
                return False
                
            if placedCount == len(toPlace):
                return True
            
            giftIdx = toPlace[placedCount]
            
            for turn in gifts[giftIdx].all():
                for row in range(len(reg.grid)):
                    for col in range(len(reg.grid[0])):
                        placed = reg.place(row, col, turn)
                        if placed and tryPlace(placed, placedCount + 1):
                            return True
            
            return False
        
        result = tryPlace(self, 0)
        print(f"Tried {tries[0]} combinations")
        return result
            
    
    def __str__(self):
        return f"{self.dims}-{self.needs}"
    
    def __repr__(self):
        return str(self)
    
class Gift:
    def __init__(self, grid):
        self.grid = grid
    
    def flips(self):
        grid = deepcopy(self.grid)
        horiz = [row[::-1] for row in self.grid]
        yield horiz
        vert = grid[::-1]
        yield vert
    
    def rots(self):
        n = len(self.grid)
        current = self.grid
        for _ in range(3):
            res = self.empty()
            for i in range(n):
                for j in range(n):
                    res[j][n-1-i] = current[i][j]
            yield res
            current = res
    
    def all(self):
        yield self.grid
        yield from self.flips()
        yield from self.rots()
        
    def empty(self):
        return [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
gifts = []
regions: list[Region] = []

inp.append("")
parts = []

l = 0
for r in range(len(inp)):
    if not inp[r]:
          parts.append(inp[l:r])
          l = r+1
          

for part in parts:
    if ": " in part[0]:
        for region in part:
            regions.append(Region(region))
    elif ":" in part[0]:
        gift = list(
            map(
                lambda s: list(map(int, s.replace("#", "1").replace(".", "0"))),
                part[1:]
            )
        )
        gifts.append(Gift(gift))
        

res1, res2 = 0, 0
for region in tqdm(regions):
    res1 += region.isValid()
    
print(res1, res2)