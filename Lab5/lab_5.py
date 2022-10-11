import numpy as np
import matplotlib.pyplot as plt
def mandelbrot(x_low, x_high, y_low, y_high, points_x, points_y):
    re = np.linspace(x_low, x_high, points_x)
    im = np.linspace(y_low, y_high, points_y).reshape((-1, 1))
    c = re + im * 1j
    z = np.zeros((points_x, points_y))
    img = np.zeros((points_x, points_y))
    for i in range(200):
        z = z ** 2 + c
        img[(np.abs(z) > 2)] = np.log(i)
    return img
        
    pass

mandelbrot1 = mandelbrot(-2, 2, -2, 2, 4000, 4000)

plt.figure(figsize=[10, 10])
plt.imshow(mandelbrot1, cmap='magma')
plt.plot()