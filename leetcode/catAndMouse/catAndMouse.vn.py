# 913. Cat and Mouse
# https://leetcode.com/problems/cat-and-mouse/
# Minimax, memoization
# 06/12/2025

# Draw positions use many more turns, so I use a limit to detect them.
# The issue is that if I put turns in the memo keys, then even winning/losing 
# states get recalculated for each turn. 
# My solution: I memoize separately the non-draw states (wins/loss) 
# without turns. So:
# * wins/losses are instantly recognized,
# * only draws use the turn limit,
# * and the algo becomes much faster.
class Solution:
    def catMouseGame(self, graph) -> int:
        from functools import cache
        MOUSE_WINS = 1
        CAT_WINS =  2
        DRAW = 0
        REFUGE = 0
        MAX_TURNS = 4 * len(graph)

        def win(isCat):
            if isCat: return CAT_WINS
            else: return MOUSE_WINS
    
        # Separate memory for non-draw states (wins/losses)
        # This caches without turns
        helper = {}
        
        @cache #Caches all
        def solve(mouse=1, cat=2, isCat=False, turns=0):
            helperKey = (mouse, cat, isCat)
            if mouse == cat: return CAT_WINS
            if mouse == REFUGE: return MOUSE_WINS
            
            # Turn limit forces to detect draws
            if turns >= MAX_TURNS: return DRAW
            
            # Check helper for previous wins/losses
            if  helperKey in helper:
                return helper[helperKey]

            # Explore all possible moves for current player
            newMouse = mouse
            newCat = cat
            foundDraw = False
            for nxt in graph[cat if isCat else mouse]:
                if isCat:
                    if nxt == REFUGE: continue  # Cat cannot enter refuge
                    newCat = nxt
                else:
                    newMouse = nxt
                res = solve(newMouse, newCat, not isCat, turns + 1)
                # If current player finds a winning move, takes it
                if res == win(isCat):
                    helper[helperKey] = res
                    return res
                # Track if there is at least one draw
                if res == DRAW:
                    foundDraw = True
            
            # No wins here
            # If found at least one draw, choose draw
            if foundDraw:
                return DRAW

            # No wins or draws found, opponent wins
            helper[helperKey] = win(not isCat)
            return win(not isCat)

        return solve()