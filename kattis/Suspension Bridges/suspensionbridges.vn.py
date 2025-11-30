# Collecting beepers
# https://open.kattis.com/problems/suspensionbridges/statistics
# Error propagation, binary search
# 29/11/2025

from math import cosh, ceil, log2
d, s = map(int, input().split())

# > 0.1 will fail :( 
# (Math says it)
tol = 10 ** -4

def f(epsilon):
    # epsilon = a / (a + s) | in 0, 1
    return cosh(d*(1-epsilon)/(2*s*epsilon))-1/epsilon # Equation 1
    
def l(epsilon):
    return 2*s*((1+epsilon)/(1-epsilon))**0.5 # Equation 2

left, right = 0, 1
# Fancy math. On peut juste iterer 50 fois
# d_l/d_epsilon pour savoir tol_epsilon(tol_l)
tol_epsilon = (tol ** 3) / (2 * s)
iterations = ceil(log2(1/tol_epsilon - 2))
# Btw, for bs la taille de l'intervalle est (born_sup - born_inf) / step
# step = 1 pour les entiers.

for _ in range(iterations):
    epsilon = (left + right) / 2
    fl = f(epsilon)
    if fl > 0:
        left = epsilon + tol_epsilon
    else:
        right = epsilon - tol_epsilon

print(l(epsilon))
