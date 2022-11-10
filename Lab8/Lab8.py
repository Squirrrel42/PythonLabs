import pygame as pg
import numpy as np
from random import randint

width = 1200
height = 800
FPS = 60
g = 500
PROJECTILES = []
TARGETS = []
ap_mass = 0.1
ap_len = 0.5
tank_size = 20
targets_number = 2

def rotate(vec, a):
    return np.dot(vec, [[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])

def mag(vec): 
    return np.sqrt(np.sum(i**2 for i in vec))

def new_target():
    x = randint(0, width)
    y = randint(0, height)
    r = randint(5, 20)
    return Target([x, y], r)

class Shell:
    def __init__(self, coord, impulse, ammo_type):
        self.type = ammo_type
        self.coord = np.array(coord)
        self.tracer = []
        if ammo_type == "AP":
            self.vel = np.array(impulse) / ap_mass
    def __del__(self):
        pass
    def move(self, g):
        self.coord += self.vel / FPS
        self.vel += np.array([0, g]) / FPS
        self.tracer.append(list(self.coord))
        if len(self.tracer) > FPS * ap_len:
            del self.tracer[0]
        return(self.coord)

class Tank:
    def __init__(self, x, spd, ang, impulse):
        self.x = x
        self.spd = spd
        self.ang = ang
        self.impulse = impulse
    def shoot(self, ammo_type):
        PROJECTILES.append(Shell([self.x, height - tank_size * 0.6], self.impulse * np.array([np.cos(self.ang), np.sin(self.ang)]), ammo_type))

    def draw(self, surface):
        p1 = np.array([self.x, height - tank_size * 0.6]) + tank_size * rotate([0 / 4,   1 / 20], self.ang)
        p2 = np.array([self.x, height - tank_size * 0.6]) + tank_size * rotate([3 / 4,   1 / 20], self.ang)
        p3 = np.array([self.x, height - tank_size * 0.6]) + tank_size * rotate([3 / 4, - 1 / 20], self.ang)
        p4 = np.array([self.x, height - tank_size * 0.6]) + tank_size * rotate([0 / 4, - 1 / 20], self.ang)
        pg.draw.polygon(surface, "RED", [p1, p2, p3, p4])
        pg.draw.circle(surface, "#004400", [self.x, height - tank_size * 0.5], tank_size / 3)
        pg.draw.rect(surface, "#004400", [[self.x - tank_size / 2, height - tank_size / 2], [tank_size, tank_size / 3]])
        pg.draw.circle(surface, "#444444", [self.x - tank_size / 2, height - tank_size / 6], tank_size / 6)
        pg.draw.circle(surface, "#444444", [self.x, height - tank_size / 6], tank_size / 6)
        pg.draw.circle(surface, "#444444", [self.x + tank_size / 2, height - tank_size / 6], tank_size / 6)

    def rotate(self, angle):
        self.ang += angle
        if self.ang >= 2 * np.pi:
            self.ang -= 2 * np.pi
        elif self.ang < 0:
            self.ang += 2 * np.pi
    
    def move(self, direction):
        self.x += direction * self.spd / FPS

class Target:
    def __init__(self, coord, radius):
        self.coord = np.array(coord)
        self.radius = radius
    def __del__(self):
        pass
    def is_shotdown(self, shell):
        if mag(shell.coord - self.coord) <= self.radius:
            return True
        else:
            return False
    def draw(self, surface):
        pg.draw.circle(surface, "WHITE", self.coord, self.radius)
        pg.draw.circle(surface, "BLACK", self.coord, self.radius - 2)


tank = Tank(10, 100, 0, 1000)

pg.init()
font = pg.font.SysFont("comicsansms", 30)
screen = pg.display.set_mode([width, height])

pg.display.update()
clock = pg.time.Clock()
finished = False
score = 0

for i in range(targets_number):
    TARGETS.append(new_target())
while not finished:
    clock.tick(FPS)   
    screen.fill("BLACK") 
    shooting = False
    for event in pg.event.get():                                #getting click, creating new balls
        if event.type == pg.QUIT:
            finished = True
        if event.type == pg.KEYDOWN:
            shooting = (event.key == pg.K_SPACE)

    keys = pg.key.get_pressed()
    if keys[pg.K_d]:
        tank.move(1)
    elif keys[pg.K_a]:
        tank.move(-1)
    
    x, y = pg.mouse.get_pos()
    if (x - tank.x) == 0:
        tank.ang = 3 * np.pi / 2
    elif (x - tank.x) > 0:
        tank.ang = np.arctan((y - (height - tank_size * 0.6)) / (x - tank.x))
    else:
        tank.ang = np.pi + np.arctan((y - (height - tank_size * 0.6)) / (x - tank.x))

    if shooting:
        tank.shoot("AP")

    for i in range(len(TARGETS)):
        target = TARGETS[i]
        target.draw(screen)
        for shell in PROJECTILES:
            if target.is_shotdown(shell):
                score += 1
                TARGETS[i] = new_target()

    for shell in PROJECTILES:
        shell.move(g)
        if len(shell.tracer) > 3:
            for i in range(len(shell.tracer) - 1):
                br = 10 + int(50 * (i) / ap_len / FPS)
                color = "#" + str(br * 10101)
                pg.draw.line(screen, color, shell.tracer[i], shell.tracer[i+1])
        pg.draw.circle(screen, "YELLOW", shell.coord, 1)
        if shell.tracer[0][1] > height:
            PROJECTILES.remove(shell)
            del shell
    label = font.render(f"SCORE: {score}", True, "RED")
    screen.blit(label, [20, 20])

    tank.draw(screen)
    pg.display.update()
            
pg.quit()


