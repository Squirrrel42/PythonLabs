import pygame as pg
Shotgun_tex = []
Surfaces = []
FPS = 60
for i in range(1, 14):
    surface = pg.surface.Surface([1200, 800], pg.SRCALPHA)
    surface.blit(pg.image.load(f"sprites/Shotgun/shotgun{i}.png"), [0, 24])
    Surfaces.append(surface)
class Weapon:
    def __init__(self) -> None:
        self.state = 0
        self.timer = 0
    def draw(self, surface, shooting):
        if self.state == 0:
            if shooting:
                self.state = 1
                self.timer = 0
            surface.blit(Surfaces[0], [0, 0])
        else:
            self.state = 2
            surface.blit(Surfaces[int(self.timer * 8) + 1], [0, 0])
            self.timer += 1 / FPS
            if self.timer > 1.5:
                self.state = 0


            
        

