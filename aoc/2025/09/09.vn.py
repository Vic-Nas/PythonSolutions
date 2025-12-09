# Advent of code Day 09
# https://adventofcode.com/2025/day/9
# 09/12/2025
   
E = 10 ** -3 
    
class Line:
    def __init__(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2:
            self.a, self.b, self.c = 1, 0, x1
        else:
            a = (y1-y2)/(x1-x2)
            b = (x2*y1-x1*y2)/(x2-x1)
            self.a, self.b, self.c = a, -1, -b
        self.line = self
            
    def has(self, p):
        if not p: return False
        x, y = p
        return abs(x*self.a+y*self.b-self.c) <= E
    
    def inter(self, other):
        a, b, p = self.a, self.b, self.c
        c, d, q = other.a, other.b, other.c
        
        det = a*d-b*c
        if abs(det) <= E: return None
        a, b, c, d = d, -b, -c, a
        x = a*p+b*q
        y = c*p+d*q
        return (x/det, y/det)
    

class Ray:
    def __init__(self, line, condition):
        self.line = line
        self.condition = condition
    
    def has(self, p):
        if not p: return False
        if not self.line.has(p): return False
        return self.condition(p)
    
    def inter(self, ray):
        inter = self.line.inter(ray.line)
        return self.has(inter) and ray.has(inter)
    
with open("input.txt") as file:
    inp = list(map(lambda s: tuple(map(int, s.strip().split(","))), file.readlines()))

from tqdm.auto import tqdm
from functools import cache
from itertools import combinations


xs = sorted(set(x for x, y in inp))
ys = sorted(set(y for x, y in inp))

original = inp
inp = [(xs.index(x), ys.index(y)) for x, y in inp]

edges = []
for i, (x1, y1) in enumerate(inp):
    x2, y2 = inp[(i+1) % len(inp)]
    
    line = Line((x1, y1), (x2, y2))
    if x1 == x2:
        def hits(p, Y1=y1, Y2=y2):
            _, y = p
            return min(Y1, Y2) <= y <= max(Y1, Y2)
    elif y1 == y2:
        def hits(p, X1=x1, X2=x2):
            x, _ = p
            return min(X1, X2) <= x <= max(X1, X2)
    
    edges.append(Ray(line, hits))

@cache
def inside(p):
    # Evil ray algorithm
    # To be inside, the four rays must cross
    # something
    if p in inp: return True
    x, y = p
    
    rays = [
        Ray(Line(p, (x-10, y)), lambda p1, X=x: p1[0] <= X),
        Ray(Line(p, (x, y+10)), lambda p1, Y=y: p1[1] >= Y),
        Ray(Line(p, (x+10, y)), lambda p1, X=x: p1[0] >= X),
        Ray(Line(p, (x, y-10)), lambda p1, Y=y: p1[1] <= Y)
    ]
    
    hits = [0, 0, 0, 0]
    for edge in edges:
        for i, ray in enumerate(rays):
            if ray.inter(edge):
                hits[i] = 1
        if sum(hits) == 4: return True
    return sum(hits) == 4

res1, res2 = 0, 0

for (x1, y1), (x2, y2) in tqdm(list(combinations(inp, 2))):
    # area computed with real coords
    area = (abs(xs[x2] - xs[x1]) + 1) * (abs(ys[y2] - ys[y1]) + 1)
    res1 = max(res1, area)
    
    # Checks on reduced coords
    allIn = True
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if not inside((x, y)):
                allIn = False
                break
        if not allIn:
            break
    
    if allIn:
        res2 = max(res2, area)

print(res1, res2)