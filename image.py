import sympy
import numpy as np
from PIL import Image
import sys
import importlib

import mathstuffs
importlib.reload(mathstuffs)

RESOLUTION = 8

u,v = sympy.symbols("s t", real=True)

transform = None
sqtwo = sympy.sqrt(2)
x_, y_ = sympy.symbols("x y")
transX = sympy.lambdify((x_,y_),((x_-.5)-(y_-.5))*sqtwo)
transY = sympy.lambdify((x_,y_),((x_-.5)+(y_-.5))*sqtwo)

def process_patch(patch):
    gc = tuple([mathstuffs.gaussian_curvature(p) for p in patch[0]])
    gc = tuple([sympy.lambdify((u,v),c) for c in gc])
    # Patch is a sympy equation
    map = []
    for xval in np.arange(0,1, 1/RESOLUTION):
        for yval in np.arange(0,1,1/RESOLUTION):
            p = (transX(xval,yval),transY(xval,yval))
            i = ((3,2),(0,1))[p[0]>0][p[1]>0]
            map.append(gc[i](abs(p[0]),abs(p[1])))
    return map

def normalize(patch, magnitude):
    pnew = []
    for p in patch:
        value = (128 * p / magnitude) + 128
        # Decide on HSV mapping here
        color = (int(max(0, (value*2) - 256)),
                 int(256 - abs((value*2) - 256)),
                 int(abs(min(0, (value*2 - 256)))))
        pnew.append(color)

    return pnew

def colorize(curvatures):
    # First find min and max values
    min_val = -.01
    max_val = .01

    for p in curvatures:
        n = min(p)
        x = max(p)
        if n < min_val:
            min_val = n
        if x > max_val:
            max_val = x

    magnitude = (-1*min_val, max_val)[max_val - min_val > 0]

    colors = []
    for p in curvatures:
        colors.append(normalize(p, magnitude))

    return colors

def make_image(patches, filename):
    curvatures = []
    for i,p in enumerate(patches):
        sys.stdout.write("\r%d verticies done out of %d"%(i,len(patches)))
        curvatures.append(process_patch(p))
    print('\nDone calculating, now making heatmap')

    colors = colorize(curvatures)

    # make one big image for the gauss map. There's buffer for overlap.
    im = Image.new("RGB", (RESOLUTION, (RESOLUTION)*len(patches)))
    imdata = []
    for l in colors:
        imdata += l
    im.putdata(imdata)
    im.save(filename)
    


def test():
    # strings are iterable. this should totally work.
    make_image("uuu", "test.png")

if __name__ == "__main__":
    test()
