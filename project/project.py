import pygame as pg
import numpy as np

FoV_deg = 100
fov = FoV_deg / 180 * np.pi
del_ang = 3


def transform(c_0, vec, coord):
    x, y = vec[0], vec[1]
    return 1 / np.sqrt(x ** 2 + y ** 2) * np.dot((coord - c_0), np.array([np.array([x, -y]), np.array([y, x])]))

class Wall:
    def __init__(self, c_a, c_b, color):
        self.c_a = np.array(c_a)
        self.c_b = np.array(c_b)
        self.color = color

class Ray:
    def __init__(self, c_0, vec_0, ang):
        self.c_0 = c_0
        self.vec = np.dot(vec_0, [[np.cos(ang), np.sin(ang)], [-np.sin(ang), np.cos(ang)]])
    def cross(self, wall):
        y_a = transform(self.c_0, self.vec, wall.c_a)[1]
        y_b = transform(self.c_0, self.vec, wall.c_b)[1]
        x_a = transform(self.c_0, self.vec, wall.c_a)[0]
        x_b = transform(self.c_0, self.vec, wall.c_b)[0]
        if (y_a * y_b) < 0:
            r = (x_a + np.abs(y_a) / (np.abs(y_a) + np.abs(y_b)) * (x_b - x_a))
            if r >= 0:
                return r
            else:
                return -1000000
        else:
            return -1000000

class Observer:
    def __init__(self, coord, direct, vel):
        self.coord = np.array(coord)
        self.direct = np.array(direct)
        self.vel = vel
    def raycast(self, walls):
        angles = np.linspace(-fov / 2, fov / 2, 250)
        dist = []
        walls_color = []
        for wall in walls:
            walls_color.append(wall.color)
        for a in angles:
            ray_dist = []
            for wall in walls:
                ray_dist.append(Ray(self.coord, self.direct, a).cross(wall))
            r_i = np.argmin(np.abs(np.array(ray_dist)))
            r = ray_dist[r_i]
            color = walls_color[r_i]
            if r > 0:
                dist.append([a, r, color])
        return dist
    def move(self, angle):
        self.coord = self.coord + self.vel * np.dot(self.direct, [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]) / FPS

            
wall1 = Wall([0, 0], [0, 2], "WHITE")
wall2 = Wall([0, 0], [5, 0], "GREY")
wall3 = Wall([5, 5], [5, 0], "WHITE")
wall4 = Wall([5, 5], [0, 5], "GREY")
wall5 = Wall([0, 3], [0, 5], "WHITE")
walls = [wall1, wall2, wall3, wall4, wall5]
obs = Observer([0, 0], [1, 1], 5)



width = 1000
heigth = 700

scale = width / fov

pg.init()
FPS = 60
screen = pg.display.set_mode([width, heigth])
clock = pg.time.Clock()
h = 1

finished = False
while not finished:
    clock.tick(FPS)     

    for event in pg.event.get():                                
        if event.type == pg.QUIT:
            finished = True
        
    keys = pg.key.get_pressed()
    if keys[pg.K_RIGHT]:
        obs.direct = np.dot(obs.direct, [[np.cos(del_ang / FPS), np.sin(del_ang / FPS)], [-np.sin(del_ang / FPS), np.cos(del_ang / FPS)]])
    elif keys[pg.K_LEFT]:
        obs.direct = np.dot(obs.direct, [[np.cos(-del_ang / FPS), np.sin(-del_ang / FPS)], [-np.sin(-del_ang / FPS), np.cos(-del_ang / FPS)]])
    elif keys[pg.K_w] and keys[pg.K_d]:
        obs.move(np.pi / 4)
    elif keys[pg.K_d] and keys[pg.K_s]:
        obs.move(3 * np.pi / 4)
    elif keys[pg.K_s] and keys[pg.K_a]:
        obs.move(5 * np.pi / 4)
    elif keys[pg.K_a] and keys[pg.K_w]:
        obs.move(7 * np.pi / 4)
    elif keys[pg.K_w]:
        obs.move(0)
    elif keys[pg.K_d]:
        obs.move(np.pi * 0.5)
    elif keys[pg.K_s]:
        obs.move(np.pi)
    elif keys[pg.K_a]:
        obs.move(np.pi * 1.5)

    screen.fill("BLACK")
    pg.draw.rect(screen, "CYAN", [[0, 0], [width, heigth / 2]])
    pg.draw.rect(screen, "YELLOW", [[0, heigth / 2], [width, heigth]])
    for i in obs.raycast(walls):
        pg.draw.line(screen, i[2], [i[0] * scale + width / 2, heigth / 2 - np.arctan(0.5 * h / i[1]) * scale], [i[0] / fov * width + width / 2, heigth / 2 + np.arctan(0.5 * h / i[1]) * scale], width=5)
    

    pg.display.update()

            

pg.quit()

