from pyglet import options
options['debug_gl'] = 1
#options['debug_gl_trace'] = 0
#options['debug_gl_trace_args'] = 0
#options['debug_graphics_batch'] = 1
#options['debug_graphics_batch_quiet'] = 1
options['vsync'] = 0

import pyglet.gl as gl
import pyglet.graphics
import pyglet.clock

import miru
from miru.ext import geom

context = miru.context

import euclid
import ctypes

window = miru.ui.BaseWindow(600,400, clear_color=(0.4,0.4,.4,1))
context.window = window
context.osd.add_object( pyglet.clock.ClockDisplay() )
context.control = miru.input.SimpleMouseControl()
context.camera.lights = miru.camera.LightGroup([])
context.camera.pos.z = 9
context.camera.angle.x = 0

gl.glDisable( gl.GL_LIGHTING )
#gl.glCullFace( gl.GL_FRONT )
#gl.glPolygonMode( gl.GL_BACK, gl.GL_LINE )

# First create a CellShader to use for batching our geometrical primitives
cell_shader = miru.graphics.CellShader()
# Build a some color shaders and use these bind new textures:
texobjs = []
for color in [(0.7,0.,0), (0.0,0.7,0.0), (0.0,0,0.7), (0.7,0.7,0.0)]:
    color_table = cell_shader.create_color_table(color)
    texobjs.append( cell_shader.create_texobject( color_table ) )

# Next we create some Tori which we'll batch into the cell shader
# and attach under the default group for the texture object we
# generated above
tori = []
for (idx, pos) in enumerate( [(-2.5,-2,0),(-2.5,2,0),(2.5,2,0),(2.5,-2,0)] ):
    torus = geom.Torus(divisions=27)
    tori.append( miru.core.Object(torus) )
    tori[-1].pos = pos
    tori[-1].angle.x = 45
    group = miru.core.ObjectGroup(
            tori[-1], parent=miru.graphics.TextureBindGroup(
                texobjs[idx],
                gl.GL_TEXTURE_1D,
                miru.graphics.tex_enable_group_1D))
    data = [ ('v3f', torus.vertices),
             ('n3f', torus.normals) ]
    cell_shader.add_vlist(
            torus.vertex_count,
            torus.drawing_mode,
            data, texobjs[idx], indices=torus.indices, group=group )

obj = miru.core.Object(cell_shader.batch)
context.add_object( obj )

# Finally we need to schedule the update method on our cell
# shader which updates the texture coordinates during runtime
pyglet.clock.schedule_interval_soft( cell_shader.update, 1/60. )

camera_velocity = 15
def update_camera(dt):
    d = dt * camera_velocity
    context.camera.angle.y += d
pyglet.clock.schedule_interval(update_camera, 1/60.)

def pfps(dt):
    print pyglet.clock.get_fps()
pyglet.clock.schedule_interval(pfps, 3)

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    context.render()
    window.flip()

