# 913. Cat and Mouse
# https://leetcode.com/problems/cat-and-mouse/
# Dunno
# 05/12/2025


# Note: This is sadly TLE
# 70 cases passed
class Solution:
    def catMouseGame(self, graph) -> int:
        from functools import cache
        MOUSE_WINS = 1
        CAT_WINS =  2
        DRAW = 0
        REFUGE = 0
        limit = 4 * len(graph)

        def wins(isCat):
            if isCat: return CAT_WINS
            else:
                return MOUSE_WINS
    
        @cache
        def solve(mouse=1, cat=2, isCat=False, turns=0):
            if mouse == cat: return CAT_WINS
            if mouse == REFUGE: return MOUSE_WINS
            if turns >= limit: return DRAW

            newMouse = mouse
            newCat = cat
            foundDraw = False
            for nxt in graph[cat if isCat else mouse]:
                if isCat:
                    if nxt == 0: continue
                    newCat = nxt
                else:
                    newMouse = nxt
                res = solve(newMouse, newCat, not isCat, turns + 1)
                if res == wins(isCat):
                    return res

                if res == DRAW:
                    foundDraw = True

            if foundDraw:
                return DRAW

            return wins(not isCat)

        return solve()