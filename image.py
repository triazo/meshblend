import sympy
from PIL import Image
import sys
import importlib

import mathstuffs
importlib.reload(mathstuffs)

RESOLUTION = 8

u,v = sympy.symbols("u v", real=True)

# To make more
x = 0.0
# ==========TODO==========
def process_patch(patch):
    gc = mathstuffs.gaussian_curvature(patch[0])
    gc = sympy.lambdify((u,v),gc)
    # Patch is a sympy equation
    map = []
    for uval in range(-1, RESOLUTION+1):
        for vval in range(-1, RESOLUTION+1):
            map.append(gc(uval,vval))
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
    im = Image.new("RGB", (RESOLUTION+2, (RESOLUTION+2)*len(patches)))
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
