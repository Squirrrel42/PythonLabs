import pygame as pg
import numpy as np
from random import randint

width = 1200
height = 800
FPS = 60
g = 500
PROJECTILES = []
TARGETS = []
AMMO = ["AP", "RCT"]
ap_len = 0.3
rct_len = 0.5
tank_size = 20
targets_number = 2
ap_mass = 1
rct_mass = 5
rct_F = 5000
rct_mu = 1

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
        self.ammo_type = ammo_type

        if ammo_type == "AP":
            self.mass = ap_mass
        elif ammo_type == "RCT":
            self.mass = rct_mass
        if self.ammo_type == "AP":
            self.tr_len = ap_len
        elif self.ammo_type == "RCT":
            self.tr_len = rct_len

        self.coord = np.array(coord)
        self.tracer = [list(self.coord), list(self.coord), list(self.coord)]
        self.vel = np.array(impulse) / self.mass
    def __del__(self):
        pass
    def move(self, g):
        self.coord += self.vel / FPS
        self.vel += np.array([0, g]) / FPS
        if self.ammo_type == "AP":
            self.tracer.append(list(self.coord))
            if len(self.tracer) > FPS * ap_len:
                del self.tracer[0]
        elif self.ammo_type == "RCT":
            if self.mass >= 0.3 * rct_mass:
                self.mass -= rct_mass * rct_mu / FPS
                self.vel += (self.vel / mag(self.vel)) * rct_F / self.mass / FPS
                self.tracer.append(list(self.coord))
            if (len(self.tracer) > FPS * ap_len or self.mass < rct_mass * 0.3) and len(self.tracer) > 0:
                del self.tracer[0]
    def draw(self, surface):
        for i in range(len(self.tracer) - 1):
            if len(self.tracer) > 3:
                if self.ammo_type == "AP":
                    br = 10 + int(50 * (i) / self.tr_len / FPS)
                    color = "#" + str(br * 10101)   
                    pg.draw.line(surface, color, self.tracer[i], self.tracer[i+1], 1)
                elif self.ammo_type == "RCT":
                    br = 10 + int(50 * (i) / self.tr_len / FPS)
                    color = "#" + str(br * 10101)   
                    pg.draw.line(surface, color, self.tracer[i], self.tracer[i+1], int((1 - i / len(self.tracer)) * 10 + 3))
        if self.ammo_type == "AP":
            pg.draw.circle(surface, "YELLOW", self.coord, 1)
        elif self.ammo_type == "RCT":
            if self.mass >= rct_mass * 0.3:
                pg.draw.line(surface, "ORANGE", self.tracer[-1], self.tracer[-2], width=2)
            pg.draw.line(surface, "GREEN", self.coord, self.coord + (self.vel / mag(self.vel) * 1), width=6)
            pg.draw.line(surface, "GREY", self.coord, self.coord + (self.vel / mag(self.vel) * 10), width=2)

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

ammo_n = 0

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
            if event.key == pg.K_TAB:
                if ammo_n < len(AMMO) - 1:
                    ammo_n += 1
                else:
                    ammo_n = 0
    ammo_type = AMMO[ammo_n]

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
        tank.shoot(ammo_type)

    for i in range(len(TARGETS)):
        target = TARGETS[i]
        target.draw(screen)
        for shell in PROJECTILES:
            if target.is_shotdown(shell):
                score += 1
                TARGETS[i] = new_target()

    for shell in PROJECTILES:
        shell.move(g)
        shell.draw(screen)
        if len(shell.tracer) == 0:
            if shell.coord[1] > height:
                PROJECTILES.remove(shell)
                del shell
        elif shell.tracer[0][1] > height:
            PROJECTILES.remove(shell)
            del shell
        
    label1 = font.render(f"SCORE: {score}", True, "RED")
    label2 = font.render(f"AMMO: {ammo_type}", True, "RED")
    screen.blit(label1, [20, 20])
    screen.blit(label2, [width - 200, 20])

    tank.draw(screen)
    pg.display.update()
            
pg.quit()


