from pyglet import options
options['debug_gl'] = 0
options['vsync'] = 0

import pyglet.gl as gl
import pyglet.graphics
import pyglet.clock

import miru
from miru.ext import geom
context = miru.context

import euclid
import ctypes

window = miru.ui.Window(600,400, clear_color=(0,0,.5,1))
context.window = window
context.osd.add_object(pyglet.clock.ClockDisplay())
context.control = miru.input.SimpleMouseControl()
context.camera.lights = miru.camera.LightGroup([
    miru.camera.DirectionalLight()])
context.camera.pos.z = 5
context.camera.angle.x = -25


# First create a CellShader to use for batching our geometrical primitives
cell_shader = miru.graphics.CellShader()
# Build a color table and use this to create a new texture object
color_table = cell_shader.create_color_table((0.,0.7,0.))
texobj = cell_shader.create_texobject( color_table )

# Next we create a Torus which we'll batch into the cell shader
# and attach under the default group for the texture object we
# generated above
torus = geom.Torus(divisions=48)
data = [ ('v3f', torus.vertices),
         ('n3f', torus.normals) ]
cell_shader.add_vlist(
        torus.vertex_count,
        torus.drawing_mode,
        data, texobj, indices=torus.indices)

# Next we wrap the batch in an object we can move in the scene 
obj = miru.core.Object(cell_shader.batch)
obj.angle.z = 15
context.add_object( obj )

# Finally we need to schedule the update method on our cell
# shader which updates the texture coordinates during runtime
pyglet.clock.schedule_interval_soft( cell_shader.update, 1/60.)


def pfps(dt):
    print pyglet.clock.get_fps()
pyglet.clock.schedule_interval(pfps, 3)

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    context.render()
    window.flip()
window.close()
