# Collecting beepers
# https://open.kattis.com/problems
# Dynamic programming
# 15/09/2025

from math import asin, pi

for _ in range(int(input())):
    D, d, s = map(float, input().split())
    n = pi / asin((s + d) / (D - d))
    print(int(n))