# Advent of code Day 06
# https://adventofcode.com/2025/day/6
# 06/12/2025
    
# No blank line at end of file
with open("input.txt") as file:
    inp = file.readlines()
    
nums = inp[:-1]
big = max(nums, key=len)
reals = []

# I needed to add something because
# my algo needs two ops to calculate
# the zone. I added something I could clean
# easily 
ops = inp[-1].ljust(len(big), " ") + "\t"

# The zone is determined 
# by the operators

prev = 0
for i in range(1, len(ops)):
    if ops[i] != ' ':
        real = []
        for row in nums:
            real.append(
                row[prev: i - 1] # Here
            )
        prev = i
        reals.append(real)
    
# We can clean ops now
ops = ops.split()  

from functools import reduce

res1, res2 = 0, 0
default = {
    "+": 0, 
    "*": 1
}

for i in range(len(ops)):
    res1 += reduce(
        lambda a, b: eval(f"{a}{ops[i]}{b}"),
        reals[i],
        default[ops[i]]
    )
    
    # reals is all centered already
    # They all have same length 
    # in each row
    
    final = ["" for _  in range(len(reals[i][0]))]
    for j in range(len(final)):
        for n in reals[i]:
            final[j] += n[j]
            # I strip for not to have a
            # space in the middle
            final[j] = final[j].strip()
            
            
    res2 += reduce(
        lambda a, b: eval(f"{a}{ops[i]}{b}"),
        final,
        default[ops[i]]
    )
    
print(res1, res2)