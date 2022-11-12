import pygame as pg
import numpy as np
from random import randint, random

width = 1200
height = 800
FPS = 60
g = 500
PROJECTILES = []
EXPLOSIONS = []
TARGETS = []
PULSES = []
AMMO = ["AP", "HE", "RCT"]
FLASH_LABELS = []
SCORE = 0
DIFF = 1
load_time = 0.5
charge_time = 1
pulse_time = 5

tank_size = 15
targets_number = 5

ap_mass = 0.7
ap_len = 0.3

he_mass = 1.1
he_len = 0.3

rct_mass = 5
rct_F = 5000
rct_mu = 1
rct_len = 0.5

bmb_mass = 1
bmb_len = 0.1

def diff():
    global SCORE
    global DIFF
    global targets_number
    if SCORE < 50:
        DIFF = 1 + SCORE / 50 * 2
    else:
        DIFF = 3
    targets_number = 4 + int(DIFF)

def prob(p):
    if p >= random():
        return True
    else:
        return False

def rotate(vec, a):
    return np.dot(vec, [[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])

def transform(c_0, vec, coord):
    x, y = vec[0], vec[1]
    return 1 / np.sqrt(x ** 2 + y ** 2) * np.dot((np.array(coord) - np.array(c_0)), np.array([np.array([x, -y]), np.array([y, x])]))

def mag(vec): 
    return np.sqrt(np.sum(i**2 for i in vec))

def new_target():
    global DIFF
    x = randint(-100, -50) + randint(0, 1) * (width + 100)
    y = randint(100, height - 100)
    r = 10
    v = 100 * DIFF
    t = 1.5 / DIFF
    if prob((DIFF - 1) / 4):
        mode = "ADVANCED"
    else:
        mode = "NORMAL"
    return Target([x, y], r, v, t, mode)

class Flash_label:
    def __init__(self, text, time):
        self.counter = 0
        self.br = 0
        self.text = text
        self.time = time
        self.label = font.render(self.text, True, "BLACK")
    def show(self):
        if self.counter <= FPS * self.time:
            br = int(255 * (1 - self.counter / FPS / self.time))
            color = (br, 0, 0)
            del self.label
            self.label = font_large.render(self.text, True, color)
            screen.blit(self.label, [width / 2 - 150, height / 2 - 30])
            self.counter += 1
        else:
            del self



class Shell:
    def __init__(self, coord, impulse, ammo_type):
        self.destroyed = False
        self.ammo_type = ammo_type
        self.hp = 1

        if ammo_type == "AP":
            self.mass = ap_mass
            self.tr_len = ap_len
            self.hp = 2
        elif ammo_type == "HE":
            self.mass = he_mass
            self.tr_len = he_len
        elif ammo_type == "RCT":
            self.mass = rct_mass
            self.tr_len = rct_len
        elif ammo_type == "BMB":
            self.mass = bmb_mass
            self.tr_len = bmb_len

        self.coord = np.array(coord)
        self.tracer = [list(self.coord), list(self.coord), list(self.coord)]
        self.hitline = [list(self.coord), list(self.coord)]
        self.vel = np.array(impulse) / self.mass
    def __del__(self):
        pass
    def move(self, g):
        self.coord = self.coord + self.vel / FPS
        self.vel += np.array([0, g]) / FPS
        self.hitline.append(list(self.coord))
        del self.hitline[0]
        if self.ammo_type == "AP" or self.ammo_type == "HE" or self.ammo_type == "BMB":
            if not self.destroyed:
                self.tracer.append(list(self.coord))
            if len(self.tracer) > FPS * self.tr_len or (len(self.tracer) > 0 and self.destroyed):
                del self.tracer[0]
        elif self.ammo_type == "RCT":
            if self.mass >= 0.3 * rct_mass and not self.destroyed:
                self.mass -= rct_mass * rct_mu / FPS
                self.vel += (self.vel / mag(self.vel)) * rct_F / self.mass / FPS
                self.tracer.append(list(self.coord))
            if (len(self.tracer) > FPS * self.tr_len or self.mass < rct_mass * 0.3 or self.destroyed) and len(self.tracer) > 0 :
                del self.tracer[0]
    def draw(self, surface):
        for i in range(len(self.tracer) - 1):
            if len(self.tracer) > 3:
                if self.ammo_type == "AP" or self.ammo_type == "HE":
                    br = 10 + int(50 * (i) / self.tr_len / FPS)
                    color = (br, br, br)   
                    pg.draw.line(surface, color, self.tracer[i], self.tracer[i+1], 1)
                elif self.ammo_type == "BMB":
                    br = int(255 * (i) / self.tr_len / FPS)
                    color = (255 - br / 2, br / 2, 0) 
                    pg.draw.line(surface, color, self.tracer[i], self.tracer[i+1], int((i / len(self.tracer)) * 6))
                elif self.ammo_type == "RCT":
                    br = 10 + int(80 * (i) / self.tr_len / FPS)
                    color = (br, br, br)   
                    pg.draw.line(surface, color, self.tracer[i], self.tracer[i+1], int((1 - i / len(self.tracer)) * 15 + 3))
        if not self.destroyed:
            if self.ammo_type == "AP":
                pg.draw.circle(surface, "YELLOW", self.coord, 1)
            elif self.ammo_type == "HE":
                pg.draw.circle(surface, "RED", self.coord, 1)
            elif self.ammo_type == "BMB":
                pg.draw.circle(surface, "ORANGE", self.coord, 1)
            elif self.ammo_type == "RCT":
                if self.mass >= rct_mass * 0.3:
                    pg.draw.line(surface, "ORANGE", self.tracer[-1], self.tracer[-2], width=2)
                pg.draw.line(surface, "GREEN", self.coord, self.coord + (self.vel / mag(self.vel) * 1), width=6)
                pg.draw.line(surface, "GREY", self.coord, self.coord + (self.vel / mag(self.vel) * 10), width=2)
    def destroy(self):
        if not self.destroyed:
            self.hp -= 1
            if self.hp <= 0:
                self.destroyed = True
                if self.ammo_type == "RCT":
                    EXPLOSIONS.append(Explosion(list(self.hitline[0]), 500, 100))
                elif self.ammo_type == "AP":
                    EXPLOSIONS.append(Explosion(list(self.hitline[1]), 20, 0))
                elif self.ammo_type == "HE":
                    EXPLOSIONS.append(Explosion(list(self.hitline[0]), 100, 20))
                elif self.ammo_type == "BMB":
                    EXPLOSIONS.append(Explosion(list(self.hitline[0]), 100, 20))

class Tank:
    def __init__(self, x, spd, ang, impulse):
        self.x = x
        self.spd = spd
        self.ang = ang
        self.impulse = impulse
        self.dir = 0
        self.coord = np.array([x, height])
        self.radius = tank_size / 2
    def shoot(self, ammo_type):
        shell = (Shell([self.x, height - tank_size * 0.6], self.impulse * np.array([np.cos(self.ang), np.sin(self.ang)]), ammo_type))
        shell.vel[0] += self.dir * self.spd
        PROJECTILES.append(shell)

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
        self.dir = direction
        if self.x <= tank_size:
            self.x  = tank_size
            if self.dir == -1:
                self.dir = 0
        elif self.x >= width - tank_size:
            self.x = width - tank_size
            if self.dir == 1:
                self.dir = 0
        self.x += self.dir * self.spd / FPS
        self.coord[0] = self.x
    
    def is_shotdown(self, shell):
        if not shell.destroyed:
            coord_t = transform(shell.hitline[0], shell.vel, self.coord)
            if coord_t[0] > 0 and coord_t[0] < mag(np.array(shell.hitline[1]) - np.array(shell.hitline[0])) and np.abs(coord_t[1]) <= self.radius:
                shell.destroy()
                return 1
            else:
                return 0
        else:
            return 0
    def is_blownup(self, explosion):
        if mag(self.coord - np.array(explosion.coord)) <= explosion.effect_rad + self.radius:
            return 1
        else:
            return 0

class Target:
    def __init__(self, coord, radius, spd, wait, mode):
        self.coord = np.array(coord)
        self.mode = mode
        self.radius = radius
        self.wait = wait
        self.spd = spd
        self.timer = 0
        self.dest = self.coord
        self.shooting = False
        self.shot = False
        self.spawned = True
    def __del__(self):
        pass
    def is_shotdown(self, shell):
        if not shell.destroyed:
            coord_t = transform(shell.hitline[0], shell.vel, self.coord)
            if coord_t[0] > 0 and coord_t[0] < mag(np.array(shell.hitline[1]) - np.array(shell.hitline[0])) and np.abs(coord_t[1]) <= self.radius:
                shell.destroy()
                EXPLOSIONS.append(Explosion(self.coord, 10 * self.radius, 0.5 * self.radius))
                return True
            else:
                return False
    def is_blownup(self, explosion):
        if mag(self.coord - np.array(explosion.coord)) <= explosion.effect_rad + self.radius:
            return True
        else:
            return False
    def draw(self, surface, tank):
        if self.timer == 0:
            if self.spawned == True:
                self.shooting = False
                self.spawned = False
            else:
                self.shooting = (0 == randint(0, 2))
            self.dest = np.array([randint(50, width - 50), randint(100, height - 100)])
            self.timer += 1 / FPS
        elif self.timer < self.wait / 3:
            self.timer += 1 / FPS
        elif self.timer < self.wait:
            if self.shooting and not self.shot:
                if self.mode == "NORMAL":
                    PROJECTILES.append(Shell(self.coord + np.array([0, self.radius]), [bmb_mass * np.sqrt(1 / (2 * (height - self.coord[1] - self.radius) / g)) * (tank.x - self.coord[0]), 0], "BMB"))
                elif self.mode == "ADVANCED":
                    PROJECTILES.append(Shell(self.coord + np.array([0, self.radius]), [bmb_mass * np.sqrt(1 / (2 * (height - self.coord[1] - self.radius) / g)) * (tank.x + tank.spd * tank.dir * np.sqrt(2 * (height - self.coord[1] - self.radius) / g) - self.coord[0]), 0], "BMB"))
                self.shot = True
            self.timer += 1 / FPS
        elif self.timer >= self.wait:
            dist = (self.dest - self.coord)
            if mag(dist) >= self.radius:
                self.coord = self.coord + dist * self.spd / mag(dist) / FPS
            else:
                self.timer = 0
                self.shot = False
        if self.mode == "NORMAL":
            targetcolor = (100, 0, 0)
        elif self.mode == "ADVANCED":
            targetcolor = (100, 100, 0)
        if self.coord[0] > tank.x:       
            pg.draw.circle(surface, "#001066", self.coord + [- self.radius * 0.7, self.radius * 0.3], self.radius * 0.3)
            pg.draw.rect(surface, targetcolor, [[self.coord[0] - 0.7 * self.radius, self.coord[1]], [self.radius, self.radius * 0.6]])
            pg.draw.polygon(surface, targetcolor, [
                [self.coord[0] - 0.4 * self.radius, self.coord[1] + 0.4 * self.radius], 
                [self.coord[0] + 0.4 * self.radius, self.coord[1] + 0.4 * self.radius], 
                [self.coord[0] - 0.2 * self.radius, self.coord[1] + self.radius], 
                [self.coord[0] + 0.2 * self.radius, self.coord[1] + self.radius]
                ])
            pg.draw.line(surface, targetcolor, self.coord + np.array([0, self.radius * 0.1]), self.coord + np.array([1.5 * self.radius, self.radius * 0.1]), int(0.2 * self.radius))
            pg.draw.line(surface, "RED", self.coord + np.array([0.4 * self.radius, self.radius]), self.coord + np.array([-0.4 * self.radius, self.radius]), int(0.2 * self.radius))
            pg.draw.circle(surface, "#555555", self.coord + np.array([0, self.radius]), 0.2 * self.radius)
            pg.draw.ellipse(surface, "#555555", [self.coord + np.array([- 1.0 * self.radius, - 0.8 * self.radius]), [2.0 * self.radius, 0.6 * self.radius]])
            pg.draw.circle(surface, "GREY", self.coord + np.array([0, - self.radius * 0.5]), 0.1 * self.radius)
            pg.draw.circle(surface, "#555555", self.coord + np.array([1.5 * self.radius, self.radius * 0.1]), 0.4 * self.radius)
            pg.draw.circle(surface, "GREY", self.coord + np.array([1.5 * self.radius, self.radius * 0.1]), 0.1 * self.radius)
        else:
            pg.draw.circle(surface, "#001066", self.coord + [self.radius * 0.7, self.radius * 0.3], self.radius * 0.3)
            pg.draw.rect(surface, targetcolor, [[self.coord[0] - 0.3 * self.radius, self.coord[1]], [self.radius, self.radius * 0.6]])
            pg.draw.polygon(surface, targetcolor, [
                [self.coord[0] - 0.4 * self.radius, self.coord[1] + 0.4 * self.radius], 
                [self.coord[0] + 0.4 * self.radius, self.coord[1] + 0.4 * self.radius], 
                [self.coord[0] - 0.2 * self.radius, self.coord[1] + self.radius], 
                [self.coord[0] + 0.2 * self.radius, self.coord[1] + self.radius]
                ])
            pg.draw.line(surface, targetcolor, self.coord + np.array([0, self.radius * 0.1]), self.coord + np.array([-1.5 * self.radius, self.radius * 0.1]), int(0.2 * self.radius))
            pg.draw.line(surface, "RED", self.coord + np.array([-0.4 * self.radius, self.radius]), self.coord + np.array([0.4 * self.radius, self.radius]), int(0.2 * self.radius))
            pg.draw.circle(surface, "#555555", self.coord + np.array([0, self.radius]), 0.2 * self.radius)
            pg.draw.ellipse(surface, "#555555", [self.coord + np.array([-1.0 * self.radius, - 0.8 * self.radius]), [2.0 * self.radius, 0.6 * self.radius]])
            pg.draw.circle(surface, "GREY", self.coord + np.array([0, - self.radius * 0.5]), 0.1 * self.radius)
            pg.draw.circle(surface, "#555555", self.coord + np.array([-1.5 * self.radius, self.radius * 0.1]), 0.4 * self.radius)
            pg.draw.circle(surface, "GREY", self.coord + np.array([-1.5 * self.radius, self.radius * 0.1]), 0.1 * self.radius)
            

class Explosion:
    def __init__(self, coord, draw_rad, effect_rad):
        self.coord = coord
        self.rad = effect_rad
        self.draw_rad = draw_rad
        self.effect_rad = effect_rad
        self.br = 0
    def __del__(self):
        pass
    def draw(self, surface):
        if self.rad < self.draw_rad:
            self.br = 255 * (1 - self.rad / self.draw_rad)
            if self.br < 0:
                self.br = 0
            color1 = (self.br, self.br, self.br)
            pg.draw.circle(surface, color1, self.coord, int(self.rad))
            pg.draw.circle(surface, "BLACK", self.coord, int(self.rad - 1))

            self.rad += 500 / FPS
            return False
        else:
            return True
    def draw_effect(self, surface):
        color2 = (self.br, self.br, 0)
        pg.draw.circle(surface, color2 , self.coord, int(self.effect_rad))

class Pulse:
    def __init__(self, maxrad, coord):
        self.rad = 0
        self.timer = 0
        self.maxrad = maxrad
        self.coord = np.array(coord)
    def draw(self, surface, shell):
        if self.rad <= self.maxrad:
            self.br = int(100 + 155 * (1 - self.rad / self.maxrad))
            if self.br < 0:
                self.br = 0
            color1 = (0, self.br, self.br)
            pg.draw.circle(surface, color1, self.coord, int(self.rad))
            pg.draw.circle(surface, "BLACK", self.coord, int(self.rad - 2))
            self.rad += 500 / FPS
            for shell in PROJECTILES:
                if mag(shell.coord - self.coord) < self.rad:
                    shell.hp = 0
                    shell.destroy()
        else:
            del self


tank = Tank(10, 100, 0, 1000)

pg.init()
font = pg.font.SysFont("comicsansms", 30)
font_large = pg.font.SysFont("comicsansms", 60)
screen = pg.display.set_mode([width, height])
game_surface = pg.surface.Surface([width, height])
ammo_surface = pg.surface.Surface([width / 8, 60])
pulse_surface = pg.surface.Surface([width / 8, 60])

pg.display.update()
clock = pg.time.Clock()
finished = False

nuke = 0
ammo_n = 0
charge = 0
load = 1
pulse_load = 1
charging = False
PULSES.append(Pulse(750, tank.coord))
pg.mouse.set_visible(False)

while not finished:
    tank_hits = 0
    diff()
    while len(TARGETS) < targets_number:
        TARGETS.append(new_target())
    clock.tick(FPS)   
    screen.fill("BLACK") 
    game_surface.fill("BLACK")
    shooting = False
    left_pressed = False
    for event in pg.event.get():                               
        if event.type == pg.QUIT:
            finished = True
        if event.type == pg.MOUSEBUTTONDOWN:
            left, middle, right = pg.mouse.get_pressed()
            if right:
                detonating = True
            if left:
                charge = 0
                charging = True   
        if event.type == pg.MOUSEBUTTONUP:
            left, middle, right = pg.mouse.get_pressed()
            if not right:
                detonating = False 
            if (not left) and charging:
                charging = False
                shooting = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB:
                charge = 0
                load = 0
                if ammo_n < len(AMMO) - 1:
                    ammo_n += 1
                else:
                    ammo_n = 0
            if event.key == pg.K_SPACE:
                if pulse_load == 1:
                    PULSES.append(Pulse(200, tank.coord))
                    pulse_load = 0
        
    pulse_load += 1 / pulse_time / FPS
    if pulse_load > 1:
        pulse_load = 1
    
    if charging and (load == 1):
        charge += 1 / charge_time / FPS
        if charge > 1:
            charge = 1
            
    ammo_type = AMMO[ammo_n]

    keys = pg.key.get_pressed()
    if keys[pg.K_d]:
        tank.move(1)
    elif keys[pg.K_a]:
        tank.move(-1)
    else:
        tank.move(0)
    
    
    x, y = pg.mouse.get_pos()
    if (x - tank.x) == 0:
        tank.ang = 3 * np.pi / 2
    elif (x - tank.x) > 0:
        tank.ang = np.arctan((y - (height - tank_size * 0.6)) / (x - tank.x))
    else:
        tank.ang = np.pi + np.arctan((y - (height - tank_size * 0.6)) / (x - tank.x))

    if ammo_type == "RCT" and SCORE == 0:
        if shooting:
            FLASH_LABELS.append(Flash_label("NO AMMO", 0.5))
        shooting = False
        load = 0
        charge = 0
    else:
        load += 1 / load_time / FPS
        if load > 1:
            load = 1
        if shooting:
            shooting = (load == 1)

    if shooting:
        if ammo_type == "RCT":
            SCORE -= 1
            if SCORE < 0:
                SCORE = 0
        tank.impulse = charge * 800 + 200
        tank.shoot(ammo_type)
        load = 0
        charge = 0

    for explosion in EXPLOSIONS:
        stop = explosion.draw(game_surface)
        if stop:
            EXPLOSIONS.remove(explosion)
            del explosion
    
    for pulse in PULSES:
        pulse.draw(game_surface, PROJECTILES)


    for target in TARGETS:
        hit = False
        target.draw(game_surface, tank)
        for shell in PROJECTILES:
            if target.is_shotdown(shell):
                hit = True
        for explosion in EXPLOSIONS:
            if target.is_blownup(explosion):
                hit = True
        if hit:
            SCORE += 1
            TARGETS.remove(target)
            del target
                

    for shell in PROJECTILES:
        shell.move(g)
        shell.draw(game_surface)
        if shell.coord[1] > height and not shell.destroyed:
            shell.destroy()
        if len(shell.tracer) == 0:
            if shell.coord[1] > height:
                PROJECTILES.remove(shell)
                del shell
        elif shell.tracer[0][1] > height:
            PROJECTILES.remove(shell)
            del shell
    
    for shell in PROJECTILES:
        tank_hits += tank.is_shotdown(shell)
        if (shell.ammo_type == "RCT" or shell.ammo_type == "HE") and detonating:
            shell.destroy()

    shake = 0
    for explosion in EXPLOSIONS:                                                                                #EXPLOSION EFFECTS
        tank_hits += tank.is_blownup(explosion)
        shake += explosion.effect_rad
        explosion.draw_effect(game_surface)
        for shell in PROJECTILES:
            coord_t = transform(shell.hitline[0], shell.vel, explosion.coord)
            if coord_t[0] > 0 and coord_t[0] < mag(np.array(shell.hitline[1]) - np.array(shell.hitline[0])) and np.abs(coord_t[1]) <= explosion.effect_rad:
                shell.destroy()


    tank.draw(game_surface)
    shake += nuke
    if shake == 0:
        game_x = 0
        game_y = 0
    else:
        game_x = randint(- int(shake / 10), int(shake / 10))
        game_y = randint(- int(shake / 10), int(shake / 10))
    
    screen.blit(game_surface, [game_x, game_y])


    #HUD
    for label in FLASH_LABELS:
        label.show()

    if (SCORE == 0) and (ammo_type == "RCT"):
        loadcolor = "RED"
    elif load < 1:
        loadcolor = "ORANGE"
    else:
        loadcolor = "GREEN"

    if charge < 1:
        r_charge = int((1 - charge) * 255)
        g_charge = int(charge * 255)
        chargecolor = (r_charge, g_charge, 0)
    else:
        chargecolor = "CYAN"

    if pulse_load < 1:
        r_load = int((1 - pulse_load) * 255)
        g_load = int(pulse_load * 255)
        pulsecolor = (r_load, g_load, 0)
    else:
        pulsecolor = "CYAN"

    if nuke > 0:
        charge = 0
        load = 0
        pulse_load = 0
        pulsecolor = "RED"
        chargecolor = "RED"
        loadcolor = "RED"

    label1 = font.render(f"SCORE: {SCORE}", True, loadcolor)
    label2 = font.render(f"AMMO: {ammo_type}", True, loadcolor)
    screen.blit(label1, [20, 20])
    screen.blit(label2, [width - 190, 20])

    pg.draw.rect(screen, loadcolor, [[width / 3 - 4, 16], [width / 3 + 8, 18]])
    pg.draw.rect(screen, "BLACK", [[width / 3 - 2, 18], [width / 3 + 4, 14]])
    pg.draw.rect(screen, loadcolor, [[width / 2, 20], [width / 6 * load, 10]])
    pg.draw.rect(screen, loadcolor, [[width / 3, 20], [width / 6, 10]])
    pg.draw.rect(screen, "BLACK", [[width / 3, 20], [width / 6 * (1 - load), 10]])

    pg.draw.rect(screen, chargecolor, [[width - 16 - 18, height / 3 - 4], [18, height / 3 + 8]])
    pg.draw.rect(screen, "BLACK", [[width - 18 - 14, height / 3 - 2], [14, height / 3 + 4]])
    pg.draw.rect(screen, chargecolor, [[width - 20 - 10, height / 3], [10, height / 3]])
    pg.draw.rect(screen, "BLACK", [[width - 20 - 10, height / 3], [10, height / 3 * (1 - charge)]])

    pg.draw.rect(screen, chargecolor, [[16, height / 3 - 4], [18, height / 3 + 8]])
    pg.draw.rect(screen, "BLACK", [[18, height / 3 - 2], [14, height / 3 + 4]])
    pg.draw.rect(screen, chargecolor, [[20, height / 3], [10, height / 3]])
    pg.draw.rect(screen, "BLACK", [[20, height / 3], [10, height / 3 * (1 - charge)]])

    #PULSE ICON
    pulse_surface.fill(pulsecolor)
    pg.draw.rect(pulse_surface, "BLACK", [[1, 1], [width / 8 - 2, 58]])
    pg.draw.polygon(pulse_surface, pulsecolor, [
        [20, 15], 
        [20, 45], 
        [width / 8 - 50, 45],
        [width / 8 - 20, 30],
        [width / 8 - 50, 15]
        ], 2)

    pg.draw.line(pulse_surface, "BLACK", [1 + 40, 1 + 5], [width / 8 - 2 + 1 - 40, 1 + 58 - 5], 9)
    pg.draw.line(pulse_surface, "BLACK", [1 + 40, 1 + 58 - 5], [width / 8 - 2 + 1 - 40, 1 + 5], 9)
    pg.draw.line(pulse_surface, pulsecolor, [1 + 40, 1 + 5], [width / 8 - 2 + 1 - 40, 1 + 58 - 5], 3)
    pg.draw.line(pulse_surface, pulsecolor, [1 + 40, 1 + 58 - 5], [width / 8 - 2 + 1 - 40, 1 + 5], 3)
    screen.blit(pulse_surface, [0.18 * width, 20])

    #AMMO ICON
    ammo_surface.fill(loadcolor)
    pg.draw.rect(ammo_surface, "BLACK", [[1, 1], [width / 8 - 2, 58]])
    if ammo_type == "HE":
        pg.draw.polygon(ammo_surface, loadcolor, [
            [width / 8 - 20, 15], 
            [width / 8 - 20, 45], 
            [70, 45],
            [40, 40],
            [20, 30],
            [40, 20],
            [70, 15]
            ], 2)
        pg.draw.line(ammo_surface, loadcolor, [40, 40], [40, 20], 2)
        pg.draw.line(ammo_surface, loadcolor, [90, 15], [90, 45], 2) 
        pg.draw.line(ammo_surface, loadcolor, [95, 15], [95, 45], 2)
        pg.draw.line(ammo_surface, loadcolor, [100, 15], [100, 45], 2)         
    elif ammo_type == "AP":
        pg.draw.polygon(ammo_surface, loadcolor, [
            [width / 8 - 20, 20], 
            [width / 8 - 20, 40],
            [100, 33],
            [70, 33],
            [20, 30],
            [70, 27],
            [100, 27]
            ], 2)
        pg.draw.polygon(ammo_surface, "BLACK", [
            [90, 40],
            [80, 40],
            [80, 20],
            [90, 20]
            ])
        pg.draw.polygon(ammo_surface, loadcolor, [
            [90, 40],
            [80, 40],
            [80, 20],
            [90, 20]
            ], 2)
        pg.draw.line(ammo_surface, loadcolor, [width / 8 - 20, 27], [100, 27], 2)
        pg.draw.line(ammo_surface, loadcolor, [width / 8 - 20, 33], [100, 33], 2)
        pg.draw.line(ammo_surface, loadcolor, [width / 8 - 20, 30], [100, 30], 1)
        pg.draw.line(ammo_surface, loadcolor, [85, 37], [85, 23], 2)
    elif ammo_type == "RCT":
        pg.draw.polygon(ammo_surface, loadcolor, [
            [width / 8 - 20, 10], 
            [width / 8 - 20, 50],
            [100, 37],
            [70, 37],
            [70, 45],
            [60, 37],
            [50, 37],
            [20, 30],
            [50, 23],
            [60, 23],
            [70, 15],
            [70, 23],
            [100, 23]
            ], 2)
        pg.draw.polygon(ammo_surface, loadcolor, [
            [width / 8 - 20, 25], 
            [width / 8 - 20, 35],
            [width / 8 - 15, 37],
            [width / 8 - 15, 23]
            ], 2)
        pg.draw.line(ammo_surface, loadcolor, [50, 37], [width / 8 - 20, 37], 2)
        pg.draw.line(ammo_surface, loadcolor, [50, 23], [width / 8 - 20, 23], 2)
        pg.draw.line(ammo_surface, loadcolor, [100, 30], [width / 8 - 20, 30], 2)
        pg.draw.line(ammo_surface, loadcolor, [60, 30], [70, 30], 2)
        pg.draw.line(ammo_surface, loadcolor, [50, 37], [50, 23], 2)    
    screen.blit(ammo_surface, [2 * width / 3 + width / 3 - 0.18 * width - width / 8, 20])

    #CURSOR
    pg.draw.circle(screen, chargecolor, [x, y], 2)
    pg.draw.line(screen, chargecolor, [x + 9, y - 4], [x + 9, y + 4], 1)
    pg.draw.line(screen, chargecolor, [x - 10, y - 4], [x - 10, y + 4], 1)

    if nuke > 3 * width:
        finished = True
    elif nuke > 0:
        nuke += 30
        pg.draw.circle(screen, "WHITE", tank.coord, nuke)

    pg.display.update()
    if tank_hits >= 1 and nuke == 0:
        nuke = 1

screen.fill("WHITE")
pg.display.update()
font_huge = pg.font.SysFont("mscomicsans", 200)
finished = False
timer = 0
while not finished:
    clock.tick(FPS)
    timer += 1 / FPS
    if timer > 2:
        timer = 2

    if timer < 1:
        screen.fill((int(255 - timer * 255), int(255 - timer * 255), int(255 - timer * 255)))
    else:
        screen.fill("BLACK")
    
    for event in pg.event.get():                               
        if event.type == pg.QUIT:
            finished = True
        if event.type == pg.KEYDOWN:
            finished = True
        if event.type == pg.MOUSEBUTTONDOWN:
            finished = True

    if timer >= 1:
        final_label = font_huge.render("YOU DIED", True, (int((timer - 1) * 255), 0, 0))
        screen.blit(final_label, [width / 2 - 340, height / 2 - 150])
    if timer >= 2:
        score_label = font_large.render(f"YOUR FINAL SCORE: {SCORE}", True, "RED")
        screen.blit(score_label, [width / 2 - (330 + 17 * (len(str(SCORE))) - 1), height / 2 + 50])
    
    pg.display.update()

pg.quit()
