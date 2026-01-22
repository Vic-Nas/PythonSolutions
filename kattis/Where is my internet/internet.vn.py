# Where is my internet
# https://open.kattis.com/problems/wheresmyinternet
# Union-find
# 21/01/2025

n, m = map(int, input().split())

parent = [i for i in range(n)]
size = [1 for _ in range(n)]


def find(a):
    if parent[a]==a:
        return a
    parent[a] = find(parent[a])
    return parent[a]
    
def union(a, b):
    a, b = find(a), find(b)
    b, a = sorted(
        [a, b],
        key=lambda x: size[x]
        )
    size[a] += size[b]
    size[b] = 0
    parent[b] = a
    

for _ in range(m):
    a, b = map(int, input().split())
    a -= 1; b -= 1
    union(a, b)
    
network = find(0)

all_good = True
for house in range(n):
    if find(house)!=network:
        print(house+1)
        all_good = False

if all_good:
    print("Connected")