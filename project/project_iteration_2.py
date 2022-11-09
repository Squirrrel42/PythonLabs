import pygame as pg
import numpy as np

width = 1200
heigth = 800
FOV = 60 
sen = 2
rays_number = 120
fov_rad = FOV * np.pi / 180
scale = width / fov_rad
MODE = "3D"
wall_heigth = 48
colors = ["BLACK", "WHITE"]


Level = np.array([                                       #Square only
    np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
    np.array([1, 0, 0, 1, 0, 0, 0, 0, 0, 1]),
    np.array([1, 0, 0, 1, 0, 1, 0, 1, 0, 1]),
    np.array([1, 0, 1, 1, 0, 1, 1, 1, 0, 1]),
    np.array([1, 0, 0, 0, 0, 0, 1, 0, 0, 1]),
    np.array([1, 0, 0, 0, 0, 0, 1, 0, 0, 1]),
    np.array([1, 0, 1, 1, 1, 1, 1, 0, 0, 1]),
    np.array([1, 0, 1, 0, 0, 0, 1, 0, 0, 1]),
    np.array([1, 0, 0, 0, 1, 0, 0, 0, 0, 1]),
    np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
])

lw = len(Level)
mapscale = (heigth / (lw * 64))


def rotate(vec, ang):
    return np.dot(vec, [[np.cos(ang), np.sin(ang)], [-np.sin(ang), np.cos(ang)]])

def move_controls(alpha):
    move = False
    keys = pg.key.get_pressed()
    if keys[pg.K_w] and keys[pg.K_d]:
        alpha += (np.pi / 4)
        move = True
    elif keys[pg.K_d] and keys[pg.K_s]:
        alpha += (3 * np.pi / 4)
        move = True
    elif keys[pg.K_s] and keys[pg.K_a]:
        alpha += (5 * np.pi / 4)
        move = True
    elif keys[pg.K_a] and keys[pg.K_w]:
        alpha += (7 * np.pi / 4)
        move = True
    elif keys[pg.K_w]:
        alpha += (0)
        move = True
    elif keys[pg.K_d]:
        alpha += (np.pi * 0.5)
        move = True
    elif keys[pg.K_s]:
        alpha += (np.pi)
        move = True
    elif keys[pg.K_a]:
        alpha += (np.pi * 1.5)
        move = True
    return alpha, move

def mag(vec): 
    return np.sqrt(np.sum(i**2 for i in vec))
    

class Player:
    def __init__(self, coord, ang, spd, omega):
        self.coord = np.array(coord)
        self.ang = -ang
        self.spd = spd
        self.omega = omega
    def move(self, angle):
        self.coord = self.coord + self.spd / FPS * rotate([1, 0], angle)
    def rotate(self, dirc):
        self.ang += dirc / FPS * self.omega
        if self.ang > 2 * np.pi:
            self.ang -= 2 * np.pi
        elif self.ang < 0:
            self.ang += 2 * np.pi
    def collision(self, i, j, angle):
        shift = rotate([2 * self.spd / FPS, 0], angle)
        return[
            (self.coord[0] <= 64 * (i + 1) + 2 * self.spd / FPS) and (self.coord[0] >= 64 * i - 2 * self.spd / FPS) and (self.coord[1] >= 64 * j - 2 * self.spd / FPS) and (self.coord[1] <= 64 * (j + 1) + 2 * self.spd / FPS),
            (self.coord[0] + shift[0] <= 64 * (i + 1) +  2 * self.spd / FPS) and (self.coord[0] + shift[0] >= 64 * i -  2 * self.spd / FPS) and (self.coord[1] + shift[1] >= 64 * j -  2 * self.spd / FPS) and (self.coord[1] + shift[1] <= 64 * (j + 1) +  2 * self.spd / FPS)
        ]
    def increase_ang(self, value):
        self.ang += value
        if self.ang > 2 * np.pi:
            self.ang -= 2 * np.pi
        elif self.ang < 0:
            self.ang += 2 * np.pi


obs = Player([550, 250], np.pi / 2, 200, 5)

pg.init()
FPS = 60
screen = pg.display.set_mode([width, heigth])
clock = pg.time.Clock()
finished = False
pg.display.set_caption("RAYCASTER")
font = pg.font.SysFont("comicsansms", 30)
pg.mouse.set_visible(False)

while not finished: 
    clock.tick(FPS)

    for event in pg.event.get():                                
        if event.type == pg.QUIT:
            finished = True
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB:
                if MODE == "3D":
                    MODE = "Map"
                else:
                    MODE = "3D"
    
    pcol = "GREEN"
    alpha, move = move_controls(obs.ang)
    for i in range(lw):
        for j in range(lw):
            if (Level[j][i] > 0) and obs.collision(i, j, alpha)[0]:
                pcol = "YELLOW"
                if obs.collision(i, j, alpha)[1]:
                    move = False
                    pcol = "RED"

    keys = pg.key.get_pressed()
    if keys[pg.K_RIGHT]:
        obs.rotate(1)
    elif keys[pg.K_LEFT]:
        obs.rotate(-1)

    if MODE == "3D":
        obs.increase_ang(sen * pg.mouse.get_rel()[0] / scale)
        pg.mouse.set_pos([width / 2, heigth / 2])
        

    if move:
        obs.move(alpha)

    if MODE == "3D":
        screen.fill("#444444")
        pg.draw.rect(screen, "#666666", [[0, 0], [width, heigth / 2]])
    elif MODE == "Map":
        screen.fill("#444444")
        for i in range(lw):
            for j in range(lw):
                pg.draw.rect(screen, colors[Level[j][i]], [[64 * mapscale * i + 1, 64 * mapscale * j + 1], [64 * mapscale - 2, 64 * mapscale - 2]]) 

    #RAYCASTING
    for offset in np.linspace(- fov_rad / 2, fov_rad / 2, rays_number):
        angle = offset + obs.ang
        if angle > 2 * np.pi:
            angle -= 2 * np.pi
        elif angle < 0:
            angle += 2 * np.pi

            #HORIZONTAL
        if (angle > np.pi and angle < 2 * np.pi):             #UP
            j = int(obs.coord[1] // 64 - 1)
            y = 64 * (j + 1)
            x = obs.coord[0] - 1 / np.tan(angle) * (obs.coord[1] - y)
            i = int(x // 64)
            if i in range(lw) and j in range(lw):
                stopped = (Level[j][i] > 0)
                while not stopped:
                    x -= 64 / np.tan(angle)
                    y -= 64
                    i = int(x // 64)
                    j = int(y // 64) - 1
                    if i in range(lw) and j in range(lw):
                        stopped = (Level[j][i] > 0)
                    else:
                        stopped = True
                        y = -1000000
                        x = obs.coord[0] - 1 / np.tan(angle) * (obs.coord[1] - y)
            else:
                y = -1000000
                x = obs.coord[0] - 1 / np.tan(angle) * (obs.coord[1] - y)

        else:                                                                                          #DOWN
            j = int(obs.coord[1] // 64) + 1
            y = 64 * (j)
            x = obs.coord[0] - 1 / np.tan(angle) * (obs.coord[1] - y)
            i = int(x // 64)
            if i in range(lw) and j in range(lw):
                stopped = (Level[j][i] > 0)
                while not stopped:
                    x += 64 / np.tan(angle)
                    y += 64
                    i = int(x // 64)
                    j = int(y // 64)
                    if i in range(lw) and j in range(lw):
                        stopped = (Level[j][i] > 0)
                    else:
                        stopped = True
                        y = 1000000
                        x = obs.coord[0] - 1 / np.tan(angle) * (obs.coord[1] - y)
            else:
                y = 1000000
                x = obs.coord[0] - 1 / np.tan(angle) * (obs.coord[1] - y)

        hor_vec = np.array([x, y]) - obs.coord

            #VERTICAL
        if (angle > 0.5 * np.pi and angle < 1.5 * np.pi):             #LEFT
            i = int(obs.coord[0] // 64 - 1)
            x = 64 * (i + 1)
            y = obs.coord[1] + (x - obs.coord[0]) * np.tan(angle)
            j = int(y // 64)
            if i in range(lw) and j in range(lw):
                stopped = (Level[j][i] > 0)
                while not stopped:
                    x -= 64
                    y -= 64 * np.tan(angle)
                    i = int(x // 64 - 1)
                    j = int(y // 64)
                    if i in range(lw) and j in range(lw):
                        stopped = (Level[j][i] > 0)
                    else:
                        stopped = True
                        x = -1000000
                        y = obs.coord[1] + (x - obs.coord[0]) * np.tan(angle)
            else:
                x = -1000000
                y = obs.coord[1] + (x - obs.coord[0]) * np.tan(angle)

        else:                                                                                 #RIGHT
            i = int(obs.coord[0] // 64) + 1
            x = 64 * (i)
            y = obs.coord[1] + (x - obs.coord[0]) * np.tan(angle)
            j = int(y // 64)
            if i in range(lw) and j in range(lw):
                stopped = (Level[j][i] > 0)
                while not stopped:
                    x += 64
                    y += 64 * np.tan(angle)
                    i = int(x // 64)
                    j = int(y // 64)
                    if i in range(lw) and j in range(lw):
                        stopped = (Level[j][i] > 0)
                    else:
                        stopped = True
                        x = 1000000
                        y = obs.coord[1] + (x - obs.coord[0]) * np.tan(angle)
            else:
                x = 1000000
                y = obs.coord[1] + (x - obs.coord[0]) * np.tan(angle)

        ver_vec = np.array([x, y]) - obs.coord

        if mag(ver_vec) > mag(hor_vec):
            if MODE == "Map":
                pg.draw.line(screen, "#004400", obs.coord * mapscale, (obs.coord + hor_vec) * mapscale)
            elif MODE == "3D":
                pg.draw.line(screen, "#004400", [(offset + fov_rad / 2) * scale, heigth / 2 - wall_heigth / mag(hor_vec) / np.cos(offset) * scale * 1 / 2], [(offset + fov_rad / 2) * scale, heigth / 2 + wall_heigth / mag(hor_vec) / np.cos(offset) * scale * 1 / 2], int(width / rays_number) + 1)
        else:
            if MODE == "Map":
                pg.draw.line(screen, "#003300", obs.coord * mapscale, (obs.coord + ver_vec) * mapscale)
            elif MODE == "3D":
                pg.draw.line(screen, "#003300", [(offset + fov_rad / 2) * scale, heigth / 2 - wall_heigth / mag(ver_vec) / np.cos(offset) * scale * 1 / 2], [(offset + fov_rad / 2) * scale, heigth / 2 + wall_heigth / mag(ver_vec) / np.cos(offset) * scale * 1 / 2], int(width / rays_number) + 1)
    
    if MODE == "Map":
        pg.draw.circle(screen, pcol, obs.coord * mapscale, 5)

    pg.display.update()

            

pg.quit()


    
