# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details
from euclid import Vector3

#from miru import core
from miru import core
from miru import imiru
from miru.test import unittest

from zope.interface import implements
import random

class TestPositionalThing(core.PositionalMixin):
    pass

class PositionMixinTest(unittest.TestCase):

    def test_gettingAndSetting(self):
        thing = TestPositionalThing()
        thing.pos = Vector3(1,2,3)
        thing.angle = Vector3(4,5,6)
        self.assertEquals(Vector3(1,2,3), thing.pos)
        self.assertEquals(Vector3(4,5,6), thing.angle)

        thing.pos += (1,2,3)
        self.assertEquals(Vector3(2,4,6), thing.pos)
        thing.angle += (-1,-2,-3)
        self.assertEquals(Vector3(3,3,3), thing.angle)

    def test_isub(self):
        thing = TestPositionalThing()
        thing.pos = (1,2,3)
        thing.pos -= (1,3,4)
        self.assertEquals((0,-1,-1), tuple(thing.pos))
    
    def test_isubBug(self):
        thing = TestPositionalThing()
        thing.pos = (1,2,3)
        thing.pos += (1,1,1)
        self.assertEquals((2,3,4), tuple(thing.pos))
        thing.pos -= (1,1,1)
        self.assertEquals((1,2,3), tuple(thing.pos))
    
    def test_imul(self):
        thing = TestPositionalThing()
        thing.angle = (1,2,3)
        thing.angle *= 3
        self.assertEquals((3,6,9), tuple(thing.angle))
    

    def test_init(self):
        thing = TestPositionalThing(pos=Vector3(5,6,7), angle=Vector3(4,3,2))
        self.assertEquals(Vector3(5,6,7), thing.pos)
        self.assertEquals(Vector3(4,3,2), thing.angle)

  
    def test_stupidBug(self):
        thing = TestPositionalThing()
        thing.pos = (1,2,3)
        thing.pos += (1,1,1)
        thing.pos = (1,2,3)
        self.assertEquals(Vector3(1,2,3), thing.pos)

    def test_listeners(self):
        called_pos = []
        called_angle = []

        def pos_cb(obj, pos, displ):
            called_pos.append((obj, pos, displ))

        def angle_cb(obj, angle, displ):
            called_angle.append((obj, angle, displ))

        thing = TestPositionalThing(pos_listeners=[pos_cb])
        thing.pos = (1,2,3)
        thing.pos += (1,1,2)
        self.assertEquals([(thing,Vector3(1,2,3),Vector3(1,2,3)),
                           (thing,Vector3(2,3,5),Vector3(1,1,2))], called_pos)

        self.assertEquals([], called_angle)

        thing.angle_listeners.append(angle_cb)
        called_pos = []
        thing.pos += (0,0,1)
        thing.angle = Vector3(5,4,3)

        self.assertEquals([(thing,Vector3(2,3,6),Vector3(0,0,1))], called_pos)
        self.assertEquals([(thing,Vector3(5,4,3),Vector3(5,4,3))], called_angle)

        thing.pos = (1,2,3)
        self.assertEquals((1,2,3), tuple(thing.pos))
        called_pos = []
        thing.pos *= 2
        self.assertEquals((2,4,6), tuple(thing.pos))
        self.assertEquals([(thing,Vector3(2,4,6),Vector3(1,2,3))], called_pos)


    def test_listenersXYZ(self):
        called_pos = []
        called_angle = []

        def pos_cb(obj, pos, displ):
            called_pos.append((obj, pos, displ))

        def angle_cb(obj, angle, displ):
            called_angle.append((obj, angle, displ))

        thing = TestPositionalThing(pos_listeners=[pos_cb])
        thing.pos.x = 1
        thing.pos.x += 1
        self.assertEquals([(thing,Vector3(1,0,0),Vector3(1,0,0)),
                           (thing,Vector3(2,0,0),Vector3(1,0,0))], called_pos)

        self.assertEquals([], called_angle)

        thing.angle_listeners.append(angle_cb)
        called_pos = []
        thing.pos.y += 1
        thing.angle.z = 3
        thing.angle.z += 1
        thing.angle.z -= 1

        self.assertEquals([(thing,Vector3(2,1,0),Vector3(0,1,0))], called_pos)
        self.assertEquals([
            (thing,Vector3(0,0,3),Vector3(0,0,3)),
            (thing,Vector3(0,0,4),Vector3(0,0,1)),
            (thing,Vector3(0,0,3),Vector3(0,0,-1))
            ], called_angle)

        thing.pos = (2,0,0)
        self.assertEquals((2,0,0), tuple(thing.pos))
        called_pos = []
        thing.pos.x *= 3
        self.assertEquals((6,0,0), tuple(thing.pos))
        self.assertEquals([(thing,Vector3(6,0,0),Vector3(4,0,0))], called_pos)


    def test_noTracking(self):
        thing = TestPositionalThing()
        self.assertNot(thing.pos.__class__ == Vector3)
        self.assertNot(thing.angle.__class__ == Vector3)

        thing = TestPositionalThing(trackable=False)
        self.assertEquals(thing.pos.__class__, Vector3)
        self.assertEquals(thing.angle.__class__, Vector3)
    test_noTracking.todo = "Should be useful for performance reasons"

class Thingy(core.PositionalMixin):
    pass

class InXRangeConstraint:
    implements(imiru.IConstraint)

    def __init__(self, minx, maxx):
        self.minx = minx
        self.maxx = maxx

    def constrain(self, pos):
        if pos.x  > self.maxx:
            pos.x = self.maxx
        elif pos.x < self.minx:
            pos.x = self.minx
        return pos

class ConstraintTest(unittest.TestCase):

    def testPosConstraint(self):
        o = Thingy(pos_constraints=[InXRangeConstraint(-3,3)])
        o.pos += (4,1,0)
        self.assertEquals((3,1,0), tuple(o.pos))
        o.pos -= (0,5,0)
        self.assertEquals((3,-4,0), tuple(o.pos))
        o.pos -= (6,0,0)
        self.assertEquals((-3,-4,0), tuple(o.pos))
        o.pos -= (1,0,0)
        self.assertEquals((-3,-4,0), tuple(o.pos))
        o.pos += (1,0,0)
        self.assertEquals((-2,-4,0), tuple(o.pos))
    
    def testAngleConstraint(self):
        o = Thingy(angle_constraints=[InXRangeConstraint(-3,3)])
        o.angle += (4,1,0)
        self.assertEquals((3,1,0), tuple(o.angle))
        o.angle -= (0,5,0)
        self.assertEquals((3,-4,0), tuple(o.angle))
        o.angle -= (6,0,0)
        self.assertEquals((-3,-4,0), tuple(o.angle))
        o.angle -= (1,0,0)
        self.assertEquals((-3,-4,0), tuple(o.angle))
        o.angle += (1,0,0)
        self.assertEquals((-2,-4,0), tuple(o.angle))


from miru import components
from zope.interface import Interface

class IFoo(Interface):
    pass

class IHosed(Interface):
    pass

class Foo:
    implements(IFoo)
foo = Foo()

class Bar:
    implements(IFoo)
bar = Bar()

class Hosed:
    implements(IHosed)
hosed = Hosed()

class UilityTest(unittest.TestCase):

    def tearDown(self):
        components.destroyUtility(IFoo)
        components.destroyUtility(IHosed)

    def testRegistration(self):
        components.registerUtility(IFoo, foo)
        self.assertEquals(foo, components.getUtility(IFoo))
    
    def testRegistrationMultiple(self):
        components.registerUtility(IFoo, foo)
        components.registerUtility(IHosed, hosed)
        self.assertEquals(foo, components.getUtility(IFoo))
        self.assertEquals(hosed, components.getUtility(IHosed))

    def testRegisterOnceConstraint(self):
        components.registerUtility(IFoo, foo)
        def explode():
            components.registerUtility(IFoo, foo)
        self.assertRaises(components.AlreadyRegistered, explode)

    def testOverriding(self):
        components.registerUtility(IFoo, foo)
        components.registerUtility(IFoo, bar, override=True)
        self.assertEquals(bar, components.getUtility(IFoo))


