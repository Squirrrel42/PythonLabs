import pygame as pg                 #imports
from pygame import draw
from random import randrange, randint, random
import multiprocessing as mp
import numpy as np


width = 1000
heigth = 700

pg.init()

balls_number = 5
FPS = 60
g = 500                     #gravity force acceleration
coll_loss = 0              #energy loss via collisions
screen = pg.display.set_mode([width, heigth])



RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
EDGE = (150, 150, 150)
COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]




class Ball:
    def __init__(self, coord, vel, rad, color, cost):
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.color = color
        self.cost = cost
    def caught(self, x, y):
        return (self.rad ** 2) >= ((self.coord[0] - x) ** 2 + (self.coord[1] - y) ** 2)
    def move(self):
        self.coord = self.coord + self.vel * (1 / FPS)
    def wall_collide(self, wall_x, wall_y):
        if   (((self.coord[0] - self.rad) < wall_x[0]) and (self.vel[0] < 0)) or (((self.coord[0] + self.rad) > wall_x[1]) and (self.vel[0] > 0)):
            self.vel[0] = - self.vel[0] * np.sqrt(1 - coll_loss)
        elif (((self.coord[1] - self.rad) < wall_y[0]) and (self.vel[1] < 0)) or (((self.coord[1] + self.rad) > wall_y[1]) and (self.vel[1] > 0)):
            self.vel[1] = - self.vel[1] * np.sqrt(1 - coll_loss)

def new_ball():
    x = 100 + random() * 800
    y = 100 + random() * 500
    r = 10 + random() * 40
    v_x = -500 + random() * 1000
    v_y = -500 + random() * 1000
    color = COLORS[randint(0, 5)]
    cost = 1
    ball = Ball(np.array([x, y]), np.array([v_x, v_y]), r, color, cost)
    return ball

def draw_ball(screen, ball):
    pg.draw.circle(screen, EDGE, ball.coord, ball.rad)
    pg.draw.circle(screen, ball.color, ball.coord, ball.rad - 2)

def debug(balls):
    for ball in balls:
        print(ball.coord) 



pg.display.set_caption("IF YOU READ THIS KNOW THAT THE BALLS' ENERGY IS SOMEHOW ICREASING")
font = pg.font.SysFont("comicsansms", 30)
font2 = pg.font.SysFont("comicsansms", 60)

pg.display.update()
clock = pg.time.Clock()
finished = False
balls = []
score = 0
label2 = font2.render("CLICK THOSE CIRCLES!", True, "WHITE")

for i in range(balls_number):
    ball = new_ball()
    draw_ball(screen, ball)
    balls.append(ball)   



while not finished:
    clock.tick(FPS)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            finished = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            x, y = pg.mouse.get_pos()
            for i in range(len(balls)):
                if balls[i].caught(x, y) == True: 
                    balls[i] = new_ball()
                    score += balls[i].cost
        
    screen.fill(BLACK) 

    for i in range(len(balls)):
        balls[i].wall_collide([0, width], [0, heigth])
        balls[i].move()
        draw_ball(screen, balls[i])
        balls[i].vel[1] += g * (1 / FPS) 

    if score == 0:
        screen.blit(label2, [width / 2 - 340, heigth / 2 - 50])
    
    label = font.render(f"SCORE: {score}", True, "WHITE")
    screen.blit(label, [10, 0])
    
    pg.display.update()

            

pg.quit()
