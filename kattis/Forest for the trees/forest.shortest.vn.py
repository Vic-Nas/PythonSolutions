from math import gcd;a,b=map(int,input().split());c=gcd(a,b);a//=c;b//=c;d,e,f,j=map(int,input().split())
d,f=[d,f].sort()
e,j=[e,j].sort()
k=1
while k<c:
 x=k*a;y=k*b;k+=1
 if d<x<=f and e<=y<=j:k=min(f//a,j//b)+1;continue
 print("No\n%d %d"%(x,y));break
else:print("Yes")