from miru.test import unittest, require_window
from miru import camera
from miru import imiru
from miru import components
from miru import core

require_window()

class LightGroupTest(unittest.TestCase):

    def testWithinLightsLimit(self):
        lightGroup = camera.LightGroup()

        # add up to N supported lights
        for i in range(camera.LIGHT_CT_MAX):
            lightGroup.append(camera.DirectionalLight())
        # Ok ..

    def testExceedingLightsLimit(self):
        def overload():
            lightGroup = camera.LightGroup()
            for i in range(camera.LIGHT_CT_MAX + 1):
                lightGroup.append(camera.DirectionalLight())

        self.failUnlessRaises(AssertionError, overload)


    def testLimitOff(self):

        lightGroup = camera.LightGroup(enforce_limit=False)
        for i in range(camera.LIGHT_CT_MAX + 10):
            lightGroup.append(camera.DirectionalLight())

class BlittableViewTest(unittest.TestCase):

    def testZOrdering(self):
        bv = components.getUtility(imiru.IBlittableRenderStage)
        o1 = core.Object(pos=(0,0,1))
        o2 = core.Object(pos=(0,0,-1))
        o3 = core.Object(pos=(0,0,0))
        bv.addobj(o1)
        bv.addobj(o2)
        bv.addobj(o3)
        self.assertEquals([o2,o3,o1],bv.objects)
        o1.pos -= (0,0,3)
        self.assertEquals([o1,o2,o3],bv.objects)
        o2.pos += (0,0,5)
        self.assertEquals([o1,o3,o2],bv.objects)



class TestProjection(camera.BaseProjection):

    def on_resize(self, width, height):
        pass

class CamerasTest(unittest.TestCase):

    def testMetaCameraProjection(self):

        orthoProj = camera.OrthographicProjection()
        perspProj = camera.PerspectiveProjection()
        camA = camera.Camera(projection=orthoProj)
        camB = camera.Camera(projection=perspProj)
        metaCamera = camera.MetaCamera(camA, camB)

        self.assert_(isinstance(metaCamera.projection, camera._MetaProjection))
        self.assertEquals(orthoProj, camA.projection)
        self.assertEquals(perspProj, camB.projection)


    def testMetaCameraLights(self):
        camA = camera.Camera(lights=1)
        camB = camera.Camera(lights=2)
        metaCamera = camera.MetaCamera(camA, camB)

        self.assertEquals(1, metaCamera.lights)
        self.assertEquals(1, camA.lights)
        self.assertEquals(2, camB.lights)

        metaCamera.lights = 3
        self.assertEquals(3, camA.lights)
        self.assertEquals(3, camB.lights)
        self.assertEquals(3, metaCamera.lights)



