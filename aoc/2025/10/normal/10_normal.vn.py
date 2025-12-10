# Advent of code Day 10
# https://adventofcode.com/2025/day/10
# 10/12/2025
    
from functools import cache    
import heapq
from collections import defaultdict
from tqdm.auto import tqdm
from collections import deque

def parse(buttons: str):
    buttons = buttons.strip().split()
    goal = tuple(map(lambda x: int(x == "#"),
        buttons[0][1:-1]))
    size = len(goal)
    req = tuple(map(int, buttons[-1][1:-1].split(",")))
    buttons = list(map(
        lambda s: tuple(map(int, s[1:-1].split(","))),
        buttons[1:-1]))
    for i in range(len(buttons)):
        r = [0 for _ in range(size)]
        for j in buttons[i]:
            r[j] = 1
        buttons[i] = tuple(r)
    return goal, buttons, req


with open("input.txt") as file:
    inp = list(
        map(
            parse,
            file.readlines()
        )
    )
   
@cache
def apply(button, state, mod=2):
    res = list(state)
    for i in range(len(res)):
        res[i] += button[i]
        if mod:
            res[i] %= mod
    return tuple(res)
    
res1, res2 = 0, 0
for goal, buttons, req in tqdm(inp):
    n = len(goal)
    start = tuple(0 for _ in range(n))
    visited = defaultdict(bool)
    heap = [(0, start)] 
    
    while heap:
        presses, state = heapq.heappop(heap)
        
        if visited[state]: continue
        visited[state] = True
        
        if state == goal:
            res1 += presses
            break
        
        for button in buttons:
            newState = apply(button, state)
            if visited[newState]: continue
            
            heapq.heappush(
                heap,
                (presses+1, newState)
            )

from pulp import *

res2 = 0
for goal, buttons, req in tqdm(inp):
    # Create integer variables (x[i] = times button i is pressed)
    x = [LpVariable(f"x{i}", 0, cat='Integer') for i in range(len(buttons))]
    
    # Create optimization problem (minimization by default)
    prob = LpProblem()
    
    # Objective: minimize total button presses
    prob += lpSum(x)
    
    # Constraints: for each dimension, button presses must sum to goal
    for i in range(len(goal)):
        prob += lpSum(x[j] * buttons[j][i] for j in range(len(buttons))) == req[i]
    
    # Solve with no output
    prob.solve(PULP_CBC_CMD(msg=0))
    
    # If optimal solution found, add to result
    if prob.status == 1:
        res2 += int(value(prob.objective))
        
                
print(res1, res2)