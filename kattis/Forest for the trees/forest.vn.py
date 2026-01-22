# Forest for the trees
# https://open.kattis.com/problems/forestforthetrees
# Number-theory
# 21/01/2025


from math import gcd
xb, yb = map(int, input().split())
GCD = gcd(xb, yb)

xb //= GCD
yb //= GCD

x1, y1, x2, y2 = map(int, input().split())
x1, x2 = sorted([x1, x2])
y1, y2 = sorted([y1, y2])

# Iterating on integer intersections
# y = (yb/xb)x (Simplified by gcd) =>
# y = (yb'/xb')x => x = k*xb' => y = k*yb'
# y<yb => k*yb'<gcd*yb' => k<gcd
k = 1
while k<GCD:
    x = k*xb
    y = k*yb
    
    k += 1
    if x>=x1 and x<=x2:
        if y>=y1 and y<=y2:
            # We are in the rectangle
            # We need to get out
            # We are out when x is out or y is out
            k = min(x2//xb, y2//yb)+1
            continue
        
    print("No")
    print(x, y)
    break
else:
    print("Yes")