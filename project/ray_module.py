import numpy as np
def ray(lmap, coord, angle):
    coord = np.array(coord)
    lw = len(lmap)
            #HORIZONTAL
    if (angle > np.pi and angle < 2 * np.pi):             #UP
        j = int(coord[1] // 64 - 1)
        y = 64 * (j + 1)
        x = coord[0] - 1 / np.tan(angle) * (coord[1] - y)
        i = int(x // 64)
        if i in range(lw) and j in range(lw):
            stopped = (lmap[j][i] > 0)
            while not stopped:
                x -= 64 / np.tan(angle)
                y -= 64
                i = int(x // 64)
                j = int(y // 64) - 1
                if i in range(lw) and j in range(lw):
                    stopped = (lmap[j][i] > 0)
                else:
                    stopped = True
                    y = -1000000
                    x = coord[0] - 1 / np.tan(angle) * (coord[1] - y)
            if i in range(lw) and j in range(lw):
                hor_cell = [lmap[j][i], x % 64]
        else:
            y = -1000000
            x = coord[0] - 1 / np.tan(angle) * (coord[1] - y)
    else:                                                                                          #DOWN
        j = int(coord[1] // 64) + 1
        y = 64 * (j)
        x = coord[0] - 1 / np.tan(angle) * (coord[1] - y)
        i = int(x // 64)
        if i in range(lw) and j in range(lw):
            stopped = (lmap[j][i] > 0)
            while not stopped:
                x += 64 / np.tan(angle)
                y += 64
                i = int(x // 64)
                j = int(y // 64)
                if i in range(lw) and j in range(lw):
                    stopped = (lmap[j][i] > 0)
                else:
                    stopped = True
                    y = 1000000
                    x = coord[0] - 1 / np.tan(angle) * (coord[1] - y)
            if i in range(lw) and j in range(lw):
                hor_cell = [lmap[j][i], 64 - x % 64]
        else:
            y = 1000000
            x = coord[0] - 1 / np.tan(angle) * (coord[1] - y)
    if not(i in range(lw) and j in range(lw)):
        hor_cell = [0, 0]
    hor_vec = np.array([x, y]) - coord
        #VERTICAL
    if (angle > 0.5 * np.pi and angle < 1.5 * np.pi):             #LEFT
        i = int(coord[0] // 64 - 1)
        x = 64 * (i + 1)
        y = coord[1] + (x - coord[0]) * np.tan(angle)
        j = int(y // 64)
        if i in range(lw) and j in range(lw):
            stopped = (lmap[j][i] > 0)
            while not stopped:
                x -= 64
                y -= 64 * np.tan(angle)
                i = int(x // 64 - 1)
                j = int(y // 64)
                if i in range(lw) and j in range(lw):
                    stopped = (lmap[j][i] > 0)
                else:
                    stopped = True
                    x = -1000000
                    y = coord[1] + (x - coord[0]) * np.tan(angle)
            if i in range(lw) and j in range(lw):
                ver_cell = [lmap[j][i], 64 - y % 64]
        else:
            x = -1000000
            y = coord[1] + (x - coord[0]) * np.tan(angle)
    else:                                                                                 #RIGHT
        i = int(coord[0] // 64) + 1
        x = 64 * (i)
        y = coord[1] + (x - coord[0]) * np.tan(angle)
        j = int(y // 64)
        if i in range(lw) and j in range(lw):
            stopped = (lmap[j][i] > 0)
            while not stopped:
                x += 64
                y += 64 * np.tan(angle)
                i = int(x // 64)
                j = int(y // 64)
                if i in range(lw) and j in range(lw):
                    stopped = (lmap[j][i] > 0)
                else:
                    stopped = True
                    x = 1000000
                    y = coord[1] + (x - coord[0]) * np.tan(angle)
            if i in range(lw) and j in range(lw):
                ver_cell = [lmap[j][i], y % 64]
        else:
            x = 1000000
            y = coord[1] + (x - coord[0]) * np.tan(angle)
    if not (i in range(lw) and j in range(lw)):
        ver_cell = [0, 0]
    ver_vec = np.array([x, y]) - coord
    return hor_vec, ver_vec, hor_cell, ver_cell