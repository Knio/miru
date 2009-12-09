"""
Demo loading a Cube and assigning a texture.
"""
from pyglet.graphics import Batch
from pyglet import clock
from pyglet.image import load as load_image
from pyglet import app

from miru.core import Object
from miru.context import context
from miru.ext.geom import Cube, get_vlist
from miru.ui import Window
from miru.graphics import TextureBindGroup
from miru.camera import LightGroup, DirectionalLight
from miru.input import SimpleMouseControl

window = Window(800, 450)
context.window = window
context.osd.add_object(clock.ClockDisplay())
context.control = SimpleMouseControl()
context.camera.lights = LightGroup([
   DirectionalLight([1.0, 0.0, 1.0])])
tex = load_image('docs/demo/test.png').get_texture()

batch = Batch()
texture_group = TextureBindGroup(tex)
cube_geom = Cube()
get_vlist(cube_geom, batch, texture_group)

cube = Object(batch)
cube.angle.z = 15
context.add_object(cube)

v = 35
def update(dt):
    dy = dt * v
    cube.angle.x += dy

clock.schedule_interval(update, 1/60.)

@window.event
def on_draw():
    window.clear()
    context.render()

app.run()

