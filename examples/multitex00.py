from pyglet import options
options['debug_gl'] = False
options['vsync'] = True

from pyglet.gl import *
import pyglet.gl as gl
import pyglet.graphics
import pyglet.image
from pyglet import clock

import miru.graphics
from miru.context import context
import miru.ui
import miru.input
from miru import core

import ctypes
import os
import sys

window = miru.ui.BaseWindow(600, 400)
context.window = window
context.control = miru.input.SimpleMouseControl()
context.osd.add_object(clock.ClockDisplay())
#glEnable(GL_CULL_FACE)

class MultiTextureGroup(pyglet.graphics.Group):
    v = GLint()
    glGetIntegerv(GL_MAX_TEXTURE_UNITS, v)
    max_texture_units = v.value
    del v

    def __init__(self, unit_ids, parent=None):

        parent = parent or miru.graphics._tex_enable_group
        super(MultiTextureGroup, self).__init__(parent=parent)

        self.unit_ids = list(unit_ids)
        self.unit_ids.sort()

        tmp = list(unit_ids)
        tmp.reverse()
        for unit_id in tmp:
            if (unit_id - GL_TEXTURE0) <= self.max_texture_units:
                break
            import warnings
            warnings.warn('Texture unit out of supported range : ' + unit_id)
            self.unit_ids.pop()


    def set_state(self):
        # This hard coded for testing
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE1)
        glColor3f(1, 1, 1)
        
    #def unset_state(self):
    #    glActiveTexture(GL_TEXTURE0)


cubemap = miru.graphics.Cubemap([
    os.path.join('docs', 'demo', 'cm-%s.png' % sfx) for sfx in (
        'left', 'forward', 'up', 'down', 'right', 'back'
        )
    ])

img = pyglet.image.load(
        os.path.join('docs', 'demo', 'tarnish.png'))
tarnish_tex = miru.graphics.get_wrapped_texture(img)

################################################
# Now the fun bit - setting up the texture units
################################################
glActiveTexture(GL_TEXTURE0)
glEnable(GL_TEXTURE_2D)
glBindTexture(GL_TEXTURE_2D, tarnish_tex.id)
glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL) # decal the tarnish

# Second texture unit contains the cube map
glActiveTexture(GL_TEXTURE1)
glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap.texture_id )
glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP)
glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP)
glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_REFLECTION_MAP)
glEnable(GL_TEXTURE_CUBE_MAP)

# Multiply this texture by the one underneath
glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)



batch1 = pyglet.graphics.Batch()

class SkyBox:
    
    def draw(self):

        extent = 15

        glActiveTexture(GL_TEXTURE0)
        glDisable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE1)
        #glEnable(GL_TEXTURE_CUBE_MAP)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, -1.0, 1.0)
        glVertex3f(-extent, -extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, -1.0, -1.0)
        glVertex3f(-extent, -extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, 1.0, -1.0)
        glVertex3f(-extent, extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, 1.0, 1.0)
        glVertex3f(-extent, extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, -1.0, -1.0)
        glVertex3f(extent, -extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, -1.0, 1.0)
        glVertex3f(extent, -extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, 1.0, 1.0)
        glVertex3f(extent, extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, 1.0, -1.0)
        glVertex3f(extent, extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, -1.0, -1.0)
        glVertex3f(-extent, -extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, -1.0, -1.0)
        glVertex3f(extent, -extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, 1.0, -1.0)
        glVertex3f(extent, extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, 1.0, -1.0)
        glVertex3f(-extent, extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, -1.0, 1.0)
        glVertex3f(extent, -extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, -1.0, 1.0)
        glVertex3f(-extent, -extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, 1.0, 1.0)
        glVertex3f(-extent, extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, 1.0, 1.0)
        glVertex3f(extent, extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, 1.0, 1.0)
        glVertex3f(-extent, extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, 1.0, -1.0)
        glVertex3f(-extent, extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, 1.0, -1.0)
        glVertex3f(extent, extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, 1.0, 1.0)
        glVertex3f(extent, extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, -1.0, -1.0)
        glVertex3f(-extent, -extent, -extent)
        glMultiTexCoord3f(GL_TEXTURE1, -1.0, -1.0, 1.0)
        glVertex3f(-extent, -extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, -1.0, 1.0)
        glVertex3f(extent, -extent, extent)
        glMultiTexCoord3f(GL_TEXTURE1, 1.0, -1.0, -1.0)
        glVertex3f(extent, -extent, -extent)


multi_tex_group = MultiTextureGroup(
        [ GL_TEXTURE0, GL_TEXTURE1 ],
        parent=miru.graphics.GenCoordTextureGroup())


batch2 = pyglet.graphics.Batch()
mesh_id = miru.graphics.load_mesh(
        (sys.argv[1:] and sys.argv[1]
            or os.path.join('docs', 'demo', 'yam.obj')))
miru.graphics.batch_mesh(
        mesh_id, batch2, multi_tex_group, False)

obj = core.Object(SkyBox())
context.add_object(obj)
obj = core.Object(batch2)
context.add_object(obj)

velocity = 20
def update(dt):
    delta = dt * velocity
    obj.angle.y += delta
clock.schedule_interval(update, 1/60.)

while not window.has_exit:
    clock.tick()
    window.clear()
    window.dispatch_events()
    context.render()
    window.flip()
window.close()

