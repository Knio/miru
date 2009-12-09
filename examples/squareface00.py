from pyglet import options
options['debug_gl'] = 0
#options['debug_gl_trace'] = 1
#options['debug_gl_trace_args'] = 1
options['vsync'] = 0

import pyglet.graphics
import pyglet.clock

import miru
from miru.context import context
from miru.ext import geom

skin_1 = r'/var/forge/workingcopies/sister/bzr/pymgen_3d_experiments/examples/python-powered-w-200x80.png'
#skin_1 = r'/var/forge/workingcopies/sister/bzr/pymgen_3d_experiments/examples/6.jpg'
#skin_1 = r'/var/forge/testbed/text_tex.png'

window = miru.ui.Window(720,480)
context.window = window
context.osd.add_object(pyglet.clock.ClockDisplay())
context.control = miru.input.SimpleMouseControl()
context.camera.lights = miru.camera.LightGroup([
   miru.camera.DirectionalLight(pos=[1.0,1.0,0.5])])
context.camera.pos.z = 15
#context.camera.angle.x = -15
img = pyglet.image.load(skin_1)
tex = img.get_texture(rectangle=True, force_rectangle=True)

batch = pyglet.graphics.Batch()
shape = geom.Square(width=16, height=9, depth=0, tex=tex)
#shape = geom.Square(width=480, height=270, depth=0, tex=tex)

group = miru.graphics.TextureBindGroup(tex, tex.target, parent=None, gencoords=False)

vlist = geom.get_vlist(shape, batch, group)

shape_obj = miru.core.Object(batch)
#shape_obj.angle.z = 15
context.add_object(shape_obj)

v = 35
def update(dt):
    dy = dt * v
    shape_obj.angle.y += dy
pyglet.clock.schedule_interval(update, 1/60.)

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    #pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)
    #Need blending enabled for cull face to work
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    context.render()
    #shape_obj.draw()
    window.flip()

