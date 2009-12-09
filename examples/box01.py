from pyglet import options
options['debug_gl'] = 0

import pyglet.gl as gl
import pyglet.graphics

import miru.graphics
import miru.ui
import miru.core
import miru.input
import miru.ext.geom

from miru.context import context


window = miru.ui.BaseWindow(600,400)
context.window = window
context.control = miru.input.SimpleMouseControl()
context.camera.lights = miru.camera.LightGroup([
    miru.camera.PositionalLight(
        pos=(0,1,-1),
        diffuse=(1,1,1,1),
        ambient=(1,1,1,1), kq=0.15)])
#    miru.camera.PositionalLight(pos=(0,1,0))])
context.camera.pos = ( 0., -0.9, 5.0 )
context.camera.angle.x = 7

gl.glEnable( gl.GL_CULL_FACE )

box = miru.ext.geom.Box()
batch = pyglet.graphics.Batch()
greengroup = miru.graphics.ColorGroup((0.6,0.9,0.6))
miru.ext.geom.get_vlist(box, batch, greengroup)

cube = miru.ext.geom.Cube()
miru.ext.geom.transform(cube, (0,-1.5,-1))
redgroup = miru.graphics.ColorGroup((0.9,0.3,0.3))
miru.ext.geom.get_vlist(cube, batch, redgroup)


#torus = miru.ext.geom.Torus()
#miru.ext.geom.transform(torus, (0,1,0))
cube2 = miru.ext.geom.Cube(1)
miru.ext.geom.transform(cube2, (-1, -2, 1))
yellowgroup = miru.graphics.ColorGroup((0.8,0.8,0.3))
miru.ext.geom.get_vlist(cube2, batch, yellowgroup)


obj = miru.core.Object(batch)
context.add_object(obj)

#v = 20
#def update(dt):
#    d  = dt * v
#    context.camera.angle.y += d
#pyglet.clock.schedule_interval(update, 1/60.)

while not window.has_exit:
    window.clear()
    pyglet.clock.tick()
    window.dispatch_events()
    context.render()
    window.flip()


