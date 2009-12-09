# -*- test-case-name: miru.test.test_effects -*-
# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
"""Effects that can be added to objects in ICamera.render.
"""

#
# Some notes:
#
# basic bledning equation:
#     C_f = (C_5 * S) + (C_d * D)
#     C_f is the final computed color 
#     C_s is the source color
#     C_d it the destination color
#     S source blending factor
#     D destination blending factor
#
# Blending factor can be set with gl.glBlendFunc(S::gl.GLenum, D:gl.GLenum)


from pyglet import gl

from miru.imiru import IEffect
from miru.context import context
import miru.camera

from zope.interface import implements

import copy

class Blend:
    _ls = locals()
    for n in ('GL_ZERO', 'GL_ONE', 'GL_SRC_COLOR', 'GL_ONE_MINUS_SRC_COLOR',
              'GL_DST_COLOR', 'GL_ONE_MINUS_DST_COLOR', 'GL_SRC_ALPHA',
              'GL_ONE_MINUS_SRC_ALPHA', 'GL_DST_ALPHA',
              'GL_ONE_MINUS_DST_ALPHA', 'GL_CONSTANT_COLOR',
              'GL_CONSTANT_ALPHA', 'GL_ONE_MINUS_CONSTANT_ALPHA','GL_SRC_ALPHA_SATURATE'):
        _ls['_'.join(n.split('_')[1:])] = getattr(gl, n)
    del _ls

    blendEffect = ZERO

class Reflection:
    """Simulate reflection of objects on a surface.  Currently the surface
    must be coplanar with the (X,Z) plane and Y=1.  In the future, we should
    support arbitrary positioning and orientation of the ground surface.

    N.B.:

    * The reflected lights will not mirror changes in global lights if they
    change position etc. during runtime. 
    
    * Global lighting should be set before creating Reflection instances.

    >>> from zope.interface.verify import verifyClass, verifyObject
    >>> verifyClass(IEffect, Reflection)
    True
    >>> verifyObject(IEffect, Reflection(lights=[]))
    True
    """
    implements(IEffect)
    objects = []

    def __init__(self, objects=None, ground=None, lights=None, camera=None):
        assert ground
        self.objects = objects
        self.camera = camera
        if not self.camera:
            self.camera = context.camera
        if not self.objects:
            self.objects = self.camera.objects
        
        ls = lights
        if ls is None:
            ls = context.camera.lights
        self.lights = miru.camera.LightGroup()
        for l in ls:
            self.lights.append(l.clone())
            l2 = self.lights[-1]
            p = (l2.pos.x, -l2.pos.y, l2.pos.z)
            l2.pos = tuple(p)
        self.ground = ground

    def _before_visible(self):
        gl.glScalef(1,-1,1)

    def enable(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT | gl.GL_STENCIL_BUFFER_BIT)


        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glColorMask(gl.GL_FALSE, gl.GL_FALSE, gl.GL_FALSE, gl.GL_FALSE)

        gl.glEnable(gl.GL_STENCIL_TEST)
        gl.glStencilOp(gl.GL_REPLACE, gl.GL_REPLACE, gl.GL_REPLACE)
        gl.glStencilFunc(gl.GL_ALWAYS, 1, 0xffffffff)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(Blend.SRC_ALPHA, Blend.ONE_MINUS_SRC_ALPHA)
        self.ground.draw()

        gl.glColorMask(gl.GL_TRUE, gl.GL_TRUE, gl.GL_TRUE, gl.GL_TRUE)
        gl.glEnable(gl.GL_DEPTH_TEST)

        gl.glStencilFunc(gl.GL_EQUAL, 1, 0xffffffff)
        gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_KEEP)

        gl.glPushMatrix()
        gl.glCullFace(gl.GL_FRONT)
        gl.glEnable(gl.GL_NORMALIZE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(Blend.SRC_ALPHA, Blend.ONE_MINUS_SRC_ALPHA)
        self.camera.render(lights=self.lights, effect_pass=1, before_render=self._before_visible)
        gl.glDisable(gl.GL_NORMALIZE)
        gl.glCullFace(gl.GL_BACK)
        gl.glPopMatrix()

        gl.glDisable(gl.GL_STENCIL_TEST)
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(Blend.SRC_ALPHA, Blend.ONE_MINUS_SRC_ALPHA)
        self.ground.draw()
        #gl.glDisable(gl.GL_BLEND)


    def disable(self):
        pass


class Fog(object):
    """
    >>> from zope.interface.verify import verifyObject, verifyClass
    >>> verifyClass(IEffect, Fog)
    True
    >>> verifyObject(IEffect, Fog())
    True
    """
    implements(IEffect)

    HINT_NICEST = gl.GL_NICEST
    HINT_FASTEST = gl.GL_FASTEST
    EQ_LINEAR = gl.GL_LINEAR
    EQ_EXP = gl.GL_EXP
    EQ_EXP2 = gl.GL_EXP2

    def __init__(self, color=(0.9,0.9,0.9,1), start=3.0, end=20.0,
            equation=gl.GL_LINEAR, density=1.0, hint=None):
        self.color = color
        self.start = start
        self.end = end
        self.equation = equation
        self.density = density
        self.hint = hint

    def enable(self):
        gl.glEnable(gl.GL_FOG)
        gl.glFogfv(gl.GL_FOG_COLOR, self.color)
        gl.glFogf(gl.GL_FOG_START, self.start)
        gl.glFogf(gl.GL_FOG_END, self.end)
        if self.density is not None:
            gl.glFogf(gl.GL_FOG_DENSITY, self.density)
        if self.hint is not None:
            gl.glHint(gl.GL_FOG_HINT, self.hint)
        gl.glFogi(gl.GL_FOG_MODE, self.equation)

    def disable(self):
        pass
        #gl.glDisable(gl.GL_FOG)

    def _getcolor(self):
        return self._color
    def _setcolor(self, color):
        self._color = (4 * gl.GLfloat)()
        self._color[:] = color
    color = property(_getcolor, _setcolor)


