import numpy as np

FPS = 60


def rotate(vec, ang):
    return np.dot(vec, [[np.cos(ang), np.sin(ang)], [-np.sin(ang), np.cos(ang)]])


class Enemy:
    def __init__(self, coord, spd):
        self.coord = np.array(coord)
        self.spd = spd
        self.angle = 0
        print("first ", np.shape(self.coord))

    def move(self, obs, Level):
        # vector to player and angle between this vector and Ox
        vect = obs.coord - self.coord
        self.angle = np.arctan2(vect[1], vect[0])

        # position in Level
        i = int(self.coord[0] / 64)
        j = int(self.coord[1] / 64)

        # checking collisions
        # shift is next position of enemy
        shift = self.coord + 3 * self.spd / FPS * rotate([1, 0], self.angle)

        i_next = int(shift[0] / 64)
        j_next = int(shift[1] / 64)

        if j_next != j or i_next != i:
            angle_pos = np.arctan2(j_next - j, i_next - i)

            if Level[j_next][i_next] > 0:
                if self.angle >= angle_pos:
                    self.angle = angle_pos + np.pi / 2
                else:
                    self.angle = angle_pos - np.pi / 2

        self.coord = self.coord + self.spd / FPS * rotate([1, 0], self.angle)

        return [i * 64 + 32, j * 64 + 32, i_next * 64 + 32, j_next * 64 + 32]
