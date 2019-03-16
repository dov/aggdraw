# This is a test bed for testing the svg extension. It should
# probably not be part of the final workspace.
#
# Dov Grobgeld <dov.grobgeld@gmail.com>
# 2019-03-16 Sat

from __future__ import print_function
import sys
import math

sys.path.insert(0, '../build/lib.linux-x86_64-3.6/')
from aggdraw import Draw,Brush,Svg
from PIL import Image

im = Image.new("RGB", (1024, 1024))
draw = Draw(im)
brush = Brush('#44c')
draw.rectangle((0, 0, im.size[0], im.size[1]), brush)

svg = Svg(open('tux.svg').read())
br = svg.bounding_rect()
center = (0.5*(br[0]+br[2]),0.5*(br[1]+br[3]))
draw.svg((500-center[0],500-center[1]),svg)
draw.flush()
im.save('tux.png')

print('ok')

