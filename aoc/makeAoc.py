

from pathlib import Path

DAYS = 12
YEAR = 2025
aoc = Path("aoc") / str(YEAR)

for i in range(1, DAYS + 1):
    j = i
    j = str(j).rjust(2, "0")
    normal = aoc / j / "normal" 
    animated = aoc / j / "animated" 
    normal.mkdir(parents=True)
    animated.mkdir(parents=True)
    with open(normal / (j + "_normal.vn.py"), "x") as f:
        f.write(
    f"""# Advent of code Day {j}
# https://adventofcode.com/{YEAR}/day/{i}
# {j}/12/{YEAR}

with open("input.txt") as file:
    inp = file.readlines()
    """
        )
        
    with open(animated / (j + "_animated.vn.py"), "x") as f:
        f.write(
    f"""# Advent of code Day {j}
# https://adventofcode.com/{YEAR}/day/{j}
# {j}/12/{YEAR}

with open("input.txt") as file:
    inp = file.readlines()
    """
        )
        
    with open(normal / "input.txt", "x") as f:
        f.write("input")
    
    with open(animated / "input.txt", "x") as f:
        f.write("input")