"""
An example of updating texture coordinate data on
pyglet's VertexList.
"""

from collections import deque

from pyglet.graphics import Batch
from pyglet.image import load as load_image
from pyglet import clock
from pyglet import app

from miru.core import Object
from miru.input import SimpleMouseControl
from miru.ui import Window
from miru.context import context
from miru.ext.geom import Cube, get_vlist
from miru.graphics import TextureBindGroup
from miru.camera import LightGroup, DirectionalLight

window = Window(800,450)
context.window = window
context.osd.add_object(clock.ClockDisplay())
context.control = SimpleMouseControl()
context.camera.lights = LightGroup([
   DirectionalLight(pos=[1.0,1.0,0.5])])
tex = load_image('docs/demo/cross.png').get_texture()

batch = Batch()
texture_group = TextureBindGroup(tex)

cube_geom = Cube()
cube_geom.texcoord_data = [
    0.245, 0.505, 0.245, 0.745, 0.005, 0.746, 0.005, 0.505, # left 
    0.495, 0.755, 0.495, 0.995, 0.255, 0.995, 0.255, 0.755, # back 
    0.745, 0.505, 0.745, 0.745, 0.505, 0.745, 0.505, 0.505, # right
    0.255, 0.745, 0.255, 0.505, 0.495, 0.505, 0.495, 0.745, # top
    0.255, 0.245, 0.255, 0.005, 0.495, 0.005, 0.495, 0.245, # bottom
    0.255, 0.495, 0.255, 0.255, 0.495, 0.255, 0.495, 0.495 ] # front
vlist = get_vlist(cube_geom, batch, texture_group)
slider = deque(vlist.tex_coords)

cube = Object(batch)
context.add_object(cube)
cube.angle.z = 35

v = 35
def update(dt):
    dy = dt * v
    cube.angle.x += dy
clock.schedule_interval(update, 1/60.)

def update_texcoords(dt):
    slider.rotate(8)
    vlist.tex_coords[:] = list(slider)
clock.schedule_interval(update_texcoords, 0.25)

@window.event
def on_draw():
    window.clear()
    context.render()

app.run()

