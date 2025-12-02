import pygame
from math import sin, cos, pi
from pymsgbox import alert
WIDTH, HEIGHT = 800, 800
x0, y0 =  WIDTH // 2, HEIGHT // 2

# Speed
fps = 200
skip = 100


mod = 100
radius = x0 / 1.2
textRadius = x0 / 1.1
fontSize = 20
fontSize2 = int(1.5 * fontSize)
res1, res2 = 0, 0
pointer = 50
running = True


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, fontSize)
font2 = pygame.font.Font(None, fontSize2)



with open("input.txt", "r") as f:
    inp = f.readlines()

for progress, row in enumerate(inp, 1):
    if not running: break
    row = row.strip()
    sens = 1 if row[0] == "R" else -1
    turns = int(row[1:])
    
    for i in range(turns):
        if not running: break
        pointer += sens
        pointer %= 100
        res2 += pointer == 0
        
        if i % skip != 0: continue
        
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    fps = max(20, fps - 20)
                
                if event.key == pygame.K_UP:
                    fps = min(500, fps + 20)

                if event.key == pygame.K_LEFT:
                    skip = max(1, skip // 2)
                
                if event.key == pygame.K_RIGHT:
                    skip = min(1000, skip * 2)
                
        
        screen.fill("white")
        pygame.draw.circle(screen, "black", (x0, y0), radius, 5)
        for n in range(mod):
            txt = font.render(str(n), True, "red")
            alpha = 2 * pi * n / mod - (pi / 2)
            x = textRadius * cos(alpha)
            y = textRadius * sin(alpha)
            screen.blit(txt, (x0 + x, y0 + y))
            if n == pointer:
                pygame.draw.line(screen, "blue", (x0, y0), (x0 + x, y0 + y), 2)
            state = f"Fps: {fps}--Skip: {skip}--Instruction: {row}--res1: {res1}--res2: {res2}--Progress: {progress * 100 / len(inp): .2f} %"
            txt = font2.render(state, True, "green", "black")
            screen.blit(txt, (0, 0))
    
        pygame.display.flip()
        clock.tick(fps)
    
    res1 += pointer == 0


alert(state)
pygame.quit()
