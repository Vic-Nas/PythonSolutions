# Forest for the trees
# https://open.kattis.com/problems/forestforthetrees
# Number-theory
# 21/01/2025


from math import gcd
xb, yb = map(int, input().split())
pgcd = gcd(xb, yb)

xb //= pgcd
yb //= pgcd

x1, y1, x2, y2 = map(int, input().split())

for k in range(1, pgcd):
    x = k*xb
    y = yb*x//xb
    if x*yb != y*xb: continue
    if x>=x1 and x<=x2 and y>=y1 and y<=y2:
        continue
    
    print("No")
    print(x, y)
    break
else:
    print("Yes")