
from pyglet.gl import *

from miru import effects
from miru.test import unittest


class EffectTest(unittest.TestCase):


    def testBlendClassAttributes(self):
        Blend = effects.Blend

        self.assertEquals(GL_ZERO, Blend.ZERO)
        self.assertEquals(GL_ONE, Blend.ONE)
        self.assertEquals(GL_SRC_COLOR, Blend.SRC_COLOR)
        self.assertEquals(GL_ONE_MINUS_SRC_COLOR, Blend.ONE_MINUS_SRC_COLOR)
        self.assertEquals(GL_DST_COLOR, Blend.DST_COLOR)
        self.assertEquals(GL_ONE_MINUS_DST_COLOR, Blend.ONE_MINUS_DST_COLOR)
        self.assertEquals(GL_SRC_ALPHA, Blend.SRC_ALPHA)
        self.assertEquals(GL_ONE_MINUS_SRC_ALPHA, Blend.ONE_MINUS_SRC_ALPHA)
        self.assertEquals(GL_DST_ALPHA, Blend.DST_ALPHA)
        self.assertEquals(GL_ONE_MINUS_DST_ALPHA, Blend.ONE_MINUS_DST_ALPHA)
        self.assertEquals(GL_CONSTANT_COLOR, Blend.CONSTANT_COLOR)
        self.assertEquals(GL_CONSTANT_ALPHA, Blend.CONSTANT_ALPHA)
        self.assertEquals(GL_ONE_MINUS_CONSTANT_ALPHA, Blend.ONE_MINUS_CONSTANT_ALPHA)
        self.assertEquals(GL_SRC_ALPHA_SATURATE, Blend.SRC_ALPHA_SATURATE)

        
