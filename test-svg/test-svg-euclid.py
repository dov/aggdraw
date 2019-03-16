# This is a test bed for testing the svg extension. It should
# probably not be part of the final workspace.
#
# This example makes use of github.com/dov/pyeuclid
# 
# Dov Grobgeld <dov.grobgeld@gmail.com>
# 2019-03-16 Sat

from __future__ import print_function
import sys
sys.path.insert(0, '../build/lib.linux-x86_64-3.6/')
import math
import euclid
import aggdraw
from aggdraw import Draw,Brush,Svg
from PIL import Image

def euclid2agg(t):
    '''Extract the euclid affine coordinates in the proper order for agg'''
    return (t[0],t[1],t[3],t[4],t[6],t[7])

im = Image.new("RGB", (1024, 1024))
draw = Draw(im)
brush = Brush('#44c')
draw.rectangle((0, 0, im.size[0], im.size[1]), brush)

svg = Svg(open('tux.svg').read())
br = svg.bounding_rect()
center = euclid.Point2(0.5*(br[0]+br[2]),0.5*(br[1]+br[3]))
brush = Brush('red')
draw.svg((500-center[0],500-center[1]),svg)
s = 0.3
for i in range(16):
    angle = math.radians(360./16*i)
    t = (euclid.Matrix3.new_identity()
        .scale(s,s)
        .rotate_around(angle, center[0], center[1])
        .translate(0, -1300)
        .pre_translate(-center[0]*s+500, -center[1]*s+500)
        )
    draw.svg(euclid2agg(t),svg)
draw.flush()
im.save('tuxes.png')

print('ok')

