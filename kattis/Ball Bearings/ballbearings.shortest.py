from math import*
for D,d,s in(map(eval,input().split())for _ in range(int(input()))):print(int(pi/asin((s+d)/(D-d))))